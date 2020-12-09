# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 11:18:05 2017

@author: cassandra
"""

sys.path.append("../..")
import create_connection_to_databases, authenticate
import MySQLdb as mdb
import sys
import datetime
import threading


# class of thread to find umls cuis for the symptoms
class SymptomThread(threading.Thread):
    def __init__(self, threadID, name, disease_id,  disease_definition):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.disease_id = disease_id
        self.disease_definition = disease_definition

    def run(self):
        # print "Starting " + self.name
        # Get lock to synchronize threads
        threadLock.acquire()
        load_in_hetionet_disease_in_dictionary(self.disease_id,  self.disease_definition)
        #      print "Ending " + self.name
        #      print_time(self.name, self.counter, 3)
        # Free lock to release next thread
        threadLock.release()


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = mdb.connect('127.0.0.1', 'root', 'Za8p7Tf', 'umls')

    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with mondo as key and symptoms terms as list
dict_mondo_to_symptom = {}

# dictionary with symptom term (name) as key and umls cui as value
dict_symptom_to_umls_cui = {}

# list of word to split the symptoms
list_words_to_split = ['in', 'of', 'from', 'on']

# dictionary mondo to name
dict_mondo_to_name={}

'''
split and combined the symptom name and search for this symptom and return if a cui is found or not
'''


def find_cui_for_different_forms_of_string(symptom, split_word):
    symptom = symptom.replace(' the ', ' ')
    split_by_in = symptom.split(' ' + split_word + ' ')
    if len(split_by_in) == 2:
        one_way = split_by_in[0] + ' ' + split_by_in[1]
        another_way = split_by_in[1] + ' ' + split_by_in[0]
        #        cur.close()
        cur = con.cursor()
        query = ('Select CUI From MRCONSO Where  lower(STR)= "%s" or lower(STR)= "%s"  Limit 1;')
        query = query % (one_way, another_way)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            list_cuis = []
            for cui, in cur:
                #                        print(cui)
                list_cuis.append(cui)
            dict_symptom_to_umls_cui[symptom] = list_cuis[0]
            print('good')
            print(symptom + ' ' + list_cuis[0])
            return True
        else:
            return False
    else:
        return False


# counter not mapped symptoms
counter_not_mapped_symptoms = 0

# counter with mapping with change the order of the name
counter_map_with_changed_order = 0

'''
disease in dictionary. Extract symptoms from definition and map symptoms to umls cui
'''


def load_in_hetionet_disease_in_dictionary(mondo,  definition):
    global counter_map_with_changed_order, counter_not_mapped_symptoms

    splitted = definition.split('has_symptom ')
    #        print(splitted)
    list_symptoms = []
    for symptom in splitted[1:]:
        # excluded , and . and all after
        symptom = symptom.split(',')[0].split('.')[0].lower()
        #            print(symptom)
        if symptom[-5:] == ' and ':
            symptom = symptom[0:-5]
        if symptom[-4:] == ' or ':
            symptom = symptom[0:-4]
        list_symptoms.append(symptom)
        if not symptom in dict_symptom_to_umls_cui:
            cur = con.cursor()
            #                query=('Select CUI, count(AUI) From MRCONSO Where  lower(STR)= "%s" Group By CUI Order By count(AUI) DESC;')
            query = ('Select CUI From MRCONSO Where  lower(STR)= "%s" Limit 1;')
            query = query % (symptom)
            rows_counter = cur.execute(query)

            if rows_counter > 0:
                list_cuis = []
                for cui, in cur:
                    #                        print(cui)
                    list_cuis.append(cui)
                dict_symptom_to_umls_cui[symptom] = list_cuis[0]

            else:
                found_a_cui = False
                if symptom.find(' the ') != -1:
                    cur.close()
                    cur = con.cursor()
                    # check if the symptom exist without 'the' in name
                    query = ('Select CUI From MRCONSO Where  lower(STR)= "%s" Limit 1;')
                    query = query % (symptom.replace(' the ', ' '))
                    rows_counter = cur.execute(query)
                    if rows_counter > 0:
                        found_a_cui = True
                        list_cuis = []
                        for cui, in cur:
                            #                        print(cui)
                            list_cuis.append(cui)
                        dict_symptom_to_umls_cui[symptom] = list_cuis[0]
                if not found_a_cui:
                    # if not found  search for the name with exclude preposition and use different orders
                    for split_word in list_words_to_split:
                        if find_cui_for_different_forms_of_string(symptom, split_word):
                            found_a_cui = True
                            counter_map_with_changed_order += 1
                            # sys.exit()
                            # break

                    if found_a_cui == False:
                        counter_not_mapped_symptoms += 1
                        print('ohje')
                        print(symptom)

        dict_mondo_to_symptom[mondo] = list_symptoms


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


# dictionary umls cui to mesh id
dict_cui_to_mesh = {}

# list of all new symptom umls cuis in hetionet
list_new_add_umls_cuis = []

'''
integrated directly the symptoms into Hetionet and for the connection between diseases an symptoms a cypher file is
generated.
also generate file with disease symptoms
Create (s:Symptom{identifier:"%s",type:'cui',license:'UMLS licence', name:"%s", source:'UMLS', url:"%s", hetionet:'no', umls:'yes'}) 
'''


def integrate_information_into_hetionet():
    # count new symptoms
    counter_new_symptoms = 0

    # counter already in hetionet symptoms
    counter_already_in_hetionet_symptoms = 0

    for symptom, cui in dict_symptom_to_umls_cui.items():
        if cui in list_new_add_umls_cuis:
            continue

        mesh_ids = cui_to_mesh(cui)
        query = '''MATCH (n:Symptom) Where n.identifier in ['%s'] RETURN n '''
        #                print(mesh_cui_ids)
        mesh_ids_string = "','".join(mesh_ids)
        query = query % (mesh_ids_string)
        is_their = g.run(query)
        first_entry = is_their.evaluate()

        if first_entry == None:
            #            print(list_new_add_umls_cuis)
            #            print(symptom)
            #            print(cui)
            url = 'http://identifiers.org/umls/' + cui
            query = '''
            Create (s:Symptom{identifier:"%s",type:'cui',license:'UMLS licence', name:"%s", resource:['Disease Ontology'], source:'UMLS', url:"%s", hetionet:'no', do:'yes'});     '''
            query = query % (cui, symptom, url)
            counter_new_symptoms += 1
            list_new_add_umls_cuis.append(cui)

        else:

            mesh = first_entry['identifier']
            query = ''' Match (s:Symptom{identifier:"%s"}) Set s.hetionet='yes', s.cui="%s", s.do='yes', s.resource=["hetionet", "Disease Ontology"] '''
            query = query % (mesh, cui)
            dict_cui_to_mesh[cui] = mesh

            counter_already_in_hetionet_symptoms += 1
        # g.run(query)

    # all symptoms which not appeare in DO get the information
    query = '''Match (s:Symptom) Where not exists(s.do) Set s.hetionet='yes', s.do='no', s.resource=['hetionet'] '''
    g.run(query)

    print('number of new symptoms:' + str(counter_new_symptoms))
    print('number of already in hetionet symptoms:' + str(counter_already_in_hetionet_symptoms))

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    # file counter
    i = 1

    # cypher file with all cypher queries for the connection
    cypher_file = open('cypher/connection_symptoms_' + str(i) + '.cypher', 'w')
    cypher_file.write('begin \n')

    # file with all not mapped symptoms
    not_mapped_file = open('not_mapped_symptoms.txt', 'w')
    not_mapped_file.write('name \n')

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

    for mondo, symptom_terms in dict_mondo_to_symptom.items():
        # generate for every disease which symptoms are mapped and which not
        f = open('Disease_symptoms/' + mondo + '_symptoms.txt', 'w')
        f.write(dict_mondo_to_name[mondo]+'\n')
        f.write('name \t cui \t mesh\n')
        h = open('Disease_symptoms/' + mondo + '_not_mapped.txt', 'w')
        h.write('name \n')
        for symptom_term in symptom_terms:
            if not symptom_term in dict_symptom_to_umls_cui:
                h.write(symptom_term + '\n')
                not_mapped_file.write(symptom_term + '\n')
            else:
                cui = dict_symptom_to_umls_cui[symptom_term]
                if not cui in dict_cui_to_mesh:
                    f.write(symptom_term + '\t' + cui + '\t' + '\n')
                    query = ''' MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"}) 
                    Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'%s',hetionet:'no',do:'yes', resource:['Disease Ontology']}]->(s); \n '''
                    query = query % (mondo, cui, mondo)
                    count_new_connection += 1

                else:
                    mesh_id = dict_cui_to_mesh[cui]
                    query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"}) Return l  '''
                    query = query % (mondo, mesh_id)
                    result = g.run(query)
                    first_entry = result.evaluate()
                    if first_entry == None:
                        query = '''MATCH (n:Disease{identifier:"%s"}),(s:Symptom{identifier:"%s"}) 
                        Create (n)-[:PRESENTS_DpS{license:'CC BY 3.0',unbiased:'false',source:'DO', source_id:'%s', resource:['Disease Ontology'],hetionet:'no',do:'yes'}]->(s); \n '''
                        count_new_connection += 1

                    else:
                        query = '''MATCH (n:Disease{identifier:"%s"})-[l:PRESENTS_DpS]->(s:Symptom{identifier:"%s"})
                        Set l.do='yes', l.hetionet="yes", l.resource=['Disease Ontology','Hetionet'], l.source_id='%s'; \n'''
                        count_update_connection += 1
                    query = query % (mondo, mesh_id, mondo)

                    f.write(symptom_term + '\t' + cui + '\t' + mesh_id + '\n')

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

        h.close()
        f.close()

    cypher_file.write('commit \n begin \n')
    # all disease symptom connection which are not in this get this information.
    query = ''' MATCH ()-[l:PRESENTS_DpS]->(s:Symptom) Where not exists(l.do) Set l.do='no', l.hetionet='yes'; \n '''
    cypher_file.write(query)
    cypher_file.write('commit')

    print(counter_connection)
    print('number of new relationships:' + str(count_new_connection))
    print('number od update connection:' + str(count_update_connection))


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in diseases with symptoms in and find for the symptoms umls cuis')

    # create a lock, is used to synchronized threads
    global threadLock
    threadLock = threading.Lock()

    # all threads
    threads_list = []

    thread_id = 1

    query = '''MATCH (n:Disease) Where n.definition contains 'has_symptom' RETURN n.identifier, n.name ,n.definition '''
    results = g.run(query)
    for mondo, name, definition, in results:
        dict_mondo_to_name[mondo]=name
        # if thread_id>50:
        #     break
        # create thread
        thread = SymptomThread(thread_id, 'thread_' + str(thread_id), mondo,  definition)
        # start thread
        thread.start()
        # add to list
        threads_list.append(thread)
        # increase thread id
        thread_id += 1

        # wait for all threads
    for t in threads_list:
        t.join()


    print('number of mapped symptoms with change the order of the name:' + str(counter_map_with_changed_order))
    print('number of disease which has symptoms in their definition:' + str(len(dict_mondo_to_symptom)))
    print('number of different symptoms which are mapped to umls cui:' + str(len(dict_symptom_to_umls_cui)))
    print('number of not mapped symptoms to umls cuis:' + str(counter_not_mapped_symptoms))

    # sys.exit()
    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate new information into hetionet and cypher files')
    integrate_information_into_hetionet()

    print('##########################################################################')

    print(datetime.datetime.utcnow())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
