
from py2neo import Graph#, authenticate
import MySQLdb as mdb
import sys
import datetime, time
import  csv
from _collections import defaultdict


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('localhost', 'ckoenigs', 'Za8p7Tf$', 'umls')


    global g
    g = Graph("http://localhost:7474/db/data/", auth=("neo4j", "test"))



# csv file for mapping disease
file_symptom_mapped=open('mapping_files/symptom_mapped.tsv','w', encoding='utf-8')
csv_symptom_mapped= csv.writer(file_symptom_mapped,delimiter='\t')
csv_symptom_mapped.writerow(['hpo_id','hetionet_id', 'umls_cuis','mesh_ids','xrefs','resources'])


# cypher file for mapping and integration
cypher_file=open('cypher_symptom.cypher','w')


# csv file for mapping disease
file_symptom_new=open('mapping_files/symptom_new.tsv','w', encoding='utf-8')
csv_symptom_new= csv.writer(file_symptom_new,delimiter='\t')
csv_symptom_new.writerow(['hpo_id','hetionet_id', 'umls_cuis','mesh_ids','xrefs','resources'])

# the general query start
query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%s/master_database_change/mapping_and_merging_into_hetionet/hpo/%s" As line FIELDTERMINATOR '\\t' 
    Match'''


file_hpo_has_umls_cui = open('mapping_files/symptom/map_hpo_has_umls_cui.txt', 'w', encoding='utf-8')
csv_symptoms=csv.writer(file_hpo_has_umls_cui,delimiter='\t')
csv_symptoms.writerow(['hpo id','hpo name','umls cui'])

file_hpo_map_name_to_umls_cui = open('mapping_files/symptom/map_hpo_name_to_umls_cui.txt', 'w', encoding='utf-8')
csv_symptoms_name=csv.writer(file_hpo_map_name_to_umls_cui,delimiter='\t')
csv_symptoms_name.writerow(['hpo id','hpo name','umls cui'])

file_not_map_hpo = open('mapping_files/symptom/not_map_hpo.txt', 'w', encoding='utf-8')
csv_symptoms_not_mapped=csv.writer(file_not_map_hpo,delimiter='\t')
csv_symptoms_not_mapped.writerow(['hpo id','hpo name'])


'''
function to find mesh id for a cui
'''


def cui_to_mesh(cui):
    cur = con.cursor()
    query = ("Select Distinct CODE From MRCONSO Where SAB= 'MSH' AND CUI In ('%s')")
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

## dictionary of symptoms
dict_of_hetionet_symptoms={}

#diction mesh to mapped hpo
dict_mapped_mesh={}

#dictionnary mesh to new hpo
dict_new_mesh_to_hpo={}

#  not mapped hpos files
not_mapped_file=open('not_mapped.csv','w',encoding='utf-8')
csv_not_mapped=csv.writer(file_not_map_hpo,delimiter='\t')
csv_not_mapped.writerow(['hpo_id','name'])


'''
Get al symptoms from hetionet and put this information into a dictionary
'''
def get_all_symptoms_and_add_to_dict():
    query = '''MATCH (n:Symptom) RETURN n  '''
    results=g.run(query)

    #add all symptoms to dictioanry
    for result, in results:
        identifier=result['identifier']
        dict_of_hetionet_symptoms[identifier]=dict(result)


#dictionary with the new mesh ids
dict_new_mesh_ids={}

'''
first search for umls cuis if not in hpo existing check in umls
then map with umls to mesh
check if mesh are in hetionet esle generate new nodes
'''
def symptoms_mapping(name, xrefs, hpo_id):
    global counter_no_umls_cui, counter_symptoms
    global counter_new_symptom_in_hetionet, counter_symptom_from_hetionet
    #                    print(dict_all_info)
    name = name.lower()
    umls_cuis = []
    has_at_least_one = False

    if hpo_id=='HP:0002027':
        print('oj')

    # start = time.time()
    # try to find umls cui with external identifier from hpo
    if xrefs is not None:
        for xref in xrefs:
            if xref[0:4] == 'UMLS':
                has_at_least_one = True
                umls_cuis.append(xref.split(':')[1])
            else:
                print('other xref then umls :O')
                print(xref)
        if has_at_least_one:
            csv_symptoms.writerow([hpo_id, name, '|'.join(umls_cuis)])
    else:
        xrefs=[]
    # print('\t xrefs : %.4f seconds' % (time.time() - start))
    # start = time.time()

    # if no external identifier is a umls cui then search for the name in umls
    if not has_at_least_one:
        cur = con.cursor()
        query = 'SELECT DISTINCT CUI FROM MRCONSO WHERE STR = "%s";' % name
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            for (cui,) in cur:
                umls_cuis.append(cui)
            csv_symptoms_name.writerow([
                hpo_id, name, '|'.join(umls_cuis)])
        else:
            counter_no_umls_cui += 1
            csv_symptoms_not_mapped.writerow([hpo_id, name])
            return
    # print('\t umls : %.4f seconds' % (time.time() - start))
    # start = time.time()

    #
    no_cui_in_hetinet_symptomes = False
    all_mapped_cuis_mesh_ids = []
    # string form of umls cuis
    umls_string = '|'.join(umls_cuis)

    name = name.replace('"', '')
    umls_cuis_string_for_mysql = "','".join(umls_cuis)
    mesh_cui_ids = cui_to_mesh(umls_cuis_string_for_mysql)
    # found one
    found_one = False
    # string form of mesh cuis
    mesh_cuis_string = '|'.join(mesh_cui_ids)
    xrefs.append('HPO:'+hpo_id)

    #check if mesh ids from hpo map to hetionet mesh
    for mesh_id in mesh_cui_ids:
        if mesh_id=='D015423':
            print('huhut')

        if mesh_id in dict_of_hetionet_symptoms:
            found_one = True
            resource=dict_of_hetionet_symptoms[mesh_id]['resource'] if 'resource' in dict_of_hetionet_symptoms[mesh_id] else []
            resource.append('HPO')
            resource=list(set(resource))
            if mesh_id in dict_mapped_mesh:
                dict_mapped_mesh[mesh_id][0].append(hpo_id)
                dict_mapped_mesh[mesh_id][2].append(mesh_cui_ids)
                dict_mapped_mesh[mesh_id][1]=list(set(umls_cuis).union(dict_mapped_mesh[mesh_id][1]))
                dict_mapped_mesh[mesh_id][3] = list(set(umls_cuis).union(dict_mapped_mesh[mesh_id][3]))
            else:
                dict_mapped_mesh[mesh_id]=[[hpo_id],umls_cuis,[mesh_cui_ids],xrefs,resource]


            all_mapped_cuis_mesh_ids.append(mesh_id)
    # print('\t preparation and write into files : %.4f seconds' % (time.time() - start))
    # start = time.time()

    if not found_one:
        name = name.replace('"', '')
        counter_new_symptom_in_hetionet+=1
        dict_hpo_to_mesh_ids[hpo_id]=mesh_cui_ids
        if len(mesh_cui_ids)>0:
            first_mesh= mesh_cui_ids[0]
            if not first_mesh in dict_mapped_mesh:

                dict_mapped_mesh[first_mesh] = [[hpo_id], umls_cuis, [mesh_cui_ids], xrefs, ["HPO"]]
            else:
                found_alternativ_mesh_id=False
                other_mesh=''
                for mesh_id in mesh_cui_ids:
                    if mesh_id not in dict_mapped_mesh:
                        found_alternativ_mesh_id=True
                        other_mesh=mesh_id
                        break
                if found_alternativ_mesh_id:

                    dict_mapped_mesh[other_mesh] = [[hpo_id], umls_cuis, [mesh_cui_ids], xrefs, ["HPO"]]
                else:
                    dict_mapped_mesh[first_mesh][0].append(hpo_id)
                    dict_mapped_mesh[first_mesh][2].append(mesh_cui_ids)
                    dict_mapped_mesh[first_mesh][1]=list(set(umls_cuis).union(dict_mapped_mesh[first_mesh][1]))
                    dict_mapped_mesh[first_mesh][3] = list(set(xrefs).union(dict_mapped_mesh[first_mesh][3]))
        else:
            csv_not_mapped.writerow([hpo_id,"|".join(xrefs)])


    else:
        dict_hpo_to_mesh_ids[hpo_id]=all_mapped_cuis_mesh_ids
        counter_symptom_from_hetionet+=1

        # print('\t not mapped write into file : %.4f seconds' % (time.time() - start))

    if counter_symptoms % 200 == 0:
        print(counter_symptoms)
        print(datetime.datetime.utcnow())

'''
write into a specific file with a given dictionary
'''
def write_into_file(file, dictionary):
    for mesh_id, [hpos,umls_cuis,list_mesh_cuis,xrefs,resource] in dictionary.items():
        umls_string="|".join(umls_cuis)
        xref_string="|".join(xrefs)
        resource_string="|".join(resource)
        for index,hpo_id in enumerate(hpos):
            mesh_cuis_string="|".join(list_mesh_cuis[index])
            file.writerow([hpo_id, mesh_id, umls_string, mesh_cuis_string, xref_string, resource_string])

'''
prepare the csv files from the dictionaries
'''
def prepare_files():
    #first the mapped on
    write_into_file(csv_symptom_mapped,dict_mapped_mesh)

    #the new symptoms
    write_into_file(csv_symptom_new,dict_new_mesh_ids)


# aspect dictionary
dict_aspect={
    'P': 'Phenotypic abnormality',
    'I': 'inheritance',
    'C': 'onset and clinical course'
}

# dictionary of hpo symptoms
dict_hpo_symptoms={}

#dictionary mapping hpo to mesh
dict_hpo_to_mesh_ids={}


'''
Map hpo symptomes to umls cui or mesh and generate connection between symptoms and hpo symptoms. Further the 
hpo symptoms get the mapped umls_cui or mesh as property.
'''


def map_hpo_symptoms_and_integrate_into_hetionet():
    global counter_symptoms, counter_no_umls_cui
    # '','hetionet_id', 'umls_cuis'
    query =query_start+ ''' (s:Symptom{identifier:line.hetionet_id }) , (n:HPOsymptom{id:line.hpo_id}) Set s.hpo='yes', s.umls_cuis=split(line.umls_cuis,"|"), s.xrefs=split(line.xrefs,"|") , s.hpo_version='1.2', s.hpo_release='2019-11-08', s.definition=n.def, s.synonyms=n.synonyms, s.url_HPO="https://hpo.jax.org/app/browse/term/"+line.hpo_id, n.mesh_ids=split(line.mesh_ids,'|') Create (s)-[:equal_to_hpo_symptoms]->(n);\n'''
    query = query %(path_of_directory,'mapping_files/symptom_mapped.tsv')
    cypher_file.write(query)
    # all symptoms which are in hetionet set the resource hpo
    query = '''MATCH (s:Symptom) Where exists(s.hpo) Set s.resource=s.resource+"HPO";\n '''
    cypher_file.write(query)

    query=query_start+'''  (n:HPOsymptom{id:line.hpo_id}) Set n.mesh_ids=split(line.mesh_ids,'|') Create (s:Symptom{identifier:line.hetionet_id, umls_cuis:split(line.umls_cuis,"|") ,source:'MESH',license:'UMLS licence', name:n.name, resource:['HPO'], source:'MESH', url:"http://identifiers.org/mesh/"+line.hetionet_id , xrefs:s.xrefs=split(line.xrefs,"|"), hpo:'yes', hpo_version:'1.2', hpo_release:'2019-11-08', definition:n.def, url_HPO:"https://hpo.jax.org/app/browse/term/"+line.hpo_id})  Create (s)-[:equal_to_hpo_symptoms]->(n);\n '''
    query=query %(path_of_directory,'mapping_files/symptom_new.tsv')
    cypher_file.write(query)
    #    counter_has_no_xrefs=0
    #    counter_has_no_umls_cuis=0
    global counter_no_umls_cui, counter_new_symptom_in_hetionet, counter_symptom_from_hetionet
    # the number of hpo symptoms which are in a relationship, but are not mapped to umls cui
    counter_no_umls_cui = 0
    # counter for the hpo symptoms which are not in hetionet
    counter_new_symptom_in_hetionet = 0
    #  counter for the symptoms which are already in Hetionet
    counter_symptom_from_hetionet = 0


    query = '''MATCH (n:HPOsymptom) RETURN n, n.id, n.name, n.xrefs '''
    results = g.run(query)
    counter_symptoms=0

    for node, hpo_id, name, xrefs, in results:
        counter_symptoms+=1
        dict_hpo_symptoms[hpo_id]=node

        symptoms_mapping(name,xrefs,hpo_id)


    # all symptoms which are not in hpo get the property hpo='no'
    query = '''MATCH (s:Symptom) Where not exists(s.hpo) Set s.hpo='no';\n '''
    cypher_file.write(query)

    #    print('number of hpo with no umle cui:'+str(counter_has_no_umls_cuis))
    #    print('number of hpo with no xrefs:'+str(counter_has_no_xrefs))
    print('number of hpos with no umls cui:' + str(counter_no_umls_cui))
    print('number of new symptoms:' + str(counter_new_symptom_in_hetionet))
    print('number of already existing symptoms:' + str(counter_symptom_from_hetionet))



def main():
    print(datetime.datetime.utcnow())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate dictionary from symptoms of hetionet')


    get_all_symptoms_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('map hpo symptoms to mesh or umls cui and integrated them into hetionet')

    map_hpo_symptoms_and_integrate_into_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()





