import datetime
import sys, csv
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# dictionary with chemical id as key and the whole node as value
dict_chemical_pharmebinet_to_resource = {}

# dictionary synonyms/name/brands chemical ids
dict_synonyms_to_chemicals_ids = {}

# dictionary from rxcui to chemical ids
dict_rnxnorm_to_chemical_id = {}

# dictionary mesh id to chemicals ids
dict_mesh_id_to_chemicals_ids = {}

'''
create connection to neo4j and mysql
'''


def create_connection_with_neo4j_mysql():
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()

    # create connection with mysql database
    global con
    con = create_connection_to_databases.database_connection_umls()

    # generate connection to mysql to RxNorm database
    global conRxNorm
    conRxNorm = create_connection_to_databases.database_connection_RxNorm()


def check_for_rxcui(name, rxcui):
    """
    check if the rxcui ids are right
    :param name: string
    :param rxcui: string
    :return: list of strings
    """
    query = ('Select Distinct RXCUI  From RXNCONSO Where STR ="%s" ;')
    query = query % (name)
    # print(query)

    cur = conRxNorm.cursor()
    rows_counter = cur.execute(query)
    found_id = False
    if rows_counter > 0:
        other_id = []
        for rxnorm_cui in cur:
            if rxnorm_cui[0] == rxcui:
                found_id = True
            else:
                other_id.append(rxnorm_cui[0])
    else:
        # there is nothing that can found in rxnorm
        found_id = True
    if found_id:
        return [rxcui]
    else:
        return other_id


'''
load in all compound from pharmebinet in a dictionary
'''


def load_pharmebinet_chemical_in():
    query = '''MATCH (n:Chemical) RETURN n.identifier,n'''
    results = g.run(query)

    for record in results:
        [identifier, node] = record.values()
        dict_chemical_pharmebinet_to_resource[identifier] = dict(node)['resource']
        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_chemicals_ids, name, identifier)

        synonyms = node['synonyms']
        if synonyms:
            for synonym in synonyms:
                synonym = synonym.lower()
                pharmebinetutils.add_entry_to_dict_to_set(dict_synonyms_to_chemicals_ids, synonym, identifier)
        xrefs = node['xrefs'] if 'xrefs' in node else []
        for xref in xrefs:
            if xref.startswith('RxNorm_CUI:'):
                xref = xref.split(':', 1)[1]
                rxcuis = check_for_rxcui(name, xref)
                for rxcui in rxcuis:
                    pharmebinetutils.add_entry_to_dict_to_set(dict_rnxnorm_to_chemical_id, rxcui, identifier)
            elif xref.startswith('MESH:'):
                xref = xref.split(':', 1)[1]
                pharmebinetutils.add_entry_to_dict_to_set(dict_mesh_id_to_chemicals_ids, xref, identifier)

    print('length of compound in pharmebinet:' + str(len(dict_chemical_pharmebinet_to_resource)))


def prepare_csv_file_and_cypher_file():
    """
    Prpare csv file and cypher query.
    :return:
    """
    file_name = 'chemical/map_chemical.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['med_id', 'id', 'resource', 'how_mapped'])

    cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')
    query = 'Match (n:Chemical_Ingredient_MEDRT{id:line.med_id}), (r:Chemical{identifier:line.id}) Set r.resource=split(line.resource,"|"), r.med_rt="yes" Create (r)-[:equal_chemical_med_rt{how_mapped:line.how_mapped}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              'mapping_and_merging_into_hetionet/med_rt/' + file_name, query)
    cypher_file.write(query)

    return csv_writer


dict_manual_mapping_identifier={
    'N0000178919':'DBSALT000845',
    'N0000179741':'DBSALT001473',
    'N0000178917':'DBSALT000206',
    'N0000178915':'DBSALT000267',
    'N0000179466':'DBSALT001025',
    'N0000179641':'DBSALT000299',
    'N0000178961':'DBSALT000999',
    'N0000178975':'DBSALT000262',
    'N0000179005':'DBSALT001356',
    'DBSALT000316':'DBSALT000316',
    'N0000179512':'DBSALT000991',
    'N0000005922':'DB00986',
    'N0000179599':'DBSALT002390',
    'N0000178984':'DBSALT000726',
    'N0000179419':'DBSALT000429',
    'N0000178978':'DBSALT000417',
    'N0000179299':'DBSALT000264',
    'N0000179427':'DBSALT000734',
    'N0000178897':'DBSALT001319',
    'N0000179746':'DBSALT001341',
    'N0000179438':'DBSALT001968',
    'N0000005781':'DBSALT000985',
    'N0000007469':'DBSALT002769',
    'N0000145823':'DBSALT002390',
    'N0000145826':'DBSALT000726',
    'N0000145824':'DBSALT000299'

}


def load_med_rt_drug_in():
    query = '''MATCH (n:Chemical_Ingredient_MEDRT) RETURN n'''
    results = g.run(query)

    csv_writer = prepare_csv_file_and_cypher_file()
    count = 0
    counter_mapped = 0

    set_mapped_pairs=set()

    for record in results:
        result = record.data()['n']
        count += 1
        identifier = result['id']
        xref = result['xref'] if 'xref' in result else ''
        name = result['name'].lower()

        synonyms= result['synonyms'] if 'synonyms' in result else []

        mapped = False

        if xref.startswith('MeSH'):
            mesh_id = xref.split(':')[1]
            if mesh_id in dict_mesh_id_to_chemicals_ids:
                mapped = True
                counter_mapped += 1
                for chemical_id in dict_mesh_id_to_chemicals_ids[mesh_id]:
                    if (identifier,chemical_id) in set_mapped_pairs:
                        continue
                    set_mapped_pairs.add((identifier,chemical_id))
                    csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                        dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'mesh'])
        elif xref.startswith('RxCUI'):
            rx_id = xref.split(':')[1]
            # wrong mapping in rxnorm !!!!!!!!!
            if rx_id!='1860418':
                if rx_id in dict_rnxnorm_to_chemical_id:
                    mapped = True
                    counter_mapped += 1
                    for chemical_id in dict_rnxnorm_to_chemical_id[rx_id]:
                        if (identifier, chemical_id) in set_mapped_pairs:
                            continue
                        set_mapped_pairs.add((identifier, chemical_id))
                        csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'rxcui'])

        if mapped:
            continue

        if identifier in dict_manual_mapping_identifier:
            chemical_id=dict_manual_mapping_identifier[identifier]
            mapped=True
            csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'manual'])

        if mapped:
            continue

        if 'namespace' in result:
            # wrong mapping in rxnorm !!!!!!!!! chrysarobin->Hemoglobin
            if identifier != '1860418':
                if identifier in dict_rnxnorm_to_chemical_id:
                    mapped = True
                    counter_mapped += 1
                    for chemical_id in dict_rnxnorm_to_chemical_id[identifier]:
                        if (identifier, chemical_id) in set_mapped_pairs:
                            continue
                        set_mapped_pairs.add((identifier, chemical_id))
                        csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'rxcui_id'])

        if mapped:
            continue

        if name in dict_synonyms_to_chemicals_ids:
            mapped = True
            counter_mapped += 1
            for chemical_id in dict_synonyms_to_chemicals_ids[name]:
                if (identifier, chemical_id) in set_mapped_pairs:
                    continue
                set_mapped_pairs.add((identifier, chemical_id))
                csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                    dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'name'])

        if mapped:
            continue

        if xref.startswith('MeSH') :
            query = ('Select Distinct RXCUI, CODE   From RXNCONSO Where SCUI ="%s" and SAB="MSH" ;')
            query = query % (xref.split(':')[1])

            cur = conRxNorm.cursor()
            rows_counter = cur.execute(query)
            rxcuis = set()
            set_real_mesh_xref=set()
            if rows_counter > 0:
                for (rxnorm_cui, real_mesh_id) in cur:
                    rxcuis.add(rxnorm_cui)
                    set_real_mesh_xref.add(real_mesh_id)
                    if real_mesh_id in dict_chemical_pharmebinet_to_resource:
                        mapped=True
                        if (identifier, real_mesh_id) in set_mapped_pairs:
                            continue
                        set_mapped_pairs.add((identifier, real_mesh_id))
                        csv_writer.writerow([identifier, real_mesh_id, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'rxnorm_to_mesh_id'])
                    # elif real_mesh_id in dict_mesh_id_to_chemicals_ids:
                    #     for chemical_id in dict_mesh_id_to_chemicals_ids[real_mesh_id]:
                    #         if (identifier, chemical_id) in set_mapped_pairs:
                    #             continue
                    #         set_mapped_pairs.add((identifier, chemical_id))
                    #         mapped = True
                    #         csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                    #             dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'rxnorm_to_mesh_id'])

        if mapped:
            counter_mapped += 1
            continue

        if xref.startswith('MeSH') and len(rxcuis)>0:
            for rxnorm_cui in rxcuis:

                if rxnorm_cui in dict_rnxnorm_to_chemical_id:
                    mapped = True
                    for chemical_id in dict_rnxnorm_to_chemical_id[rxnorm_cui]:
                        if (identifier, chemical_id) in set_mapped_pairs:
                            continue
                        set_mapped_pairs.add((identifier, chemical_id))
                        csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'rxcui_from_rxnorm'])

        if mapped:
            counter_mapped += 1
            continue

        if xref.startswith('MeSH') and len(rxcuis)>0:
            # mapping is not so good
            if identifier in ['N0000179651', 'N0000179713']:
                continue
            query = ('Select Distinct CODE  From RXNCONSO Where RXCUI in ("%s") and SAB="DRUGBANK" ;')
            query = query % ('","'.join(rxcuis))

            cur = conRxNorm.cursor()
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (drugbank_id,) in cur:
                    if drugbank_id in dict_chemical_pharmebinet_to_resource:
                        mapped = True
                        if (identifier, drugbank_id) in set_mapped_pairs:
                            continue
                        set_mapped_pairs.add((identifier, drugbank_id))
                        csv_writer.writerow([identifier, drugbank_id, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'mesh_drugbank_from_rxnorm'])

        if mapped:
            counter_mapped += 1
            continue

        if xref.startswith('RxCUI') or 'namespace' in result:
            if xref.startswith('RxCUI'):
                cui = xref.split(':')[1]
            else:
                cui = identifier
            query = ('Select Distinct STR  From RXNCONSO Where RXCUI ="%s" ;')
            query = query % (cui)

            cur = conRxNorm.cursor()
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (alternative_name,) in cur:
                    alternative_name=alternative_name.lower()
                    if alternative_name in dict_synonyms_to_chemicals_ids:
                        mapped = True
                        for chemical_id in dict_synonyms_to_chemicals_ids[alternative_name]:
                            if (identifier, chemical_id) in set_mapped_pairs:
                                continue
                            set_mapped_pairs.add((identifier, chemical_id))
                            csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                                dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'name_rxnorm'])

        if mapped:
            counter_mapped += 1

        if len(synonyms)>0:
            for synonym in synonyms:
                synonym=synonym.lower()
                if synonym in dict_synonyms_to_chemicals_ids:
                    mapped = True
                    counter_mapped += 1
                    for chemical_id in dict_synonyms_to_chemicals_ids[synonym]:
                        if (identifier, chemical_id) in set_mapped_pairs:
                            continue
                        set_mapped_pairs.add((identifier, chemical_id))
                        csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'synonyms'])

        if mapped:
            continue

        if xref.startswith('MeSH') and len(rxcuis)>0:

            query = ('Select Distinct STR  From RXNCONSO Where RXCUI  in ("%s") ;')
            query = query % ('","'.join(rxcuis))

            cur = conRxNorm.cursor()
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (alternative_name,) in cur:
                    alternative_name=alternative_name.lower()
                    if alternative_name in dict_synonyms_to_chemicals_ids:
                        mapped = True
                        for chemical_id in dict_synonyms_to_chemicals_ids[alternative_name]:
                            if (identifier, chemical_id) in set_mapped_pairs:
                                continue
                            set_mapped_pairs.add((identifier, chemical_id))
                            csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                                dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'mesh_name_rxnorm'])

        if mapped:
            counter_mapped += 1


        if xref.startswith('MeSH'):

            query = ('Select Distinct RXCUI  From RXNCONSO Where STR ="%s" ;')
            query = query % (name)

            cur = conRxNorm.cursor()
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (rxcui,) in cur:
                    if rxcui in dict_rnxnorm_to_chemical_id:
                        mapped = True
                        for chemical_id in dict_rnxnorm_to_chemical_id[rxcui]:
                            if (identifier, chemical_id) in set_mapped_pairs:
                                continue
                            set_mapped_pairs.add((identifier, chemical_id))
                            csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
                                dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'name_rxnorm_chemical'])

        if mapped:
            counter_mapped += 1

        # if xref.startswith('MeSH') and len(set_real_mesh_xref)>0:
        #     for real_mesh_id in set_real_mesh_xref:
        #         if real_mesh_id in dict_mesh_id_to_chemicals_ids:
        #             for chemical_id in dict_mesh_id_to_chemicals_ids[real_mesh_id]:
        #                 if (identifier, chemical_id) in set_mapped_pairs:
        #                     continue
        #                 set_mapped_pairs.add((identifier, chemical_id))
        #                 mapped = True
        #                 csv_writer.writerow([identifier, chemical_id, pharmebinetutils.resource_add_and_prepare(
        #                     dict_chemical_pharmebinet_to_resource[chemical_id], 'MED-RT'), 'rxnorm_to_mesh_id_xref'])
        #
        # if mapped:
        #     counter_mapped += 1

    print('number of chemicals in med-rt', count)
    print('number of mapped chemicals in med-rt', counter_mapped)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in chemical from pharmebinet')

    load_pharmebinet_chemical_in()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Load in drug from med-rt')

    load_med_rt_drug_in()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
