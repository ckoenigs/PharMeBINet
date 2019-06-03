
from py2neo import Graph, authenticate
import datetime
import MySQLdb as mdb
import csv
import sys


# dictionary with mondo_id as key and class DiseaseHetionet as value
dict_diseases_hetionet = {}

# dictionary with code as key and value is class DiseaseNDF_RT
dict_diseases_NDF_RT = {}

# dictionary umls cui to mondo id
dict_umls_cui_to_mondo_id={}

# dictionary with name/synonyms to mondo id
dict_name_synonym_to_mondo_id = {}

# list with all names and synonyms of disease ontology
list_name_synonyms = []

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # authenticate("localhost:7474", "neo4j", "test")
    # global g
    # g = Graph("http://localhost:7474/db/data/")


    # create connection to server
    authenticate("bimi:7475", "ckoenigs", "test")
    global g
    g = Graph("http://bimi:7475/db/data/", bolt=False)

    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'root', 'dadmin17', 'umls',  charset="utf8")
    # con = mdb.connect('localhost', 'root', 'Za8p7Tf', 'umls', charset="utf8")
#

# boolean to check if the umls cuis in hetionet are right
check_umls_cuis = True

# dictionary from umls sab to mondo sab
dict_sab_umls_to_mondo_sab={
   'MSH':'MESH',
    'SNOMEDCT_US':'SNOMEDCT_US_2016_03_01'

}

'''
check if umls and hetionet disease has for the same cui the same xref
'''
def generate_umls_list_with_umls_query_and_xrefs(dict_xrefs, query, print_string):
    updated_cui_list=[]
    cur = con.cursor()
    rows_counter = cur.execute(query)
    if rows_counter > 0:
        for cui, sab, code, in cur:
            if sab in dict_xrefs or (
                    sab in dict_sab_umls_to_mondo_sab and dict_sab_umls_to_mondo_sab[sab] in dict_xrefs):
                if sab in dict_xrefs:
                    if code in dict_xrefs[sab]:
                        print(print_string)
                        updated_cui_list.append(cui)
                        break
                else:
                    if code in dict_xrefs[dict_sab_umls_to_mondo_sab[sab]]:
                        print(print_string)
                        updated_cui_list.append(cui)
                        break
    return updated_cui_list

'''
function to check if the umls cui with the name is the same and return only where cui and name fitts or when the xrefs are fitting
else search for umls cui with name
'''

def check_umls_cui_and_name_in_umls(list_umls_cuis, name, synonyms, xrefs):
    name=name.lower()
    updated_cui_list=[]
    synonyms=[x.lower().split(' exact')[0] for x in synonyms]
    synonyms.append(name)
    string_synonyms='","'.join(synonyms)
    dict_xrefs={}
    for xref in xrefs:
        if ':' in xref:
            split_xref=xref.split(':')
            if not split_xref[0] in dict_xrefs:
                dict_xrefs[split_xref[0]]=[split_xref[1]]
            else:
                dict_xrefs[split_xref[0]].append(split_xref[1])
        else:
            print(xref)

    # string_synonyms=string_synonyms.encode('utf-8')
    for cui in list_umls_cuis:
        cur = con.cursor()
        query = ('SELECT str FROM MRCONSO WHERE cui="%s" and lower(STR) in ("%s") ; ') % (cui,string_synonyms)
        query.encode('utf-8')
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            updated_cui_list.append(cui)

    if len(updated_cui_list)==0:
        for cui in list_umls_cuis:
            query = ('Select CUI,SAB, CODE From MRCONSO Where cui="%s" ;') % (cui)
            updated_cui_list=generate_umls_list_with_umls_query_and_xrefs(dict_xrefs, query, 'found xref mapping')


    if len(updated_cui_list)==0:
        query = ('Select Distinct CUI, SAB, CODE From MRCONSO Where lower(STR)="%s" ;') % ( name)
        updated_cui_list=generate_umls_list_with_umls_query_and_xrefs(dict_xrefs, query, 'name with xref mapping')

    return updated_cui_list


'''
load in all diseases from hetionet in a dictionary in a dictionary and  generate dictionary and list with all names and synonyms
'''


def load_hetionet_diseases_in():
    query = '''MATCH (n:Disease) RETURN n'''
    results = g.run(query)

    for disease_node, in results:

        identifier=disease_node['identifier']
        name=disease_node['name']
        synonyms=disease_node['synonyms'] if 'synonyms' in disease_node else []
        xrefs=disease_node['xrefs']
        umls_cuis=disease_node['umls_cuis']
        if ':' in umls_cuis[0]:
            umls_cuis = [x.split(':')[1] for x in umls_cuis]
            if check_umls_cuis and umls_cuis[0]!='' and  not len(umls_cuis)> 1:
                new_umls_cuis=check_umls_cui_and_name_in_umls(umls_cuis,name,synonyms, xrefs)
                if len(new_umls_cuis)==0:
                    print(identifier)
                    print(name.encode('utf-8'))
                    print(umls_cuis)
                    print('all cuis away')
            umls_cuis_string = '","'.join(list(set(umls_cuis)))
            query = '''MATCH (n:Disease{identifier:'%s'}) Set n.umls_cuis=["%s"]''' % (identifier, umls_cuis_string)
            g.run(query)
        else:
            if check_umls_cuis and umls_cuis[0]!='' and  not len(umls_cuis)> 1:

                print(identifier)
                new_umls_cuis = check_umls_cui_and_name_in_umls(umls_cuis, name, synonyms,xrefs)

                print(new_umls_cuis)
                if len(new_umls_cuis) == 0:
                    print(identifier)
                    print(name.encode('utf-8'))
                    print(umls_cuis)
                    print('all cuis away')
        umls_cuis=set(umls_cuis)
        resource=disease_node['resource']
        for umls_cui in umls_cuis:
            if len(umls_cui) > 0:
                if not umls_cui in dict_umls_cui_to_mondo_id:
                    dict_umls_cui_to_mondo_id[umls_cui]=[identifier]
                else:
                    other_node=dict_diseases_hetionet[dict_umls_cui_to_mondo_id[umls_cui][0]]
                    other_synonyms=other_node['synonyms'] if 'synonyms' in other_node else []
                    other_synonyms=[x.lower() for x in other_synonyms]
                    found_similar_names=False
                    if name.lower() in other_synonyms or name.lower()== other_node['name'].lower():
                        found_similar_names=True
                    else:
                        for synonym in synonyms:
                            if synonym.lower() in other_synonyms or synonym.lower()== other_node['name'].lower():
                                found_similar_names=True
                    if not found_similar_names:
                        print(umls_cui)
                        print(dict_umls_cui_to_mondo_id[umls_cui])
                        print(identifier)
                        print('double cui')
                    else:
                        dict_umls_cui_to_mondo_id[umls_cui].append(identifier)

        if not name.lower() in dict_name_synonym_to_mondo_id:
            dict_name_synonym_to_mondo_id[name.lower()] = [identifier]
        else:
            dict_name_synonym_to_mondo_id[name.lower()].append(identifier)
        for synonym in synonyms:
            synonym = synonym.split(':')[0].lower()
            synonym=synonym.split(' exact')[0]
            if not synonym in dict_name_synonym_to_mondo_id:
                dict_name_synonym_to_mondo_id[synonym] = [identifier]
            else:
                dict_name_synonym_to_mondo_id[synonym].append(identifier)
        dict_diseases_hetionet[identifier] = dict(disease_node)
    print('length of disease in hetionet:' + str(len(dict_diseases_hetionet)))

# dictionary of umls cui to side effect
dict_umls_cui_to_se={}

'''
load in all diseases from hetionet in a dictionary in a dictionary and  generate dictionary and list with all names and synonyms
'''

def load_hetionet_side_effects_in():
    query = '''MATCH (n:SideEffect) RETURN n '''
    results = g.run(query)
    for node, in results:
        identifier=node['identifier']
        dict_umls_cui_to_se[identifier]=dict(node)



#dictionary from mesh to ndf-rt code
dict_mesh_to_ndf_rt_code={}

#dictionary from snomed to ndfrt code
dict_snomed_to_ndfrt={}

'''
load in all diseases from ndf-rt in a dictionary and get all umls cuis

MeSH_CUI
SNOMED_CID
'''


def load_ndf_rt_diseases_in():
    query = '''MATCH (n:NDF_RT_disease) RETURN n'''
    results = g.run(query)
    i = 0
    for result, in results:
        code = result['code']
        properties = result['properties']
        name = result['name'].lower()
        properties = properties.split(',')
        umls_cuis = []
        for prop in properties:
            if prop[0:8] == 'UMLS_CUI':
                cui = prop
                umls_cuis.append(cui.split(':')[1])
            elif prop =='MeSH_CUI':
                mesh_cui=prop.split(':')[1]
                if mesh_cui in dict_mesh_to_ndf_rt_code:
                    print('ohje mesh')
                else:
                    dict_mesh_to_ndf_rt_code[mesh_cui]=code
            elif prop == 'SNOMED_CID':
                snomed = prop.split(':')[1]
                if snomed in dict_snomed_to_ndfrt:
                    print('ohje snomed')
                else:
                    dict_snomed_to_ndfrt[snomed]=code
        result=dict(result)
        result['umls_cui']=umls_cuis
        dict_diseases_NDF_RT[code] = result

        i += 1
    print('length of disease in ndf-rt:' + str(len(dict_diseases_NDF_RT)))


# dictionary with code as key and value is a list of mondo ids
dict_mapped = {}
# dictionary with code as key and value is a list of umls cuis of se
dict_mapped_to_se = {}
# list of codes which are not mapped to disease ontology ids
list_code_not_mapped = []

# files for the how_mapped
map_direct_cui_cui = open('disease/ndf_rt_disease_cui_cui_map.tsv', 'w')
map_direct_cui_cui.write('code in NDF-RT \t name in NDF-RT \t MONDO ids with | as seperator  \n')

map_direct_cui_cui_se = open('disease/ndf_rt_disease_cui_cui_map_se.tsv', 'w')
map_direct_cui_cui_se.write('code in NDF-RT \t name in NDF-RT \t umls cuis with | as seperator  \n')

map_direct_name = open('disease/ndf_rt_disease_name_name_synonym_map.tsv', 'w')
map_direct_name.write('code in NDF-RT \t name in NDF-RT \t MONDO ids with | as seperator  \n')

map_synonym_cuis = open('disease/ndf_rt_disease_synonyms_map.tsv', 'w')
map_synonym_cuis.write('code in NDF-RT \t name in NDF-RT \t MONDO ids with | as seperator  \n')

'''
first round of map:
go through all diseases from ndf-rt and check if the umls cuis  are in the dictionary of the umls cui to mondo
'''


def map_with_cuis_go_through_all():
    for code, disease_ndf_rt in dict_diseases_NDF_RT.items():
        umls_cuis=disease_ndf_rt['umls_cui']
        umls_cuis = set(umls_cuis)
        mapped_cuis_to_side_effects=[]
        found_a_mapping=False
        for umls_cui in umls_cuis:
            if umls_cui in dict_umls_cui_to_mondo_id:
                if not code in dict_mapped:
                    found_a_mapping=True
                    dict_mapped[code] = [dict_umls_cui_to_mondo_id[umls_cui],'direct map of cuis from ndf-rt and hetionet']


                else:
                    dict_mapped[code][0].extend(dict_umls_cui_to_mondo_id[umls_cui])
            else:
                if umls_cui in dict_umls_cui_to_se:
                    mapped_cuis_to_side_effects.append(umls_cui)
        if not found_a_mapping:
            if len(mapped_cuis_to_side_effects)==0:
                list_code_not_mapped.append(code)
            else:
                dict_mapped_to_se[code]=mapped_cuis_to_side_effects
                list_code_not_mapped.append(code)

    print('number of mapped:' + str(len(dict_mapped)))
    print('number of mapped to se:'+str(len(dict_mapped_to_se)))
    for code, [mondo_ids,how_mapped] in dict_mapped.items():
        string_mondo_ids = '|'.join(mondo_ids)
        map_direct_cui_cui.write(code + '\t' + dict_diseases_NDF_RT[code]['name'] + '\t' + string_mondo_ids + '\n')

    for code, umls_cuis in dict_mapped_to_se.items():
        string_umls_cuis = '|'.join(umls_cuis)
        map_direct_cui_cui_se.write(code + '\t' + dict_diseases_NDF_RT[code]['name'] + '\t' + string_umls_cuis + '\n')
    print('number of not mapped:' + str(len(list_code_not_mapped)))


'''
map the name of ndf-rt disease to name or synonym of disease ontology
'''


def map_with_name():
    delete_map_code = []
    for code in list_code_not_mapped:
        # the mapping with child do not make sense
        if code=='C31768':
            continue
        name = dict_diseases_NDF_RT[code]['name'].split(' [')[0].lower()
        if name in dict_name_synonym_to_mondo_id:
            dict_diseases_NDF_RT[code]['how_mapped']='direct map with name'
            delete_map_code.append(list_code_not_mapped.index(code))
            if not code in dict_mapped:
                dict_mapped[code] = [dict_name_synonym_to_mondo_id[name], 'map synonyms cuis']
            else:
                dict_mapped[code][0].extend(dict_name_synonym_to_mondo_id[name])

    delete_map_code = list(set(delete_map_code))
    delete_map_code.sort()
    delete_map_code = list(reversed(delete_map_code))
    for index in delete_map_code:
        code = list_code_not_mapped.pop(index)
        string_mondo_ids = '|'.join(dict_mapped[code][0])
        map_direct_name.write(code + '\t' + dict_diseases_NDF_RT[code]['name'] + '\t' + string_mondo_ids + '\n')

    print('number of mapped:' + str(len(dict_mapped)))
    print('number of not mapped:' + str(len(list_code_not_mapped)))



# generate file with code and a list of DO ids and where there are from
multiple_mondo_ids = open('ndf_rt_multiple_mondo_ids.tsv', 'w')
multiple_mondo_ids.write('ndf-rt code \t mondo_ids with | as seperator \t where are it from  \t name\n')

# tsv for integration of the mapping into neo4j
csv_file= open('disease/mapped.tsv', 'w')
csv_writter=csv.writer(csv_file, delimiter='\t')
csv_writter.writerow(['code','mondo','mondo_ids','how_mapped'])

csv_file_se= open('disease/mapped_se.tsv', 'w')
csv_writter_se=csv.writer(csv_file_se, delimiter='\t')
csv_writter_se.writerow(['code','cui','cui_ids'])

'''
this integrate only properties into hetionet for the one that are mapped,
because all data from disease ontology are integrated
all Disease which are not mapped with a ndf-rt disease get the propertie no
'''


def integrate_ndf_rt_disease_into_hetionet():
    cypher_file=open('disease/cypher_file.cypher','w')
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ndf-rt/disease/mapped.tsv" As line FIELDTERMINATOR '\\t' MATCH (n:NDF_RT_disease{code:line.code}), (d:Disease{identifier:line.mondo}) Set n.MONDO_IDs=split(line.mondo_ids,'|'), n.how_mapped=line.how_mapped, d.resource=d.resource+'NDF-RT', d.ndf_rt='yes' Create (d)-[:equal_to_Disease_NDF_RT]->(n);\n'''
    cypher_file.write(query)
    # set every disease where no ndf-rt exist as no
    query='''MATCH (n:Disease) Where Not Exists(n.ndf_rt) Set n.ndf_rt='no';\n'''
    cypher_file.write('begin\n')
    cypher_file.write(query)
    cypher_file.write('commit\n')
    # that every ndf-rt nod has at leas an mondo list to avoid complication
    query='''MATCH (n:NDF_RT_disease) Where Not Exists(n.MONDO_IDs) Set n.MONDO_IDs=[];\n'''
    cypher_file.write('begin\n')
    cypher_file.write(query)
    cypher_file.write('commit')
    for code, [mondo_ids,how_mapped] in dict_mapped.items():
        mondo_ids=list(set(mondo_ids))
        mondo_id_string = "|".join(mondo_ids)
        for mondo_id in mondo_ids:
            csv_writter.writerow([code, mondo_id, mondo_id_string, how_mapped])
        if len(mondo_ids) > 1:
            multiple_mondo_ids.write(
                code + '\t' + mondo_id_string + '\t' + how_mapped + '\t' + dict_diseases_NDF_RT[code]['name'] + '\n')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ndf-rt/disease/mapped_se.tsv" As line FIELDTERMINATOR '\\t' MATCH (n:NDF_RT_disease{code:line.code}), (d:SideEffect{identifier:line.cui}) Set n.mapped_cuis=split(line.cui_ids,'|'), d.resource=d.resource+'NDF-RT', d.ndf_rt='yes' Create (d)-[:equal_to_Disease_NDF_RT_SE]->(n);\n'''
    cypher_file.write(query)
    # set every disease where no ndf-rt exist as no
    query = '''MATCH (n:SideEffect) Where Not Exists(n.ndf_rt) Set n.ndf_rt='no';\n'''
    cypher_file.write('begin\n')
    cypher_file.write(query)
    cypher_file.write('commit\n')
    # that every ndf-rt nod has at leas an mondo list to avoid complication
    query = '''MATCH (n:NDF_RT_disease) Where Not Exists(n.mapped_cuis) Set n.mapped_cuis=[];\n'''
    cypher_file.write('begin\n')
    cypher_file.write(query)
    cypher_file.write('commit')

    not_mapped=open('disease/not_mapped.csv','w')
    not_mapped.write('code\tname\n')
    counter_not_mapped=0
    for code in list_code_not_mapped:
        # all ndf-rt disease which are not mapped to mondo but mapped to a se will generate another csv file
        if code in dict_mapped_to_se:
            umls_cuis=dict_mapped_to_se[code]
            string_umls_cuis='|'.join(umls_cuis)
            for umls_cui in umls_cuis:
                csv_writter_se.writerow([code, umls_cui, string_umls_cuis])
        else:
            counter_not_mapped+=1
            not_mapped.write(code+'\t'+dict_diseases_NDF_RT[code]['name']+'\n')

    print('number of nodes which are not to disease or se:'+str(counter_not_mapped))




def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in diseases from hetionet')

    load_hetionet_diseases_in()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in side effects from hetionet')

    load_hetionet_side_effects_in()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in diseases from ndf-rt')

    load_ndf_rt_diseases_in()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map round one, check the cuis from disease ontology to cuis in ndf-rt')

    map_with_cuis_go_through_all()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('map with name ndf-rt to name or synonym od DO')

    map_with_name()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('search for synonym cuis for ndf-rt diseases which did not mapped')

    # find_synonym_cuis_for_ndf_rt_not_mapped()

    # print(
    # '###########################################################################################################################')
    #
    # print (datetime.datetime.utcnow())
    # print('map round two, check the cuis from disease ontology to synonym cuis in ndf-rt')
    #
    # map_with_synonyms_from_code()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('integrate ndf-rt into hetionet')

    integrate_ndf_rt_disease_into_hetionet()

    print(
    '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
