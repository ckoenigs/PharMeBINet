# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import MySQLdb as mdb
import sys
import datetime
import threading
import types
reload(sys)
sys.setdefaultencoding("utf-8")


# connect with the neo4j database
def database_connection():

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary monarch DO to information: name
dict_monDO_info = {}

# dictionary external ids to monDO id
dict_external_ids_monDO = {}

# dict of xrefs from monDO which has multiple monDO IDs with counter
dict_source_mapped_to_multiple_monDOs = {}

'''
Load MonDO disease in dictionary
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:MonDOdisease) Where not exists(n.replaced_by) or not exists(n.is_obsolete) RETURN n '''
    results = g.run(query)
    for disease, in results:
        monDo_id = disease['id']
        if monDo_id=='MONDO:0007108':
            print('blub')
        xrefs = disease['xref'] if 'xref' in disease else ''
        dict_monDO_info[monDo_id] = dict(disease)
        xrefs = disease['xref'] if 'xref' in disease else ''
        for external_id in xrefs.split('|'):
            external_id = external_id.split(' ')[0]
            if external_id == '':
                continue
            if external_id in dict_external_ids_monDO:
                if external_id.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                    dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] = 1
                else:
                    dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] += 1
                # print(external_id)
                dict_external_ids_monDO[external_id].append(monDo_id)
                # print(dict_external_ids_monDO[external_id])
            else:
                dict_external_ids_monDO[external_id] = [monDo_id]
    print(dict_source_mapped_to_multiple_monDOs)


# dictionary disease ontology to external ids
dict_DO_to_xref = {}

# dictionary do to indormation: name
dict_DO_to_info = {}

'''
Load in all disease ontology ids with external identifier and alternative id
'''


def load_in_all_DO_in_dictionary():
    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for disease, in results:
        Do_id = disease['identifier']
        dict_DO_to_info[Do_id] = dict(disease)
        alternative_id = disease['alternateIds'] if 'alternateIds' in disease else []
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        xrefs = xrefs[0].split(',')
        xrefs.extend(alternative_id)
        dict_DO_to_xref[Do_id] = xrefs

    print('Number of DOIDs:' + str(len(dict_DO_to_xref)))


# dictionary monDO to DOIDs
dict_monDo_to_DO = {}

# dictionary monDO to DOIDs with only doid mapping
dict_monDo_to_DO_only_doid = {}

# dictionary Do to monDos
dict_DO_to_monDOs = {}

# dictionary Do to monDos
dict_DO_to_monDOs_only_DO = {}

# list of not mapped doids
list_of_not_mapped_doids = []

'''
Go through all DOIDs and check if the DOID or the external IDs are in the xrefs-monDO dictionary and generate mapping
'''


def map_DO_to_monDO_with_DO_and_xrefs():
    not_direct_name_matching_file = open('not_direct_name_matching_file.tsv', 'w')
    not_direct_name_matching_file.write('monDO \t DOID \t name monDO \t name DOID \n')
    counter_name_not_matching = 0
    for doid, xrefs in dict_DO_to_xref.items():
        if doid=='DOID:6126':
            print('ok')
        if doid in dict_external_ids_monDO:

            for monDO in dict_external_ids_monDO[doid]:
                monDOname = dict_monDO_info[monDO]['name'].lower().split(' (')[0]
                do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '')
                if monDOname != do_name:
                    counter_name_not_matching += 1
                    not_direct_name_matching_file.write(
                        monDO + '\t' + doid + '\t' + dict_monDO_info[monDO]['name'] + '\t' + dict_DO_to_info[doid][
                            'name'] + '\n')
                    # print(monDO)
                    # print(doid)
                    # print(dict_monDO_info[monDO][0])
                    # print(dict_DO_to_info[doid][0])
                if monDO in dict_monDo_to_DO:
                    dict_monDo_to_DO[monDO].add(doid)
                    if monDO in dict_monDo_to_DO_only_doid:
                        dict_monDo_to_DO_only_doid[monDO].add(doid)
                    else:
                        dict_monDo_to_DO_only_doid[monDO] = set([doid])
                else:
                    dict_monDo_to_DO[monDO] = set([doid])
                    dict_monDo_to_DO_only_doid[monDO] = set([doid])

                if doid in dict_DO_to_monDOs:
                    dict_DO_to_monDOs[doid].add(monDO)
                    dict_DO_to_monDOs_only_DO[doid].add(monDO)
                else:
                    dict_DO_to_monDOs[doid] = set([monDO])
                    dict_DO_to_monDOs_only_DO[doid] = set([monDO])
        else:
            list_of_not_mapped_doids.append(doid)
        for xref in xrefs:
            xref = xref.replace("'", "")
            if xref in dict_external_ids_monDO:
                for monDO in dict_external_ids_monDO[xref]:
                    if monDO in dict_monDo_to_DO:
                        dict_monDo_to_DO[monDO].add(doid)
                    else:
                        dict_monDo_to_DO[monDO] = set([doid])
                    if doid in dict_DO_to_monDOs:
                        # if monDO not in dict_DO_to_monDOs[doid]:
                        # print(xref)
                        dict_DO_to_monDOs[doid].add(monDO)
                    else:
                        dict_DO_to_monDOs[doid] = set([monDO])

    print('number of not name matching mappes:' + str(counter_name_not_matching))
    print('number of mapped doids with only doids:' + str(len(dict_DO_to_monDOs_only_DO)))
    print('number of mapped doids:' + str(len(dict_DO_to_monDOs_only_DO)))

    print('number of mapped monDO with only doids:' + str(len(dict_monDo_to_DO_only_doid)))
    print('number of mapped monDO:' + str(len(dict_monDo_to_DO)))

    counter_more_than_one_monDO_ID = 0

    for doid, mondos in dict_DO_to_monDOs.items():
        if len(mondos) > 1:
            counter_more_than_one_monDO_ID += 1

    print('number of multiple monDO IDs:' + str(counter_more_than_one_monDO_ID))

    print(list_of_not_mapped_doids)

    # generate file with not mapped doids
    file_not_mapped_doids = open('not_mapped_DOIDs.txt', 'w')
    file_not_mapped_doids.write('doid \t name \n')
    for doid in list_of_not_mapped_doids:
        file_not_mapped_doids.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')

    file_not_mapped_doids.close()

    # file for multiple mapped monDO IDs
    file_mondo_to_multiple_doids = open('multiple_doids_for_monDO.tsv', 'w')
    file_mondo_to_multiple_doids.write('monDO\t monDO name\t doids \t doid names\n')
    for monDO, doids in dict_monDo_to_DO_only_doid.items():
        if len(doids) > 1:
            text = monDO + '\t' + dict_monDO_info[monDO]['name'] + '\t' + '|'.join(doids) + '\t'
            for doid in doids:
                text = text + dict_DO_to_info[doid]['name'] + '|'
            file_mondo_to_multiple_doids.write(text[0:-1] + '\n')
            # print(monDO)
            # print(doids)

    # print(dict_DO_to_monDOs)
    print('###################################################################################')
    # print(dict_DO_to_monDOs_only_DO)

    print('###################################################################################')
    # print(dict_monDo_to_DO)


'''
Generate mapping files
'''


def mapping_files():
    for doid, mondos in dict_DO_to_monDOs_only_DO.items():
        f = open('mapping/Do_to_monDO/' + doid + '.txt', 'w')
        f.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')
        f.write('monDO ID \t name \n')
        for mondo in mondos:
            f.write(mondo + '\t' + dict_monDO_info[mondo]['name'] + '\n')
        f.close()

    for monDo, doids in dict_monDo_to_DO.items():
        g = open('mapping/monDO_to_DO/with_xref/' + monDo + '.txt', 'w')
        g.write(monDo + '\t' + dict_monDO_info[monDo]['name'] + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')
        g.close()

    for monDo, doids in dict_monDo_to_DO_only_doid.items():
        g = open('mapping/monDO_to_DO/without_xref/' + monDo + '.txt', 'w')
        g.write(monDo + '\t' + dict_monDO_info[monDo]['name'] + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')
        g.close()


# list of properties which should be an array
list_properties_which_should_be_an_array = ['synonym', 'xref', 'subset', 'relationship', 'intersection_of',
                                            'disjoint_from', 'union_of']

'''
integrate mondo into hetionet and change identifier
'''


def integrate_mondo_change_identifier():
    counter_new_nodes = 0
    counter_switched_nodes = 0
    # file counter
    file_counter = 1
    # maximal number of queries for a commit block
    constrain_number = 20000
    # maximal number of queries in a file
    creation_max_in_file = 1000000

    h = open('integrate_and_transformed_disease' + str(file_counter) + '.cypher', 'w')
    file_counter += 1
    h.write('begin \n')
    #count the number of queries
    counter_connection=0
    for monDo, info in dict_monDO_info.items():
        if monDo in dict_monDo_to_DO_only_doid and len(dict_monDo_to_DO_only_doid[monDo]) == 1:
            counter_switched_nodes += 1

            # get the different information from monDO which will be combined
            doid = list(dict_monDo_to_DO_only_doid[monDo])[0]
            monDO_synonyms = dict_monDO_info[monDo]['synonym'].split('|') if 'synonym' in dict_monDO_info else []
            monDo_def = dict_monDO_info[monDo]['def'] if 'def' in dict_monDO_info else ''
            monDO_xref = dict_monDO_info[monDo]['xref'].split('|') if 'xref' in dict_monDO_info else []

            umls_cuis_monDO = []
            other_xrefs_monDO = []
            for ref in monDO_xref:
                if ref[0:4] == 'UMLS':
                    umls_cuis_monDO.append(ref)
                else:
                    other_xrefs_monDO.append(ref)

            monDO_subset = dict_monDO_info[monDo]['subset'].split('|') if 'subset' in dict_monDO_info else []

            # combined information from monDO and DO
            monDO_synonyms.extend(dict_DO_to_info[doid]['synonyms'])
            dict_monDO_info[monDo]['synonym'] = "|".join(monDO_synonyms)

            dict_monDO_info[monDo]['def'] = dict_DO_to_info[doid]['definition'] + '[FROM DOID]. ' + monDo_def

            dict_DO_to_info[doid]['alternateIds'].append(doid)
            # the alternative id get at least a ''  if their exist no alternative id, that's why they had to be
            # removed from the list
            if dict_DO_to_info[doid]['alternateIds'][0]=='':
                dict_DO_to_info[doid]['alternateIds'].remove('')
            dict_monDO_info[monDo]['doids'] = "|".join(dict_DO_to_info[doid]['alternateIds'])

            other_xrefs_monDO.extend(dict_DO_to_info[doid]['xrefs'])
            dict_monDO_info[monDo]['xref'] = "|".join(other_xrefs_monDO)

            umls_cuis_monDO.extend(dict_DO_to_info[doid]['umls_cuis'])
            dict_monDO_info[monDo]['umls_cuis'] = "|".join(umls_cuis_monDO)

            monDO_subset.extend(dict_DO_to_info[doid]['subset'])
            dict_monDO_info[monDo]['subset'] = "|".join(monDO_subset)

            dict_DO_to_info[doid]['resource'].append('MonDO')
            string_resources= '","'.join(dict_DO_to_info[doid]['resource'])

            query = ''' Match (n:Disease{identifier:"%s"}), (a:MonDOdisease{id:"%s"})
            Create (n)-[:equal_to_monDO]->(a)
            Set n.identifier="%s",'''
            query = query % (doid, monDo, monDo)

            for key, property in dict_monDO_info[monDo].items():
                if key in list_properties_which_should_be_an_array:
                    if key == 'xref':
                        key = 'xrefs'
                    property = property.split('|')
                    property_string = '","'.join(property)
                    add_query= ''' n.%s=["%s"],''' % (key, property_string)
                    query = query + add_query
                else:
                    if key == 'def':
                        key = 'definition'
                    elif key =='id':
                        continue
                    elif key== 'is_a':
                        continue
                    elif key == 'name':
                        continue
                    # query = query + ''' n.%s="%s",'''
                    # query = query % (key, property)
                    add_query = ''' n.%s="%s",''' %(key,property)
                    query = query + add_query


            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            add_query= ''' n.url="%s" , n.resource=["%s"]; \n ''' %(url,string_resources)
            query = query + add_query

        else:
            counter_new_nodes += 1
            query = ''' Match  (a:MonDOdisease{id:"%s"})
                        Create (n:Disease{identifier:"%s", '''
            query = query % (monDo, monDo)
            for key, property in dict_monDO_info[monDo].items():
                if key in list_properties_which_should_be_an_array:
                    if key == 'xref':
                        key = 'xrefs'
                    property = property.split('|')
                    property_string = '","'.join(property)
                    add_query = ''' %s:["%s"],''' % (key, property_string)
                    query = query + add_query
                else:
                    if key == 'def':
                        key = 'definition'
                    elif key =='id':
                        continue
                    elif key== 'is_a':
                        continue
                    add_query = ''' %s:"%s",''' % (key, property)
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            add_query= '''ctd:"no", ndf_rt:"no", resource:['MonDO'], diseaseOntology:"no", hetionet:"no", source:"Monarch Disease Ontology", url:"%s"})
                        Create (n)-[:equal_to_monDO]->(a); \n''' % (url)
            query = query + add_query

        # print(query)
        # sys.exit()
        # g.run(query)
        h.write(query)
        counter_connection+=1
        if counter_connection % constrain_number == 0:
            h.write('commit \n')
            if counter_connection % creation_max_in_file == 0:
                h.close()
                h = open('integrate_and_transformed_disease' + str(file_counter) + '.cypher', 'w')
                h.write('begin \n')
                file_counter += 1
            else:
                h.write('begin \n')
    h.write('commit \n begin \n')
    print('number of new nodes:' + str(counter_new_nodes))
    print('number of switched nodes:' + str(counter_switched_nodes))

    print(datetime.datetime.utcnow())
    counte_new_relationships=0
    counter_already_existing_relationships=0
    
    query = ''' Match (a)-[r:is_a_mondo]->(b) Return a.id, b.id, r.source '''
    results= g.run(query)
    for child_id, parent_id, source, in results:
        if child_id in dict_monDo_to_DO_only_doid and len(dict_monDo_to_DO_only_doid[child_id]) == 1 and parent_id in dict_monDo_to_DO_only_doid and len(dict_monDo_to_DO_only_doid[parent_id]) == 1:
            query = ''' Match (a)-[r:IS_A_DiD]->(b) Where a.identifier="%s" and b.identifier="%s" Return r'''
            query = query % (dict_monDo_to_DO_only_doid[child_id], dict_monDo_to_DO_only_doid[parent_id])
            connections_exist = g.run(query)
            first_connection = connections_exist.evaluate()
            if first_connection == None:
                query =''' Match (a:Disease{identifier:"%s"}), (b:Disease{identifier:"%s"})
                Create (a)-[:IS_A_DiD{license:"CC BY 4.0",unbiased:"false", source:"Monarch Disease Ontology", resource:['MonDO'],  do='no' , mondo='yes', mondo_source="%s"}]->(b)'''
                query = query %(child_id, parent_id, source[1:-1])
                counte_new_relationships+=1
            else:

                query= '''Match (a)-[r:IS_A_DiD]->(b) Where a.identifier="%s" and b.identifier="%s" 
                Set r.resource=["DO","MonDO"], r.do='yes' , r.mondo='yes', r.mondo_source="%s"; \n '''
                query = query % (child_id, parent_id, source[1:-1])
                counter_already_existing_relationships+=1

        else:
            query = ''' Match (a:Disease{identifier:"%s"}), (b:Disease{identifier:"%s"})
                            Create (a)-[:IS_A_DiD{license:"CC BY 4.0",unbiased:"false", source:"Monarch Disease Ontology", resource:['MonDO'],  do='no' , mondo='yes', mondo_source="%s"}]->(b)'''
            query = query % (child_id, parent_id, source[1:-1])
            counte_new_relationships+=1

        h.write(query)
        if counter_connection % constrain_number == 0:
            h.write('commit \n')
            if counter_connection % creation_max_in_file == 0:
                h.close()
                h = open('integrate_and_transformed_disease' + str(file_counter) + '.cypher', 'w')
                h.write('begin \n')
                file_counter += 1
            else:
                h.write('begin \n')

    h.write('commit \n')
    h.close()
    print('number of new relationships:'+str(counter_new_nodes))
    print('number of already existing relationships:'+str(counter_already_existing_relationships))


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in DO diseases ')

    load_in_all_DO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Map DO to monDO ')

    map_DO_to_monDO_with_DO_and_xrefs()

    if 'DOID:6126' in dict_DO_to_monDOs_only_DO:
        print('in it')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate the mapping files ')

    mapping_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate and switch the nodes but ignore the multiple mapped monDO ids ')

    integrate_mondo_change_identifier()


    print('##########################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()
