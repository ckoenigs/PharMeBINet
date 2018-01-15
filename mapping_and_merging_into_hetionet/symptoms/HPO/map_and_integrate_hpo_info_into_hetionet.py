# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 12:14:27 2017

@author: cassandra
"""

from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
import threading

reload(sys)
# set default encoding on utf-8
sys.setdefaultencoding('utf-8')


# class of thread
class diseaseMapThread(threading.Thread):
    def __init__(self, threadID, name, db_disease_id, db_disease_name, db_disease_source):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.db_disease_id = db_disease_id
        self.db_disease_name = db_disease_name
        self.db_disease_source = db_disease_source

    def run(self):
        # print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock.acquire()
        map_hpo_disease_to_doid(self.db_disease_id, self.db_disease_name, self.db_disease_source)
        #      print "Ending " + self.name
        #      print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with the names as key and value is the doid
dict_name_to_doid = {}

# dictionary with umls cui as key and doid list as value
dict_umls_cui_to_doid = {}

# dictionary with omim id as key and doid list as value
dict_omim_to_doid = {}

'''
load all disease from hetionet and remember all name, synonym, umls cui and omim id
'''


def get_all_disease_information_from_hetionet():
    query = ''' Match (d:Disease) Return d.identifier, d.name, d.synonyms, d.xrefs, d.umls_cuis'''
    results = g.run(query)
    for doid, name, synonyms, xrefs, umls_cuis, in results:
        dict_name_to_doid[name.lower()] = doid
        #        synonyms=synonyms.split(',')
        for synonym in synonyms:
            synonym = synonym.split(' EXACT')[0].lower()
            synonym = synonym.split(' RELATED')[0].split(' NOS')[0]
            dict_name_to_doid[synonym] = doid
        for umls_cui in umls_cuis:
            #            print(umls_cui)
            if len(umls_cui) > 0:
                umls_cui = umls_cui.split(':')[1]
                if not umls_cui in dict_umls_cui_to_doid:
                    dict_umls_cui_to_doid[umls_cui] = [doid]
                else:
                    dict_umls_cui_to_doid[umls_cui].append(doid)
        for xref in xrefs:
            if xref[0:4] == 'OMIM':
                omim_id = xref.split(':')[1]
                if not omim_id in dict_omim_to_doid:
                    dict_omim_to_doid[omim_id] = [doid]
                else:
                    dict_omim_to_doid[omim_id].append(doid)

    print('number of name to doid:' + str(len(dict_name_to_doid)))
    print('number of different umls cuis:' + str(len(dict_umls_cui_to_doid)))
    print('number of different omims:' + str(len(dict_omim_to_doid)))


# list of disease ids which are not mapped to doid
list_not_mapped_disease_ids_to_doid = []

# dictionary of already mapped disease to doids
dict_disease_id_to_doids = {}

# files for the different mapping steps of disease
file_decipher_name = open('mapping_files/disease/map_decipher_or_ORPHA_with_name.txt', 'w')
file_decipher_name.write('decipher id \t decipher name \t doid \t db_type \n')

file_decipher_name_umls = open('mapping_files/disease/map_decipher_or_ORPHA_with_name_umls_cui.txt', 'w')
file_decipher_name_umls.write('decipher id \t decipher name \t umls cuis \t doids \t db_type \n')

file_decipher_name_split = open('mapping_files/disease/map_decipher_or_ORPHA_with_name_split.txt', 'w')
file_decipher_name_split.write('decipher id \t decipher name \t doids \t db_type \n')

file_not_map_decipher = open('mapping_files/disease/not_map_decipher_or_ORPHA.txt', 'w')
file_not_map_decipher.write('decipher id \t decipher name \t db_type \n')

file_omim_omim = open('mapping_files/disease/map_omim_with_omim.txt', 'w')
file_omim_omim.write('omim id \t omim name \t doids \n')

file_omim_umls_cui = open('mapping_files/disease/map_omim_with_umls_cui.txt', 'w')
file_omim_umls_cui.write('omim id \t omim name \t umls cuis \t doids \n')

file_omim_name = open('mapping_files/disease/map_omim_with_name.txt', 'w')
file_omim_name.write('omim id \t omim name \t doids \n')

file_not_map_omim = open('mapping_files/disease/not_map_omim.txt', 'w')
file_not_map_omim.write('omim id \t omim name \t doids \n')

file_hpo_has_umls_cui = open('mapping_files/symptom/map_hpo_has_umls_cui.txt', 'w')
file_hpo_has_umls_cui.write('hpo id \t hpo name \t umls cui \n')

file_hpo_map_name_to_umls_cui = open('mapping_files/symptom/map_hpo_name_to_umls_cui.txt', 'w')
file_hpo_map_name_to_umls_cui.write('hpo id \t hpo name \t umls cui \n')

file_not_map_hpo = open('mapping_files/symptom/not_map_hpo.txt', 'w')
file_not_map_hpo.write('hpo id \t hpo name \n')

# counter for decipher and orphanet diseases
counter_decipher_orphanet = 0
# counter for omim diseases
counter_omim = 0
# counter for not mapped decipher and orphanet diseases to doid
counter_decipher_orphanet_not_mapped = 0
# counter of mapped with name decipher and orphanet diseases
counter_decipher_orphanet_map_with_name = 0
# counter of mapped with splitted name decipher and orphanet diseases
counter_decipher_orphanet_map_with_name_split = 0
# counter of mapped with umls cui decipher and orphanet diseases
counter_decipher_orphanet_map_with_mapped_umls_cui = 0
# counter of not mapped omim disease
counter_omim_not_mapped = 0
# counter of mapped omim disease with omim
counter_omim_map_with_omim = 0
# counter of mapped omim diseases with umls cui
counter_omim_map_with_umls_cui = 0
# counter of mapped omim diseases with name
counter_omim_with_name = 0
# counter
counter = 0

'''
load all disease information from neo4j in and only remember the relationships where the disease 
can be mapped to DOID with use of UMLS and DO.

'''


def map_hpo_disease_to_doid(db_disease_id, db_disease_name, db_disease_source):
    global counter_decipher_orphanet, counter_omim, counter_decipher_orphanet_not_mapped
    global counter_decipher_orphanet_map_with_name, counter_decipher_orphanet_map_with_name_split
    global counter_decipher_orphanet_map_with_mapped_umls_cui, counter_omim_not_mapped, counter_omim_map_with_omim
    global counter_omim_map_with_umls_cui, counter_omim_with_name, counter

    counter += 1
    if counter % 1000 == 0:
        print(datetime.datetime.utcnow())
        print(counter)
        print('number of decipher:' + str(counter_decipher_orphanet))
        print('number of not mapped decipher:' + str(counter_decipher_orphanet_not_mapped))
        print('number of mapped decipher with name:' + str(counter_decipher_orphanet_map_with_name))
        print('number of decipher with mapped umls cui:' + str(counter_decipher_orphanet_map_with_mapped_umls_cui))
        print('number of mapped decipher with name splitted:' + str(counter_decipher_orphanet_map_with_name_split))
        print('number of omim:' + str(counter_omim))
        print('number of not mapped omim:' + str(counter_omim_not_mapped))
        print('number of direct map omim:' + str(counter_omim_map_with_omim))
        print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
        print('number of map omim with name:' + str(counter_omim_with_name))
    # if i == 100:
    #     break
    db_disease_name = db_disease_name.lower()

    # depending of the source of the diseases different mapping step's are used
    if db_disease_source != 'OMIM':
        counter_decipher_orphanet += 1
        #            print('decipher')
        #            print(counter_decipher_orphanet)
        # test if name is directly in dictionary
        if db_disease_name in dict_name_to_doid:
            doid = dict_name_to_doid[db_disease_name]
            counter_decipher_orphanet_map_with_name += 1
            file_decipher_name.write(
                db_disease_id + '\t' + db_disease_name + '\t' + doid + '\t' + db_disease_source + '\n')
            dict_disease_id_to_doids[db_disease_id] = [doid]
        else:
            names = db_disease_name.split(' (')
            has_found_one = False
            doids = []
            if len(names) > 1:
                for name in names:
                    name = name.replace(')', '')
                    more_names = name.split(' / ')
                    for more_name in more_names:
                        if more_name in dict_name_to_doid:
                            doid = dict_name_to_doid[more_name]
                            doids.append(doid)
                            has_found_one = True

            if has_found_one:
                counter_decipher_orphanet_map_with_name_split += 1
                dict_disease_id_to_doids[db_disease_id] = doids
                doids = '|'.join(doids)
                file_decipher_name_split.write(
                    db_disease_id + '\t' + db_disease_name + '\t' + doids + '\t' + db_disease_source + '\n')

            else:
                cur = con.cursor()
                # this takes a lot of time
                query = ('Select CUI From MRCONSO Where lower(STR)="%s";')
                query = query % (db_disease_name)
                rows_counter = cur.execute(query)
                # rows_counter = 0
                found_a_map = False
                doids = []
                cuis = []

                if rows_counter > 0:
                    for (cui,) in cur:
                        if cui in dict_umls_cui_to_doid:
                            if not cui in cuis:
                                cuis.append(cui)
                                for doid in dict_umls_cui_to_doid[cui]:
                                    if not doid in doids:
                                        doids.append(doid)
                                        found_a_map = True
                if found_a_map:
                    counter_decipher_orphanet_map_with_mapped_umls_cui += 1
                    dict_disease_id_to_doids[db_disease_id] = doids
                    doids = '|'.join(doids)
                    cuis = '|'.join(cuis)
                    file_decipher_name_umls.write(
                        db_disease_id + '\t' + db_disease_name + '\t' + cuis + '\t' + doids + '\t' + db_disease_source + '\n')
                else:
                    counter_decipher_orphanet_not_mapped += 1
                    list_not_mapped_disease_ids_to_doid.append(db_disease_id)
                    file_not_map_decipher.write(
                        db_disease_id + '\t' + db_disease_name + '\t' + db_disease_source + '\n')
                    return

    else:
        counter_omim += 1
        #            print('omim')
        # test if omim id is direct in DO

        omim_id=db_disease_id.split(':')[1]
        if omim_id in dict_omim_to_doid:
            counter_omim_map_with_omim += 1
            doids = []
            for doid in dict_omim_to_doid[omim_id]:
                doids.append(doid)
            dict_disease_id_to_doids[db_disease_id] = doids
            doids = '|'.join(doids)
            file_omim_omim.write(db_disease_id + 'erweitern\t' + db_disease_name + '\t' + doids + '\n')

        else:
            # fined mapping with use of umls cuis
            cur = con.cursor()
            query = ('Select CUI From MRCONSO Where SAB="OMIM" and CODE= "%s" and lower(STR)="%s";')
            query = query % (omim_id, db_disease_name)
            rows_counter = cur.execute(query)
            found = False
            if rows_counter > 0:

                doids = []
                cuis = []
                for (cui,) in cur:
                    #                        print(cui)
                    if cui in dict_umls_cui_to_doid:
                        if not cui in cuis:
                            cuis.append(cui)
                            for doid in dict_umls_cui_to_doid[cui]:
                                if not doid in doids:
                                    found = True
                                    doids.append(doid)
            if found:
                counter_omim_map_with_umls_cui += 1
                dict_disease_id_to_doids[db_disease_id] = doids
                doids = '|'.join(doids)
                cuis = '|'.join(cuis)
                file_omim_umls_cui.write(db_disease_id + '\t' + db_disease_name + '\t' + cuis + '\t' + doids + '\n')

            else:
                # last step is name mapping
                if db_disease_name in dict_name_to_doid:
                    counter_omim_with_name += 1
                    doid = dict_name_to_doid[db_disease_name]
                    file_omim_name.write(db_disease_id + '\t' + db_disease_name + '\t' + doid + '\n')
                    dict_disease_id_to_doids[db_disease_id] = [doid]

                else:
                    #                        print('OMIM not mapped:'+db_disease_name)
                    counter_omim_not_mapped += 1
                    list_not_mapped_disease_ids_to_doid.append(db_disease_id)
                    file_not_map_omim.write(db_disease_id + '\t' + db_disease_name + '\n')

    # print('number of decipher:' + str(counter_decipher_orphanet))
    # print('number of not mapped decipher:' + str(counter_decipher_orphanet_not_mapped))
    # print('number of mapped decipher with name:' + str(counter_decipher_orphanet_map_with_name))
    # print('number of decipher with mapped umls cui:' + str(counter_decipher_orphanet_map_with_mapped_umls_cui))
    # print('number of mapped decipher with name splitted:' + str(counter_decipher_orphanet_map_with_name_split))
    # print('number of omim:' + str(counter_omim))
    # print('number of not mapped omim:' + str(counter_omim_not_mapped))
    # print('number of direct map omim:' + str(counter_omim_map_with_omim))
    # print('number of map omim with umls cui:' + str(counter_omim_map_with_umls_cui))
    # print('number of map omim with name:' + str(counter_omim_with_name))


# dictionary with doid as key and hpo ids as value
dict_doid_to_hpo_ids = {}

'''
Integrate mapping connection between disease and HPOdisease and make a dictionary doid to hpo id
'''


def integrate_mapping_of_disease_into_hetionet():
    for hpo_id, doids in dict_disease_id_to_doids.items():
        for doid in doids:
            query = '''Match (n:HPOdisease{id: "%s"}), (d:Disease{identifier:"%s"}) 
                Set d.hpo="yes"
                Create (d)-[:equal_to_hpo_disease]->(n)'''

            query = query % (hpo_id, doid)
            # print(query)
            g.run(query)
            if doid in dict_doid_to_hpo_ids:
                dict_doid_to_hpo_ids[doid].append(hpo_id)
            else:
                dict_doid_to_hpo_ids[doid] = [hpo_id]

    query = '''Match (d:disease{identifier:"%s"}) Where not exists(d.hpo) Set d.hpo="no" '''
    g.run(query)


'''
function to find mesh id for a cui
'''


def cui_to_mesh(cui):
    cur = con.cursor()
    query = ("Select CODE From MRCONSO Where SAB= 'MSH' AND CUI= '%s'")
    query = query % (cui)
    rows_counter = cur.execute(query)
    if rows_counter > 0:
        codes = []
        for code, in cur:
            codes.append(code)

        codes = list(set(codes))
        return codes
    else:
        return []


'''
Map hpo symptomes to umls cui or mesh and generate connection between symptoms and hpo symptoms. Further the 
hpo symptoms get the mapped umls_cui or mesh as property.
'''


def map_hpo_symptoms_and_integrate_into_hetionet():
    #    counter_has_no_xrefs=0
    #    counter_has_no_umls_cuis=0
    # the number of hpo symptoms which are in a relationship, but are not mapped to umls cui
    counter_no_umls_cui = 0
    # counter for the hpo symptoms which are not in hetionet
    counter_new_symptom_in_hetionet = 0
    #  counter for the symptoms which are already in Hetionet
    counter_symptom_from_hetionet = 0

    query = '''MATCH (n:HPOsymptom) RETURN n.id, n.name, n.xref '''
    results = g.run(query)

    for hpo_id, name, xrefs, in results:

        #                    print(dict_all_info)
        name = name.lower()
        umls_cuis = []
        has_at_least_one = False

        # try to find umls cui with external identifier from hpo
        if not xrefs == None:
            for xref in xrefs.split('|'):
                if xref[0:4] == 'UMLS':
                    has_at_least_one = True
                    umls_cuis.append(xref.split(':')[1])
            if has_at_least_one:
                file_hpo_has_umls_cui.write(hpo_id + '\t' + name + '\t' + '|'.join(umls_cuis) + '\n')

                # if no external identifier is a umls cui then search for the name in umls
        if has_at_least_one == False:
            cur = con.cursor()
            query = ('Select CUI From MRCONSO Where  lower(STR)="%s" Limit 1;')
            query = query % (name)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (cui,) in cur:
                    umls_cuis.append(cui)
                file_hpo_map_name_to_umls_cui.write(
                    hpo_id + '\t' + name + '\t' + '|'.join(umls_cuis) + '\n')
            else:

                #                            print('Even know nothing is found ;(')
                #                            print(dict_all_info['id'][0])
                #                            print(name)
                counter_no_umls_cui += 1
                file_not_map_hpo.write(hpo_id + '\t' + name + '\n')
                continue
        no_cui_in_hetinet_symptomes = False
        all_mapped_cuis_mesh_ids = []
        for umls_cui in umls_cuis:
            mesh_cui_ids = cui_to_mesh(umls_cui)
            mesh_cui_ids.append(umls_cui)
            # identifier can be umls cui or mesh id
            query = '''MATCH (n:Symptom) Where n.identifier in ['%s'] RETURN n '''
            #                    print(mesh_cui_ids)
            mesh_cui_string = "','".join(mesh_cui_ids)
            query = query % (mesh_cui_string)
            is_their = g.run(query)
            first_entry = is_their.evaluate()

            if first_entry != None:
                resource = first_entry['resource'] if 'resource' in first_entry else []

                resource.append("Human Phenotype Ontology")
                resource = list(set(resource))
                string_resource = '","'.join(resource)

                counter_symptom_from_hetionet += 1
                mesh_or_cui = first_entry['identifier']
                query = '''MATCH (s:Symptom{identifier:"%s"}) , (n:HPOsymptom{id:"%s"})
                    Set   s.hpo='yes', s.cui="%s", s.hpo_version='1.2', s.hpo_release='2017-10-05', s.resource=["%s"] 
                    Create (s)-[:equal_to_hpo_symptoms]->(n)'''
                query = query % (mesh_or_cui, hpo_id, umls_cui, string_resource)
                g.run(query)
                all_mapped_cuis_mesh_ids.append(mesh_or_cui)
                no_cui_in_hetinet_symptomes = True

        if not no_cui_in_hetinet_symptomes:
            name = name.replace('"', '')
            url_hpo = 'http://compbio.charite.de/hpoweb/showterm?id=' + hpo_id
            counter_new_symptom_in_hetionet += 1
            url = 'http://identifiers.org/umls/' + umls_cuis[0]
            query = ''' Match (n:HPOsymptom{id:"%s"})
                Set n.umls_cui_mesh=["%s"]
                Create (s:Symptom{identifier:"%s",type:'cui',license:'UMLS licence', name:"%s", resource:['Human Phenotype Ontology'], source:'UMLS', url:"%s", hetionet:'no', do:'no', hpo:'yes', hpo_version:'1.2', hpo_release:'2017-10-05', url_HPO:"%s"}) 
                Create (s)-[:equal_to_hpo_symptoms]->(n) '''
            query = query % (hpo_id, umls_cuis[0], umls_cuis[0], name, url, url_hpo)
        else:
            mapped_identifier_string = '","'.join(all_mapped_cuis_mesh_ids)
            query = ''' Match (n:HPOsymptom{id:"%s"})
                Set n.umls_cui_mesh=["%s"] '''
            query = query % (hpo_id, mapped_identifier_string)
        # print(no_cui_in_hetinet_symptomes)
        # print(all_mapped_cuis_mesh_ids)
        g.run(query)

    # all symptoms which are not in hpo get the property hpo='no'
    query = '''MATCH (s:Symptom) Where not exists(s.hpo) Set s.hpo='no' '''
    g.run(query)

    # set for all hpo symptomes which are not mapped the umls_cui_mesh to empty list
    query = '''MATCH (s:HPOsymptom) Where not exists(s.umls_cui_mesh) Set s.umls_cui_mesh=[] '''
    g.run(query)
    #    print('number of hpo with no umle cui:'+str(counter_has_no_umls_cuis))
    #    print('number of hpo with no xrefs:'+str(counter_has_no_xrefs))
    print('number of hpos with no umls cui:' + str(counter_no_umls_cui))
    print('number of new symptoms:' + str(counter_new_symptom_in_hetionet))
    print('number of already existing symptoms:' + str(counter_symptom_from_hetionet))


# list of all new disease-symptom pairs
list_new_disease_symptom_pairs = []

'''
generate cypher file for the disease symptom connections, but only for the pairs where hpo
has a umls cui.
'''


def generate_cypher_file_for_connection():
    i = 1

    # cypher file with all cypher queries for the connection
    cypher_file = open('cypher/connection_symptoms_' + str(i) + '.cypher', 'w')
    cypher_file.write('begin \n')

    i += 1
    # count all cypher queries
    counter_connection = 0

    # number of queries in a commit block
    constrain_number = 20000

    # number of queries in a flie
    creation_max = 500000

    # counter new connection
    count_new_connection = 0

    # counter_update connection
    count_update_connection = 0

    for doid, hpo_disease_ids in dict_doid_to_hpo_ids.items():

        for hpo_disease_id in hpo_disease_ids:
            query = '''MATCH p=(:HPOdisease{id:"%s"})-[r:present]->(b) RETURN r, b.umls_cui_mesh '''
            query = query % (hpo_disease_id)
            results = g.run(query)

            for connection, umls_cui_meshs, in results:
                if len(umls_cui_meshs) > 0:
                    qualifier = connection['qualifier']
                    reference_id = connection['source']
                    evidence_code = connection['efidence_code']
                    frequency_modi = connection['frequency_modifier']

                    for umls_cui_mesh in umls_cui_meshs:

                        if (doid, umls_cui_mesh) in list_new_disease_symptom_pairs:
                            continue
                        query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"}) 
                        Set n.hpo='yes' Return l '''
                        query = query % (doid, umls_cui_mesh)
                        result = g.run(query)
                        first_entry = result.evaluate()
                        url = 'http://compbio.charite.de/hpoweb/showterm?disease=' + reference_id
                        if first_entry == None:
                            query = '''MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"}) 
                            Create (n)-[:PRESENTS_DpS{version:'phenotype_annotation.tab 2017-10-09 10:47',unbiased:'false',source:'%s',qualifier:'%s', efidence_code:'%s', frequency_modifier:'%s',  resource:['HPO'],hetionet:'no',do:'no', hpo:'yes', url:"%s"}]->(s); \n '''
                            count_new_connection += 1
                            query = query % (
                            doid, umls_cui_mesh, reference_id, qualifier, evidence_code, frequency_modi, url)


                        else:
                            resource = first_entry['resource'] if 'resource' in first_entry else []
                            resource.append("Human Phenotype Ontology")
                            resource = list(set(resource))
                            string_resource = '","'.join(resource)
                            query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
                            Set l.hpo='yes', l.version='phenotype_annotation.tab 2017-10-09 10:47', l.source='%s', l.qualifier='%s', l.efidence_code='%s', l.frequency_modifier='%s',l.resource=["%s"], l.url="%s"; \n'''
                            count_update_connection += 1
                            query = query % (
                                doid, umls_cui_mesh, reference_id, qualifier, evidence_code, frequency_modi,
                                string_resource,
                                url)

                        counter_connection += 1
                        cypher_file.write(query)
                        if counter_connection % constrain_number == 0:
                            cypher_file.write('commit \n')
                            if counter_connection % creation_max == 0:
                                cypher_file.close()
                                cypher_file = open('cypher/connection_symptoms_' + str(i) + '.cypher', 'w')
                                cypher_file.write('begin \n')
                                i += 1
                            else:
                                cypher_file.write('begin \n')

    cypher_file.write('commit \n begin \n')
    query = ''' MATCH ()-[l:PRESENTS_DpS]->(s:Symptom) Where not exists(l.hpo) Set l.hpo='no'; \n '''
    cypher_file.write(query)
    cypher_file.write('commit \n begin \n')
    cypher_file.write('Match (n:Disease) Where not exists(n.hpo) Set n.hpo="no"; \n')
    cypher_file.write('commit')

    print('number of new connection:' + str(count_new_connection))
    print('number of update connection:' + str(count_update_connection))
    print(counter_connection)


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in diseases information in dictionaries')

    get_all_disease_information_from_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('map hpo disease to doid')

    # create a lock, is used to synchronized threads
    global threadLock
    threadLock = threading.Lock()

    # all threads
    threads_synonyms = []

    thread_id = 1

    query = ''' Match (d:HPOdisease) Return d.id, d.name, d.source'''
    results = g.run(query)
    for db_disease_id, db_disease_name, db_disease_source, in results:
        # create thread
        thread = diseaseMapThread(thread_id, 'thread_' + str(thread_id), db_disease_id, db_disease_name,
                                  db_disease_source)
        # start thread
        thread.start()
        # add to list
        threads_synonyms.append(thread)
        # increase thread id
        thread_id += 1

    # wait for all threads
    for t in threads_synonyms:
        t.join()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate mapping into hetionet for disease')

    integrate_mapping_of_disease_into_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('map hpo symptoms to mesh or umls cui and integrated them into hetionet')

    map_hpo_symptoms_and_integrate_into_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('put all relationship information into a cypher file')

    generate_cypher_file_for_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
