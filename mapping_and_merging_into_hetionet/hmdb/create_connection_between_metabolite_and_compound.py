import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dict db_id to real db_id
dict_db_id_to_real_db_id = {}

# dict inchikey to compound id
dict_inchiKey_to_compound_id = {}

# dictionary name to compound ids
dict_name_to_drugbank_ids = {}


def load_compounds():
    """
    Load compounds ids into a set.
    :return:
    """
    query = 'Match (n:Compound) Return n.identifier, n.alternative_ids, n.inchikey, n.name, n.synonyms'
    results = g.run(query)
    for record in results:
        [compound_id, alternative_ids, inchikey, name, synonyms] = record.values()
        dict_db_id_to_real_db_id[compound_id] = compound_id
        if alternative_ids:
            for alternative_id in alternative_ids:
                if alternative_id in dict_db_id_to_real_db_id and dict_db_id_to_real_db_id[
                    alternative_id] != compound_id:
                    print(alternative_id)
                    print(compound_id)
                    print(dict_db_id_to_real_db_id[alternative_id])
                    sys.exit('oh god double alternative id')
                dict_db_id_to_real_db_id[alternative_id] = compound_id
        if inchikey:
            dict_inchiKey_to_compound_id[inchikey] = compound_id

        if name:
            name = name.lower()
            if not name in dict_name_to_drugbank_ids:
                dict_name_to_drugbank_ids[name] = set()
            dict_name_to_drugbank_ids[name].add(compound_id)
        # if synonyms:
        #     for synonym in synonyms:
        #         synonym = synonym.lower()
        #         if not synonym in dict_name_to_drugbank_ids:
        #             dict_name_to_drugbank_ids[synonym] = set()
        #         dict_name_to_drugbank_ids[synonym].add(compound_id)


# set of metabolite compound pairs
set_metabolite_compound_pairs = set()


def write_rela_into_tsv_file(dict_to_compund_id, key, identifier, csv_writer, mapped):
    """
    get the compound id and check if pair is not written into tsv file. If not write into file and add to set.
    :param dict_to_compund_id: dictionary
    :param key: string
    :param identifier: string
    :param csv_writer: csv writer
    :param mapped: string
    :return:
    """
    compound_id = dict_to_compund_id[key]
    if (identifier, compound_id) not in set_metabolite_compound_pairs:
        csv_writer.writerow([identifier, compound_id, mapped])
        set_metabolite_compound_pairs.add((identifier, compound_id))


def get_all_metabolites_with_xrefs():
    file_name_rela = 'metabolite_compound_edge/rela.tsv'
    file_rela = open(file_name_rela, 'w', encoding='utf-8')
    csv_writer_rela = csv.writer(file_rela, delimiter='\t')
    csv_writer_rela.writerow(['identifier', 'drug_id', 'how_mapped'])

    cypher_query = ''' Match (n:Metabolite{identifier:line.identifier}), (m:Compound{identifier:line.drug_id})  Create (n)-[:EQUAL_MeC{mapping:line.how_mapped, source:'PharMeBINet', resource:['PharMeBINet'], pharmebinet:'yes', license:'CC0 1.0'}]->(m)'''
    cypher_query = pharmebinetutils.get_query_import(path_of_directory,
                                                     f'mapping_and_merging_into_hetionet/hmdb/{file_name_rela}',
                                                     cypher_query)
    cypher_file.write(cypher_query)

    query = 'MATCH (p:Metabolite_HMDB) Return p.identifier, p.xrefs, p.inchikey, p.name, p.synonyms'
    results = g.run(query)
    for record in results:
        [identifier, xrefs, inchikey, name, synonyms] = record.values()
        is_mapped = False
        if inchikey:
            if inchikey in dict_inchiKey_to_compound_id:
                write_rela_into_tsv_file(dict_inchiKey_to_compound_id, inchikey, identifier, csv_writer_rela,
                                         'inchikey')
                is_mapped = True

        if xrefs:
            if not is_mapped:
                drugbank_ids_hmdb = set()
                for xref in xrefs:
                    if xref.startswith('drugbank'):
                        db_id = xref.split(':')[1]
                        if db_id not in dict_db_id_to_real_db_id:
                            print('drugbank id not in drugbank?', db_id, identifier)
                        else:
                            drugbank_ids_hmdb.add(db_id)

                drugbank_ids_by_names = set() if name.lower() not in dict_name_to_drugbank_ids else \
                    dict_name_to_drugbank_ids[name.lower()]
                # if synonyms:
                #     for synonym in synonyms:
                #         synonym=synonym.lower()
                #         if synonym in dict_name_to_drugbank_ids:
                #             drugbank_ids_by_names=drugbank_ids_by_names.union(dict_name_to_drugbank_ids[synonym])

                intersection = drugbank_ids_by_names.intersection(drugbank_ids_hmdb)
                if len(intersection) > 0:
                    for db_id in intersection:
                        write_rela_into_tsv_file(dict_db_id_to_real_db_id, db_id, identifier, csv_writer_rela,
                                                 'drugbank_id_and_name')


def main():
    print(datetime.datetime.now())

    global path_of_directory, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hmdb metabolite')

    cypher_file = open('output/cypher_part2.cypher', 'a', encoding='utf-8')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load the compounds')

    load_compounds()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all hmdb Metabolite from database and write prepared information into tsv file')

    get_all_metabolites_with_xrefs()

    driver.close()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
