import datetime
import MySQLdb as mdb
import sys

sys.path.append("../..")
import create_connection_to_databases


class SideEffectHetionet:
    """
    identifier: string (UMLS cui)
    resource: list
    name: string
    """

    def __init__(self, identifier, name, resource):
        self.identifier = identifier
        self.resource = resource
        self.name = name


class DiseaseCTD:
    """
    idType: string (MESh or OMIM)
    name: string
    altDiseaseIDs: string (MESH oR OMIM or DOID)
    disease_id: sting (identifier)
    cuis: list (UMLS cuis)
    how_mapped: string
    """

    def __init__(self, idType, name, altDiseaseIDs, disease_id):
        self.idType = idType
        self.name = name
        self.altDiseaseIDs = altDiseaseIDs
        self.disease_id = disease_id

    def set_cuis(self, cuis):
        self.cuis = cuis

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all CTD diseases, which has a causes relationship with a drug
# the key is the MESH or OMIM and value is class diseaseCTD
dict_CTD_disease = {}

# dictionary for hetionet side effects with cui as key and value is class SideEffectHetionet
dict_side_effects_hetionet = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    global g
    g = create_connection_to_databases.database_connection_neo4j()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


'''
load all side effects from hetionet in a dictionary
'''


def load_side_effects_from_hetionet_in_dict():
    query = '''MATCH (n:SideEffect) RETURN n '''
    results = g.run(query)

    # go through all results from the neo4j query
    for result, in results:
        sideEffect = SideEffectHetionet(result['identifier'], result['name'], result['resource'])
        dict_side_effects_hetionet[result['identifier']] = sideEffect
    print('size of side effects before the disease ctd is add:' + str(len(dict_side_effects_hetionet)))


'''
load in all ctd disease from neo4j in a dictionary
properties:
    idType
    altDiseaseIDs
    disease_id	
    synonyms
    parentIDs
    name
    parentTreeNumbers
    definition
    tree
    slimMappings
'''


def load_disease_CTD():
    query = ''' MATCH ()-[r:Causes]->(n:CTD_disease) RETURN Distinct n Limit 10 '''
    results = g.run(query)

    # go through all results from the query
    for result, in results:
        idType = result['idType']
        name = result['name']
        altDiseaseIDs = result['altDiseaseIDs']
        disease_id = result['disease_id']
        disease = DiseaseCTD(idType, name, altDiseaseIDs, disease_id)
        dict_CTD_disease[disease_id] = disease
    print('size of disease in neo4j:' + str(len(dict_CTD_disease)))


# list of map diseases to umls cui, with disease_id
list_map_to_cui = []

# list of disease_id which are not map to umls cui
list_not_map_to_cui = []

'''
find umls cui ids for all disease with use of umls
'''


def map_disease_to_cui():
    count_map_with_name = 0
    for disease_id, disease in dict_CTD_disease.items():
        cur = con.cursor()
        query = ("Select CUI,LAT,CODE,SAB, STR From MRCONSO Where SAB in ('%s') and CODE= '%s';")

        # depending on the idType the diseases id has to be search in Type MESH, OMIM or both
        if disease.idType == 'MESH':
            sab = 'MSH'
        elif disease.idType == 'OMIM':
            sab = 'OMIM'
        else:
            sab = ['MSH', 'OMIM']
            sab = "','".join(sab)

        name = disease.name.replace("'", "").lower()
        query = query % (sab, disease_id)
        rows_counter = cur.execute(query)
        if rows_counter > 0:
            # all result umls cuis
            list_cuis = []
            same_name = False
            # all result umls cuis which has the same name
            cui_with_same_name = []
            for (cui, lat, code, sab, label) in cur:
                label = label.lower().decode('utf-8')
                list_cuis.append(cui)
                if label == name:
                    same_name = True
                    cui_with_same_name.append(cui)

            # depending if with name or not the get the different umls cui list
            if same_name:
                disease.set_cuis(list(set(cui_with_same_name)))
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM and name to cui')
            else:
                disease.set_cuis(list(set(list_cuis)))
                dict_CTD_disease[disease_id].set_how_mapped('map with Mesh or OMIM to cui')

            list_map_to_cui.append(disease_id)
        else:
            print('Disease id which is not mapped directly:' + disease_id)
            cur = con.cursor()
            # if they do not mapped directly map with name in umls
            query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where SAB in ('MSH','OMIM') and lower(STR)= %s ;")
            rows_counter = cur.execute(query, (disease.name.lower(),))
            if rows_counter > 0:
                count_map_with_name += 1
                dict_CTD_disease[disease_id].set_how_mapped('map with name to cui ')
                list_cuis = []
                list_code = []
                for (cui, lat, code, sab) in cur:
                    list_cuis.append(cui)
                    list_code.append(code)
                print(list(set(list_code)))
                disease.set_cuis(list(set(list_cuis)))
                list_map_to_cui.append(disease_id)
            else:
                print('even now not')
                print(disease.idType)
                print(disease.altDiseaseIDs)
                print(disease.name)

                list_not_map_to_cui.append(disease_id)
    #        if len(list(set(list_cuis)))>1:
    #            print(disease_id)
    #            print(list(set(list_cuis)))
    print('number of map meshs with name:' + str(count_map_with_name))
    print('number of disease_id which are mapped to cui:' + str(len(list_map_to_cui)))
    print('number of disease_id which are not mapped to cui:' + str(len(list_not_map_to_cui)))


# search for the name of a given cui in the dictionary of the MRCONSO. It take the 
# prefer term if it has on else it take one possible name.


def get_name(cui):
    # list_of_names= dict_MRCONSO[cui]

    pn = False
    cur = con.cursor()
    query = ("Select * From MRCONSO Where CUI = %s AND ts='P' AND stt='PF' AND ispref='Y' And LAT= 'ENG'")
    rows_counter = cur.execute(query, (cui,))
    if rows_counter > 0:
        for name in cur:
            return name[14]
            pn = True
            break

    else:
        cur = con.cursor()
        query = ("Select * From MRCONSO Where CUI = %s And LAT= 'ENG'")
        rows_counter = cur.execute(query, (cui,))
        print(cui)
        if rows_counter > 0:
            for name in cur:
                # position11 tty
                if name[12] == 'PN':
                    return name[14]
                    pn = True
                    break
            if pn == False:
                for name in cur:
                    return name[14]
                    break
        else:
            query = ("Select * From MRCONSO Where CUI = %s")
            rows_counter = cur.execute(query, (cui,))
            print('This %s has no english term' % (cui))
            for name in cur:
                # position11 tty
                if name[12] == 'PN':
                    return name[14]
                    pn = True
                    break
            if pn == False:
                for name in cur:
                    return name[14]
                    break


# dictionary with all disease_ids which are mapped to hetionet 'map with Mesh or OMIM to cui'side effects, key is 
# disease_id and value is a list of cuis
dict_diseaseID_to_hetionet = {}

# list of go ids which are not mapped to hetionet
list_diseaseId_not_mapped_to_hetionet = []

# map files for the different how_mappeds
map_MO_and_name = open('disease_SE/ctd_disease_to_side_MESH_OMIM_to_cui_and_filter_with_name.tsv', 'w')
map_MO_and_name.write('MESH/OMIM \t type \t cuis with | as seperator \t cui names \n')

map_MO = open('disease_SE/ctd_disease_to_side_MESH_OMIM_to_cui.tsv', 'w')
map_MO.write('MESH/OMIM \t type \t cuis with | as seperator \t cui names  \n')

map_name = open('disease_SE/ctd_disease_to_side_name_to_cui.tsv', 'w')
map_name.write('MESH/OMIM \t type \t cuis with | as seperator \t cui names  \n')

# dictionary with how_mapped to file
dict_how_mapped_to_file = {
    'map with Mesh or OMIM and name to cui': map_MO_and_name,
    'map with Mesh or OMIM to cui': map_MO,
    'map with name to cui ': map_name}

'''
map disease to side effect form hetionet, by using the cui
'''


def map_disease_to_hetionet():
    for key, disease in dict_CTD_disease.items():
        if not key in list_not_map_to_cui:
            cuis = disease.cuis
            mapped_cui = []
            one_is_mapped = False
            string_cuis = "|".join(cuis)
            names = ''
            for cui in cuis:
                name = get_name(cui)
                names = names + name + '|'
            dict_how_mapped_to_file[disease.how_mapped].write(
                key + '\t' + disease.idType + '\t' + string_cuis + '\t' + names[:-1] + '\n')
            for cui in cuis:
                if cui in dict_side_effects_hetionet:
                    one_is_mapped = True
                    mapped_cui.append(cui)
            if one_is_mapped:
                dict_diseaseID_to_hetionet[key] = mapped_cui
                if len(mapped_cui) > 1:
                    print(key)
                    print(mapped_cui)
            else:
                list_diseaseId_not_mapped_to_hetionet.append(key)

    print('number of mapped to hetionet:' + str(len(dict_diseaseID_to_hetionet)))
    print('number of not mapped to hetionet:' + str(len(list_diseaseId_not_mapped_to_hetionet)))
    print(list_diseaseId_not_mapped_to_hetionet[0:10])


'''
integrate ctd disease into hetionet side effects:
the mapped on will get new properties
the not mapped one will create new SideEffect nodes
'''


def integrate_disease_into_hetionet():
    # side effects which are already in hetionet
    for disease_id, cuis in dict_diseaseID_to_hetionet.items():

        if len(cuis) == 1:
            resource = dict_side_effects_hetionet[cuis[0]].resource
            resource.append('CTD')
            resource = list(set(resource))
            resource = "','".join(resource)
            query = '''Match (s:SideEffect), (n:CTD_disease) Where s.identifier='%s' And n.disease_id='%s'
            Set s.resource=['%s'], s.ctd='yes', s.ctd_url='http://ctdbase.org/detail.go?type=disease&acc=%s' , n.cui='%s'
            Create (s)-[:equal_to_SE_Disease_CTD]->(n);
            '''
            if dict_CTD_disease[disease_id].idType == '':
                url_id = disease_id
            else:
                url_id = dict_CTD_disease[disease_id].idType + ':' + disease_id
            query = query % (cuis[0], disease_id, resource, url_id, cuis[0])
            g.run(query)

    # all new side effects
    for disease_id in list_diseaseId_not_mapped_to_hetionet:

        cui = dict_CTD_disease[disease_id].cuis[0]
        url = 'http://identifiers.org/umls/' + cui
        #        print(cui)
        query = '''Match (s:SideEffect{identifier:"%s"}) Return s'''
        query = query % (cui)
        node_exist = g.run(query)
        first_node = node_exist.evaluate()
        if first_node == None:
            name = dict_CTD_disease[disease_id].name.replace("'", "")
            query = '''Match  (n:CTD_disease) Where  n.disease_id='%s'
            Set n.cui='%s'
            Create (s:SideEffect{identifier:'%s', umls_label:'', aeolus:'no', sider:'no', url:'%s', hetionet:'no', source:'UMLS via CTD', name:'%s', conceptName:'',license:'Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved.', meddraType:'', resource:['CTD'], ctd:'yes', ctd_url:'http://ctdbase.org/detail.go?type=disease&acc=%s'}) 
            Create (s)-[:equal_to_SE_Disease_CTD]->(n);
            '''
            query = query % (disease_id, cui, cui, url, name, dict_CTD_disease[disease_id].idType + ':' + disease_id)
        else:
            query = '''Match  (n:CTD_disease), (s:SideEffect{identifier:'%s'}) Where  n.disease_id='%s'
            Set n.cui='%s'
            Create (s)-[:equal_to_SE_Disease_CTD]->(n);
            '''
            query = query % (cui, disease_id, cui)
        g.run(query)

    query = ''' Match  (s:SideEffect) Where not exists(s.ctd) Set s.ctd='no',s.ctd_url="" '''
    g.run(query)


def main():
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all side effect from hetionet into a dictionary')

    load_side_effects_from_hetionet_in_dict()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load all ctd diseases from neo4j into a dictionary')

    load_disease_CTD()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map disease id to cui with use of umls')

    map_disease_to_cui()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map disease to hetionet with use of cui')

    map_disease_to_hetionet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('integrate disease into hetionet')

    integrate_disease_into_hetionet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
