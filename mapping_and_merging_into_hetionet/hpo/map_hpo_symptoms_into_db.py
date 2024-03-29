import sys
import datetime, time
import csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name


# connect with the neo4j database AND MYSQL
def database_connection():
    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


def cui_to_mesh(cui):
    """
    function to find mesh id for a cui
    :param cui:
    :return:
    """

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


def name_to_umls_cui(name):
    """
    function to find mesh id for a cui
    :param cui:
    :return:
    """

    cur = con.cursor()
    query = ('Select Distinct CUI From MRCONSO Where STR="%s";')
    query = query % (name)
    rows_counter = cur.execute(query)
    if rows_counter > 0:
        codes = []
        for code, in cur:
            codes.append(code)

        codes = list(set(codes))
        return codes
    else:
        return []


def prepare_dictionary_for_file(dictionary):
    """
    prepare dictionary for writing into tsv file. This means list and sets are transformed to string
    :param dictionary: dictionary
    :return:
    """
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) != str:
            value = '|'.join(value)
        new_dict[key] = value
    return new_dict


def generate_cypher_queries_and_tsv_files():
    """
    generate cypher queries and tsv files
    :return: csv writer for mapping and new
    """
    set_header_for_files = ['hpo_id', 'pharmebinet_id', 'xrefs', 'mesh_ids', 'resource', 'umls_ids', 'how_mapped',
                            'level']
    # tsv file for mapping disease
    file_name_mapped = 'mapping_files/symptom_mapped.tsv'
    file_symptom_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_symptom_mapped = csv.DictWriter(file_symptom_mapped, delimiter='\t', fieldnames=set_header_for_files)
    csv_symptom_mapped.writeheader()

    # tsv file for mapping disease
    file_name_new = 'mapping_files/symptom_new.tsv'
    file_symptom_new = open(file_name_new, 'w', encoding='utf-8')
    csv_symptom_new = csv.DictWriter(file_symptom_new, delimiter='\t', fieldnames=set_header_for_files)
    csv_symptom_new.writeheader()

    # cypher file for mapping and integration
    cypher_file = open('cypher/cypher.cypher', 'a')

    query = '''MATCH (p:HPO_symptom) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields as l;'''
    results = g.run(query)

    license = 'This service/product uses the Human Phenotype Ontology (January 2024). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well.'

    query_start_match = '''Match (s:Symptom{identifier:line.pharmebinet_id }) , (n:HPO_symptom{id:line.hpo_id}) Set s.hpo='yes', s.umls_cuis=split(line.umls_cuis,"|"), s.highest_level=line.level,  s.resource=split(line.resource,"|") , s.hpo_release='%s', s.url_HPO="https://hpo.jax.org/app/browse/term/"+line.hpo_id, n.mesh_ids=split(line.mesh_ids,'|'), s.xrefs=s.xrefs + line.hpo_id, '''
    query_start_create = '''Match (n:HPO_symptom{id:line.hpo_id}) Create (s:Symptom{identifier:line.pharmebinet_id, umls_cuis:split(line.umls_cuis,"|"), highest_level:line.level ,source:'HPO', resource:['HPO'], source:'HPO', hpo:'yes', hpo_release:'%s', license:'%s', url:"https://hpo.jax.org/app/browse/term/"+line.hpo_id, xrefs:split(line.xrefs,"|"), '''

    for record in results:
        property = record.data()['l']
        if property in ['name', 'id', 'created_by', 'creation_date', 'is_obsolete', 'replaced_by', 'subset',
                        'considers']:
            if property == 'name':
                query_start_create += property + ':n.' + property + ', '
            continue
        elif property == 'def':
            query_start_create += 'definition:n.' + property + ', '
            query_start_match += 's.definition=n.definition+n.' + property + ', '
        elif property == 'alt_ids':
            query_start_create += 'alternative_ids:n.' + property + ', '
            query_start_match += 's.alternative_ids=n.' + property + ', '

        elif property in ['xrefs']:
            query_start_create += property + ':split(line.' + property + ',"|"), '
            query_start_match += 's.' + property + '=split(line.' + property + ',"|"), '
        else:
            query_start_create += property + ':n.' + property + ', '
            query_start_match += 's.' + property + '=n.' + property + ', '

    query_match = query_start_match[:-2] + ' Create (s)-[:equal_to_hpo_symptoms{how_mapped:line.how_mapped}]->(n)'
    query_match = query_match % (ontology_date)
    query_match = pharmebinetutils.get_query_import(path_of_directory,
                                                    f'mapping_and_merging_into_hetionet/hpo/{file_name_mapped}',
                                                    query_match)
    cypher_file.write(query_match)

    query_create = query_start_create[:-2] + '})-[:equal_to_hpo_symptoms{how_mapped:line.how_mapped}]->(n)  '
    query_create = query_create % (ontology_date, license)
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/hpo/{file_name_new}',
                                                     query_create)
    cypher_file.write(query_create)

    query = '''Match (s1:Symptom)--(a:HPO_symptom)-[:is_a]->(:HPO_symptom)--(s2:Symptom) Where not ID(s1)=ID(s2) Merge (s1)-[:IS_A_SiaS{license:"%s",hpo_release:'%s', source:"HPO", resource:["HPO"], hpo:"yes", url:"https://hpo.jax.org/app/browse/term/"+a.id}]->(s2);\n'''
    query = query % (license, ontology_date)
    cypher_file.write(query)

    return csv_symptom_mapped, csv_symptom_new


## dictionary of symptoms
dict_of_pharmebinet_symptoms = {}

# dictionary name_to_symptom
dict_name_to_symptom_id = {}

# dictionary umls cuis to mesh
dict_umls_cui_to_mesh = {}


def get_all_symptoms_and_add_to_dict():
    """
    Get al symptoms from pharmebinet and put this information into a dictionary
    :return:
    """
    query = '''MATCH (n:Symptom) RETURN n  '''
    results = g.run(query)

    # add all symptoms to dictioanry
    for record in results:
        result = record.data()['n']
        identifier = result['identifier']
        dict_of_pharmebinet_symptoms[identifier] = dict(result)

        name = result['name'].lower()
        if name not in dict_name_to_symptom_id:
            dict_name_to_symptom_id[name] = set()
        dict_name_to_symptom_id[name].add(identifier)

        umls_cuis = name_to_umls_cui(name)
        for cui in umls_cuis:
            if cui not in dict_umls_cui_to_mesh:
                dict_umls_cui_to_mesh[cui] = set()
            dict_umls_cui_to_mesh[cui].add(identifier)


def map_names(name, how_mapped, node_id, xrefs, level):
    found_one = False
    if name in dict_name_to_symptom_id:
        found_one = True
        for mesh_id in dict_name_to_symptom_id[name]:
            resource = dict_of_pharmebinet_symptoms[mesh_id]['resource'] if 'resource' in \
                                                                            dict_of_pharmebinet_symptoms[
                                                                                mesh_id] else []
            resource.append('HPO')
            resource = list(set(resource))
            xrefs_mesh = dict_of_pharmebinet_symptoms[mesh_id]['xrefs'] if 'xrefs' in dict_of_pharmebinet_symptoms[
                mesh_id] else []
            xrefs_mesh = set(xrefs_mesh).union(xrefs)
            if mesh_id in dict_mapped_mesh:
                # dict_mapped_mesh[mesh_id]['how_mapped'].append('name')
                dict_mapped_mesh[mesh_id]['hpos_how_mapped'].add((node_id, how_mapped))
                dict_mapped_mesh[mesh_id]['xrefs'] = dict_mapped_mesh[mesh_id]['xrefs'].union(xrefs)
            else:
                dict_node = {
                    # 'how_mapped': ['name'],
                    'hpos_how_mapped': set([(node_id, how_mapped)]),
                    'resource': resource,
                    'xrefs': xrefs_mesh,
                    'level': level + 1
                }
                dict_mapped_mesh[mesh_id] = dict_node
    return found_one


# dictionary mapped mesh ids to infos
dict_mapped_mesh = {}


def map_hpo_symptoms_and_to_pharmebinet(csv_new):
    """
    Map hpo symptomes to umls cui or mesh and generate connection between symptoms and hpo symptoms. Further the
    hpo symptoms get the mapped umls_cui or mesh as property.
    :return:
    """

    count_mapped = 0
    counter_new = 0

    query = 'Match (m:HPO_symptom{id:"HP:0000118"} )  RETURN m.id, m.xrefs'
    results = g.run(query)
    for record in results:
        [node_id, xrefs] = record.values()
        mesh_ids = set()
        umls_cuis = set()
        if xrefs is not None:
            for xref in xrefs:
                if xref.startswith('MSH:'):
                    mesh_ids.add(xref.split(':')[1])

                elif xref[0:4] == 'UMLS':
                    umls_cuis.add(xref.split(':')[1])
        else:
            xrefs = []

        # add hpo to xrefs
        xrefs.append('HPO:' + node_id)
        dict_node = {
            'hpo_id': node_id,
            'pharmebinet_id': node_id,
            'xrefs': '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'symptom')),
            'mesh_ids': '|'.join(mesh_ids),
            'umls_ids': '|'.join(umls_cuis),
            'how_mapped': 'new',
            'level': '1'
        }
        csv_new.writerow(dict_node)
        counter_new += 1

    query_nodes = 'MATCH (n:HPO_symptom)-[:is_a]->(m:HPO_symptom ) Where n.is_obsolete is NULL and m.id in ["%s"] RETURN n.id, n.name, n.xrefs, n.synonyms'

    dict_nodes = {}

    level = 1
    dict_level_to_ids = {level: set(['HP:0000118'])}

    while level in dict_level_to_ids:
        new_query = query_nodes
        new_query = new_query % ('","'.join(dict_level_to_ids[level]))
        results = g.run(new_query)
        set_ids_of_level = set()
        for record in results:
            [node_id, name, xrefs, synonyms] = record.values()
            if node_id in dict_nodes:
                continue
            set_ids_of_level.add(node_id)
            dict_nodes[node_id] = (name, xrefs)
            mesh_ids = set()
            umls_cuis = set()
            if xrefs is not None:
                for xref in xrefs:
                    if xref.startswith('MSH:'):
                        mesh_ids.add(xref.split(':')[1])

                    elif xref[0:4] == 'UMLS':
                        umls_cuis.add(xref.split(':')[1])
            else:
                xrefs = []

            # found one
            found_one = False
            # add hpo to xrefs
            xrefs.append('HPO:' + node_id)

            name = name.lower()
            found_one = map_names(name, 'name', node_id, xrefs, level)
            if found_one:
                count_mapped += 1
                continue

            if synonyms:
                for synonym in synonyms:
                    synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                    found_one = map_names(synonym, 'synonyms', node_id, xrefs, level) or found_one

            if found_one:
                count_mapped += 1
                continue

            dict_node = {
                'hpo_id': node_id,
                'pharmebinet_id': node_id,
                'xrefs': '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'symptom')),
                'mesh_ids': '|'.join(mesh_ids),
                'umls_ids': '|'.join(umls_cuis),
                'how_mapped': 'new',
                'level': level + 1
            }
            csv_new.writerow(dict_node)
            counter_new += 1
        if len(set_ids_of_level) == 0:
            break
        level += 1
        dict_level_to_ids[level] = set_ids_of_level

    print('number of mapped nodes:', count_mapped)
    print('number of new nodes:', counter_new)


def prepare_mapped_nodes_for_file(csv_mapped):
    """
    write the information into tsv file.
    :param csv_mapped: csv writer
    :return:
    """
    for mesh_id, dict_info in dict_mapped_mesh.items():
        dict_node = {
            'pharmebinet_id': mesh_id,
            'xrefs': '|'.join(go_through_xrefs_and_change_if_needed_source_name(dict_info['xrefs'], 'symptom')),
            'resource': '|'.join(dict_info['resource'])
            # 'how_mapped': '|'.join(set(dict_info['how_mapped']))
        }
        if len(dict_info['hpos_how_mapped']) > 1:
            print(mesh_id)
        for (hpo_id, how_mapped) in dict_info['hpos_how_mapped']:
            dict_node['hpo_id'] = hpo_id
            dict_node['how_mapped'] = how_mapped
            dict_node['level'] = dict_info['level']
            csv_mapped.writerow(dict_node)


def main():
    print(datetime.datetime.now())

    global path_of_directory, ontology_date
    if len(sys.argv) > 2:
        path_of_directory = sys.argv[1]
        ontology_date = sys.argv[2]
    else:
        sys.exit('need a path and ontology date')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate dictionary from symptoms of pharmebinet')

    get_all_symptoms_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('generate files and cypher queries')

    csv_mapped, csv_new = generate_cypher_queries_and_tsv_files()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('map hpo symptoms to mesh or umls cui and integrated them into pharmebinet')

    map_hpo_symptoms_and_to_pharmebinet(csv_new)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('The mapped nodes are wrote into file')

    prepare_mapped_nodes_for_file(csv_mapped)

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())

    con.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
