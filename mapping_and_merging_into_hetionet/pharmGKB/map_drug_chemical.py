import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_and_mysql():
    global g
    g = create_connection_to_databases.database_connection_neo4j()
    

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()


# dictionary of all chemical ids to resource
dict_chemical_to_resource = {}

# dictionary inchi to chemical id
dict_inchi_to_chemical_id = {}

# dictionary_pubchem_compound to chemical id
dict_pubchem_compound_to_chemical_id = {}

# dictionary rxnorm cui to chemical id
dict_rxcui_to_chemical_id = {}

# dictionary name to chemical id
dict_name_to_chemical_id={}

# dictionary name to pharmacological class ids
dict_name_to_pharmacologic_class= {}

# dictionary pharmacological class id to resource
dict_pc_to_resource={}


def add_value_to_dictionary(dictionary, key, value):
    """
    add key to dictionary if not existing and add value to set
    :param dictionary: dictionary
    :param key: string
    :param value: string
    :return:
    """
    if value not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(value)

def load_pharmacological_class():
    """
    load pharmacological information
    :return:
    """
    query='''Match (n:PharmacologicClass) Return n.identifier, n.name, n.synonyms, n.resource '''

    for identifier, name, synonyms, resource, in g.run(query):
        dict_pc_to_resource[identifier]=resource
        
        if name:
            name=name.lower()
            add_value_to_dictionary(dict_name_to_pharmacologic_class, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym=synonym.lower()
                add_value_to_dictionary(dict_name_to_pharmacologic_class, synonym, identifier)

'''
load in all compound from hetionet in a dictionary
'''


def load_db_info_in():
    query = '''MATCH (n:Chemical) Where not n:Product RETURN n.identifier,n.inchi, n.xrefs, n.resource, n.name, n.synonyms'''
    results = g.run(query)

    for identifier, inchi, xrefs, resource, name, synonyms, in results:
        dict_chemical_to_resource[identifier] = resource if resource else []
        if inchi:
            dict_inchi_to_chemical_id[inchi] = identifier

        if xrefs:
            for xref in xrefs:
                value = xref.split(':', 1)[1]
                if xref.startswith('PubChem Compound'):
                    add_value_to_dictionary(dict_pubchem_compound_to_chemical_id, value, identifier)
                elif xref.startswith('RxNorm_CUI'):
                    add_value_to_dictionary(dict_rxcui_to_chemical_id, value, identifier)
        if name:
            name=name.lower()
            add_value_to_dictionary(dict_name_to_chemical_id, name, identifier)

        if synonyms:
            for synonym in synonyms:
                synonym=synonym.lower()
                add_value_to_dictionary(dict_name_to_chemical_id, synonym, identifier)

    print('length of chemical in db:' + str(len(dict_chemical_to_resource)))


def add_information_to_file(drugbank_id, identifier, csv_writer, how_mapped, tuple_set, dict_to_resource):
    """
    add mapper to file if not already is added!
    :param drugbank_id:
    :param identifier:
    :param csv_writer:
    :param how_mapped:
    :param tuple_set:
    :return:
    """
    if (drugbank_id, identifier) in tuple_set:
        return
    tuple_set.add((drugbank_id, identifier))
    resource = dict_to_resource[drugbank_id]
    resource.append('PharmGKB')
    resource = "|".join(sorted(set(resource)))
    csv_writer.writerow([drugbank_id, identifier, resource, how_mapped])


def load_pharmgkb_in(label):
    """
    generate mapping file and cypher file for a given label
    map nodes to chemical
    :param label: string
    :return:
    """

    # csv_file
    file_name = 'chemical/mapping_' + label.split('_')[1] + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['identifier', 'pharmgkb_id', 'resource', 'how_mapped'])

    # csv file pharmacological file
    file_name_pc = 'chemical/mapping_pharmacological_class_' + label.split('_')[1] + '.tsv'
    file_pc = open(file_name_pc, 'w', encoding='utf-8')
    csv_writer_pc = csv.writer(file_pc, delimiter='\t')
    csv_writer_pc.writerow(['identifier', 'pharmgkb_id', 'resource', 'how_mapped'])

    not_mapped_file=open('chemical/not_mapping_' + label.split('_')[1] + '.tsv', 'w', encoding='utf-8')
    csv_writer_not = csv.writer(not_mapped_file, delimiter='\t')
    csv_writer_not.writerow([ 'pharmgkb_id', 'namr'])
    # generate cypher file
    generate_cypher_file(file_name, label)

    query = '''MATCH (n:%s) RETURN n'''
    query = query % (label)
    results = g.run(query)

    counter_map = 0
    counter_not_mapped = 0

    # set of all tuples
    set_of_all_tuples = set()

    # set of all tuple to pc
    set_of_all_tuples_with_pc=set()

    for result, in results:
        identifier = result['id']

        mapped = False
        inchi = result['inchi'] if 'inchi' in result else ''
        cross_references = result['cross_references'] if 'cross_references' in result else []
        for cross_reference in cross_references:
            value = cross_reference.split(':', 1)[1]
            if cross_reference.startswith('DrugBank'):
                if value in dict_chemical_to_resource:
                    mapped = True
                    add_information_to_file(value, identifier, csv_writer, 'drugbank', set_of_all_tuples, dict_chemical_to_resource)

        if mapped:
            counter_map += 1
            continue

        if inchi in dict_inchi_to_chemical_id:
            mapped = True
            counter_map += 1
            add_information_to_file(dict_inchi_to_chemical_id[inchi], identifier, csv_writer, 'inchi',
                                        set_of_all_tuples, dict_chemical_to_resource)

        if mapped:
            continue

        pubchem_compound_identifiers = result[
            'pubchem_compound_identifiers'] if 'pubchem_compound_identifiers' in result else []
        for pubchem_compound_identifier in pubchem_compound_identifiers:
            if pubchem_compound_identifier in dict_pubchem_compound_to_chemical_id:
                mapped = True
                counter_map += 1
                for drugbank_id in dict_pubchem_compound_to_chemical_id[pubchem_compound_identifier]:
                    add_information_to_file(drugbank_id, identifier, csv_writer, 'pubchem compound',
                                            set_of_all_tuples, dict_chemical_to_resource)
        if mapped:
            continue

        rxnorm_identfiers = result[
            'rxnorm_identifiers'] if 'rxnorm_identifiers' in result else []
        for rxnorm_identfier in rxnorm_identfiers:
            if rxnorm_identfier in dict_rxcui_to_chemical_id:
                mapped = True
                counter_map += 1
                for drugbank_id in dict_rxcui_to_chemical_id[rxnorm_identfier]:
                    add_information_to_file(drugbank_id, identifier, csv_writer, 'rxcui',
                                            set_of_all_tuples, dict_chemical_to_resource)

        if mapped:
            continue

        if identifier in dict_chemical_to_resource:
            mapped = True
            add_information_to_file(identifier, identifier, csv_writer, 'mesh', set_of_all_tuples, dict_chemical_to_resource)

        if mapped:
            continue

        name= result['name'] if 'name'  in result else ''
        if len(name)>0:
            name=name.lower()
            if name in dict_name_to_chemical_id:
                mapped = True
                counter_map += 1
                for drugbank_id in dict_name_to_chemical_id[name]:
                    add_information_to_file(drugbank_id, identifier, csv_writer, 'name',
                                            set_of_all_tuples, dict_chemical_to_resource)
        if mapped:
            continue
        
        if len(name)>0:
            name=name.lower()
            if name in dict_name_to_pharmacologic_class:
                mapped=True
                counter_map += 1
                for pharmacological_class_id in dict_name_to_pharmacologic_class[name]:
                    add_information_to_file(pharmacological_class_id, identifier, csv_writer_pc, 'name',
                                            set_of_all_tuples_with_pc, dict_pc_to_resource)

        if mapped:
            continue

        if len(name) > 0:
            name = name.lower()
            cur = con.cursor()
            # if not mapped map the name to umls cui
            query = ('Select CUI,LAT,CODE,SAB From MRCONSO Where STR= "%s" And SAB="MSH" ;')
            query = query % (name)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (cui, lat, code, sab) in cur:
                    if code in dict_chemical_to_resource:
                        mapped = True
                        add_information_to_file(identifier, code, csv_writer, 'mesh umls', set_of_all_tuples,
                                                dict_chemical_to_resource)


        if not mapped:
            counter_not_mapped += 1
            csv_writer_not.writerow([identifier, result['name'], result['types']])
        else:
            counter_map+=1

    print('number of chemical/drug which mapped:', counter_map)
    print('number of mapped:',len(set_of_all_tuples)+ len(set_of_all_tuples_with_pc))
    print('mapped with pc:', len(set_of_all_tuples_with_pc))
    print('number of chemical/drug which not mapped:', counter_not_mapped)


def generate_cypher_file(file_name, label):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/pharmGKB/%s" As line  FIELDTERMINATOR '\\t'  MATCH (n:%s{id:line.pharmgkb_id}), (c:Chemical{identifier:line.identifier})  Set c.pharmgkb='yes', c.resource=split(line.resource,'|') Create (c)-[:equal_to_%s_phamrgkb{how_mapped:line.how_mapped}]->(n); \n'''
    query = query % (file_name, label, label.split('_')[1].lower())
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j_and_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in chemical from hetionet')

    load_db_info_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load in pharmacological class from hetionet')

    load_pharmacological_class()

    for label in ['PharmGKB_Drug', 'PharmGKB_Chemical']:
        print(
            '###########################################################################################################################')

        print(datetime.datetime.utcnow())
        print('Load in %s from pharmgb in' % (label))

        load_pharmgkb_in(label)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
