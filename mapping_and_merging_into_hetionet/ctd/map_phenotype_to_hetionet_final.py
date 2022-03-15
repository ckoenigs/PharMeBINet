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


class PhenotypeCTD:
    """
    go_id: string
    name: string
    cuis: list (umls cuis)
    how_mapped: string
    """

    def __init__(self, go_id, name):
        self.go_id = go_id
        self.name = name

    def set_cuis(self, cuis):
        self.cuis = cuis

    def set_how_mapped(self, how_mapped):
        self.how_mapped = how_mapped


# dictionary with all CTD phenotypes, which has a relationship with a drug
# the key is the GO id and value is class PhenotypeCTD
dict_CTD_phenotypes = {}

# dictionary for hetionet side effects with umls cui as key and value is class SideEffectHetionet
dict_side_effects_hetionet = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
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
    for result, in results:
        #        list_side_effect_in_hetionet.append(result['identifier'])
        sideEffect = SideEffectHetionet(result['identifier'], result['name'], result['resource'])
        dict_side_effects_hetionet[result['identifier']] = sideEffect
    print('size of side effects before the phenotype ctd is add:' + str(len(dict_side_effects_hetionet)))


'''
load in all ctd phenotypes from neo4j in a dictionary
'''


def load_phenotpypes_CTD():
    query = ''' MATCH (n:CTDphenotype) RETURN n'''
    results = g.run(query)
    for result, in results:
        go_id = 'GO:' + result['go_id']
        name = result['name']
        phenotype = PhenotypeCTD(go_id, name)
        dict_CTD_phenotypes[go_id] = phenotype
    print('size of phenotypes in neo4j:' + str(len(dict_CTD_phenotypes)))


# list of map phenotypes to umls cui, with go_id
list_map_to_cui = []

# list of go ids which are not map to umls cui
list_not_map_to_cui = []

'''
find cui ids for all phenotype with use of umls
Therefore use first the GO ID, because GO is integrated into umls.
If this is not working use the name to map to umls cui.
'''


def map_phenotype_to_cui():
    for go_id, phenotype in dict_CTD_phenotypes.items():
        cur = con.cursor()
        # search for GO ID in umls
        query = ("Select CUI,LAT,CODE, STR,SAB From MRCONSO Where SAB = 'GO' and CODE= %s ;")
        rows_counter = cur.execute(query, (go_id,))
        name = phenotype.name.lower()
        if rows_counter > 0:
            list_cuis = []
            mapped_name = False
            list_cuis_same_name = []
            for (cui, lat, code, label, sab) in cur:
                list_cuis.append(cui)
                label = label.lower().decode('utf-8')
                if label == name:
                    mapped_name = True
                    list_cuis_same_name.append(cui)

            if mapped_name:
                phenotype.set_cuis(list(set(list_cuis_same_name)))
                dict_CTD_phenotypes[go_id].set_how_mapped('Go to cui addition name map')
                list_map_to_cui.append(go_id)
            else:
                phenotype.set_cuis(list(set(list_cuis)))
                dict_CTD_phenotypes[go_id].set_how_mapped('Go to cui')
                list_map_to_cui.append(go_id)
        else:
            print('GO id which is not mapped directly:' + go_id)
            cur = con.cursor()
            # search for name in umls
            query = ("Select CUI,LAT,CODE,SAB From MRCONSO Where SAB = 'GO' and lower(STR)= %s ;")
            rows_counter = cur.execute(query, phenotype.name.lower())
            if rows_counter > 0:
                list_cuis = []
                list_code = []
                dict_CTD_phenotypes[go_id].set_how_mapped('Name to cui')
                for (cui, lat, code, sab) in cur:
                    list_cuis.append(cui)
                    list_code.append(code)
                #                print(list(set(list_code)))
                phenotype.set_cuis(list(set(list_cuis)))
                list_map_to_cui.append(go_id)
            else:
                list_not_map_to_cui.append(go_id)
    print('number of go_id which are mapped to cui:' + str(len(list_map_to_cui)))
    print('number of go_id which are not mapped to cui:' + str(len(list_not_map_to_cui)))


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


# dictionary with all go_ids which are mapped to hetionet side effects, key is
# go_id and value is a list of umls cuis
dict_goID_to_hetionet = {}

# list of go ids which are not mapped to hetionet
list_goid_not_mapped_to_hetionet = []

# file for  the different how_mapped
map_GO = open('phenotype/ctd_phenotyp_to_sideEffect_map_use_Go_id_to_cui.tsv', 'w')
map_GO.write('GO_id \t cuis with | as seperator \t cui names  \n')

map_name = open('phenotype/ctd_phenotyp_to_sideEffect_map_use_name_to_cui.tsv', 'w')
map_name.write('GO_id \t cuis with | as seperator \t cui names  \n')

map_Go_name = open('phenotype/ctd_phenotyp_to_sideEffect_map_use_GO_and_name_to_cui.tsv', 'w')
map_Go_name.write('GO_id \t cuis with | as seperator \t cui names  \n')

# dictionary with how_mapped as key and file as value
dict_how_mapped_file = {
    'Name to cui': map_name,
    'Go to cui': map_GO,
    'Go to cui addition name map': map_Go_name}

'''
map phenotype to side effect form hetionet, by using the umls cui
'''


def map_phenotype_to_hetionet():
    for key, phenotype in dict_CTD_phenotypes.items():
        cuis = phenotype.cuis
        mapped_cui = []
        one_is_mapped = False
        how_mapped = phenotype.how_mapped
        string_cuis = "|".join(cuis)
        names = ''
        for cui in cuis:
            name = get_name(cui)
            names = names + name + '|'
        dict_how_mapped_file[how_mapped].write(key + '\t' + string_cuis + '\t' + names[:-1] + '\n')
        for cui in cuis:
            if cui in dict_side_effects_hetionet:
                one_is_mapped = True
                mapped_cui.append(cui)
        if one_is_mapped:
            dict_goID_to_hetionet[key] = mapped_cui
        else:
            list_goid_not_mapped_to_hetionet.append(key)

    print('number of mapped to hetionet:' + str(len(dict_goID_to_hetionet)))
    print('number of not mapped to hetionet:' + str(len(list_goid_not_mapped_to_hetionet)))
    print(list_goid_not_mapped_to_hetionet[0:10])


'''
integrate phenotype into hetionet:
the mapped on will get new properties
the not mapped one will create new SideEffect nodes
'''


def integrate_phenotype_into_hetionet():
    # all ctd phenotypes which are mapped to hetionet side effects
    for go_id, cuis in dict_goID_to_hetionet.items():
        id_without_go = go_id.split(':')[1]

        if len(cuis) == 1:
            resource = set(dict_side_effects_hetionet[cuis[0]].resource)
            resource.add('CTD')
            resource = "','".join(sorted(resource))
            query = '''Match (s:SideEffect), (n:CTDphenotype) Where s.identifier='%s' And n.go_id='%s'
            Set s.resource=['%s'], s.ctd='yes', s.ctd_url='http://ctdbase.org/detail.go?type=go&acc=GO:%s' , n.cui='%s'
            Create (s)-[:equal_to_SE_CTD]->(n);
            '''
            query = query % (cuis[0], id_without_go, resource, id_without_go, cuis[0])
            g.run(query)
        else:
            print('ohje')
            sys.exit()

    # ctd phenotypes which have umls cui but are not mapped to a hetionet side effect generate new side effect
    for go_id in list_goid_not_mapped_to_hetionet:
        id_without_go = go_id.split(':')[1]
        cui = dict_CTD_phenotypes[go_id].cuis[0]
        url = 'http://identifiers.org/umls/' + cui
        print(cui)
        query = '''Match (s:SideEffect{identifier:"%s"}) Return s'''
        query = query % (cui)
        node_exist = g.run(query)
        first_node = node_exist.evaluate()
        if first_node == None:
            query = '''Match  (n:CTDphenotype) Where  n.go_id='%s'
            Set n.cui='%s'
            Create (s:SideEffect{identifier:'%s', umls_label:'', aeolus:'no', sider:'no', url:'%s', hetionet:'no', source:'UMLS via CTD', name:'%s',phenotype:'yes', only_phenotype:'yes', conceptName:'',license:'Copyright 2012-2017 MDI Biological Laboratory & NC State University. All rights reserved.', meddraType:'', resource:['CTD'], ctd:'yes', ctd_url:'http://ctdbase.org/detail.go?type=go&acc=GO:%s'}) 
            Create (s)-[:equal_to_SE_CTD]->(n);
            '''
            query = query % (id_without_go, cui, cui, url, dict_CTD_phenotypes[go_id].name, id_without_go)
        else:
            query = '''Match  (n:CTDphenotype), (s:SideEffect{identifier:'%s'}) Where  n.go_id='%s'
            Set n.cui='%s', s.phenotype='yes', s.only_phenotype='no', s.ctd='yes', s.ctd_url='http://ctdbase.org/detail.go?type=go&acc=GO:%s'
            Create (s)-[:equal_to_SE_CTD]->(n);
            '''
            query = query % (cui, id_without_go, cui, id_without_go)
        g.run(query)


#


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
    print('Load all ctd phenotypes from neo4j into a dictionary')

    load_phenotpypes_CTD()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map go id to cui with use of umls')

    map_phenotype_to_cui()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Map phenotype to hetionet with use of cui')

    map_phenotype_to_hetionet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('integrate phenotype into hetionet')

    integrate_phenotype_into_hetionet()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
