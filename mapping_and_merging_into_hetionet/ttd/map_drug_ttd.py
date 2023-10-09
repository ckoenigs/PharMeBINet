import csv, sys
import datetime

sys.path.append('..')
import change_xref_source_name_to_a_specifice_form

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary chemical id to resource
dict_chemical_id_to_resource = {}
# dictionary name to chemical ids
dict_name_to_chemical_ids = {}
# dictionary inchikey to chemical ids
dict_inchikey_to_chemical_ids = {}
# dictionary smiles to chemical ids
dict_smiles_to_chemicals = {}
# dictionary pubchem c id to chemical ids
dict_pubchem_c_ids_to_identifier = {}
# dictionary ttd id to chemical ids
dict_ttd_id_to_identifiers = {}


def load_chemical_information():
    """
    Load chemical information into different dictionaries
    :return:
    """

    query = "MATCH (n:Chemical) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms, n.inchikey, n.smiles"
    result = g.run(query)

    for record in result:
        [identifier, xrefs, resource, name, synonyms, inchikey, smiles] = record.values()
        xrefs = set(xrefs) if xrefs else set()
        dict_chemical_id_to_resource[identifier] = [resource, xrefs]

        if xrefs is not None:
            for x in xrefs:
                if "PubChem Compound" in x:
                    pubchem_compound = x.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_pubchem_c_ids_to_identifier, pubchem_compound,
                                                              identifier)
                elif x.startswith('Therapeutic Targets Database'):
                    ttd_id = x.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_ttd_id_to_identifiers, ttd_id,
                                                              identifier)

        if inchikey is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_inchikey_to_chemical_ids, inchikey, identifier)

        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids, name.lower(), identifier)

        if synonyms is not None:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids, synonym.lower(), identifier)

        if smiles is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_smiles_to_chemicals, smiles, identifier)


def prepare_cypher_file_and_queries(file_name, file_name_new):
    """
    Prepare all queries for the mapping nodes. The load all props from TTD and prepare query for new node generation.
    Return the header for the new node tsv
    :param file_name: string
    :param file_name_new: string
    :return:
    """
    # cypher file
    with open("output/cypher.cypher", "a", encoding="utf-8") as cypher_file:
        query = f'Match (p1:TTD_Drug{{id:line.node_id}}),(p2:Chemical{{identifier:line.identifier}}) SET p2.xrefs=split(line.xrefs,"|"), p2.resource = split(line.resource,"|"), p2.ttd="yes" Create (p1)-[:equal_to_ttd_drug{{how_mapped:line.how_mapped }}]->(p2)'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                                  query)
        cypher_file.write(query)

        query = f'Match (p2:Chemical{{identifier:line.identifier}}) Where line.inchikey is not NULL and p2.inchikey is NULL SET p2.inchikey = line.inchikey'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                                  query)
        cypher_file.write(query)

        query = f'Match (p2:Chemical{{identifier:line.identifier}}) Where line.smiles is not NULL and p2.smiles is NULL SET p2.smiles = line.smiles'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  f'mapping_and_merging_into_hetionet/ttd/{file_name}',
                                                  query)
        cypher_file.write(query)

        query_start = 'Match (p:TTD_Drug{id:line.id}) Merge (m:Compound :Chemical{identifier:line.new_id}) On Create Set '
        query = 'MATCH (p:TTD_Drug) WITH DISTINCT keys(p) AS keys UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields RETURN allfields;'
        list_of_props = []
        header = ['id', 'new_id', 'xrefs']
        result = g.run(query)
        for record in result:
            [allfields] = record.values()
            if allfields in ['pubchem_cids', 'chebi_id', 'adi_id', 'id', 'pubchem_sids']:
                continue
            header.append(allfields)
            if allfields == 'inchi_key':
                list_of_props.append('m.inchikey=line.' + allfields)
            elif allfields == 'canonical_smiles':
                list_of_props.append('m.smiles=line.' + allfields)
            elif allfields in ['synonyms', 'drug_class', 'company', 'superdrug_atcs']:
                if allfields not in ['drug_class', 'company']:
                    list_of_props.append('m.' + allfields + '=split(line.' + allfields + ',"|")')
                elif allfields == 'company':
                    list_of_props.append('m.companies=split(line.' + allfields + ',"|")')
                else:
                    list_of_props.append('m.' + allfields + 'es=split(line.' + allfields + ',"|")')
            else:
                list_of_props.append('m.' + allfields + '=line.' + allfields)
        query_start += ', '.join(
            list_of_props) + ', m.identifier=line.new_id, m.xrefs=split(line.xrefs,"|") ,m.ttd="yes", m.source="PubChem via TTD", m.resource=["TTD"], m.url="https://db.idrblab.net/ttd/data/drug/details/"+line.id, m.license="https://www.nlm.nih.gov/copyright.html" Create (p)-[:equal_to_ttd_drug]->(m)'

        query_start = pharmebinetutils.get_query_import(path_of_directory,
                                                        f'mapping_and_merging_into_hetionet/ttd/{file_name_new}',
                                                        query_start)
        cypher_file.write(query_start)
    return header


def prepare_new_node_tsv(header, file_name_new, dict_new_nodes):
    """
    Generate the tsv file and write the information into the tsv.
    :param header:
    :param file_name_new:
    :param dict_new_nodes:
    :return:
    """
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_writer = csv.writer(file_new, delimiter='\t')
    csv_writer.writerow(header)
    for new_id, dict_of_infos in dict_new_nodes.items():
        counter = 0
        for node_id in dict_of_infos['id']:
            if 'name' not in dict_of_infos:
                print(node_id, 'without name')
                continue
            xrefs = change_xref_source_name_to_a_specifice_form.go_through_xrefs_and_change_if_needed_source_name(
                dict_of_infos['xrefs'], 'Compound')
            prepare_line = [node_id, new_id, '|'.join(xrefs)]
            if counter == 0:
                for head in header[3:]:
                    if head in dict_of_infos:
                        value = dict_of_infos[head]
                        if type(value) == set:
                            prepare_line.append('|'.join(value))
                        else:
                            prepare_line.append(value)
                    else:
                        prepare_line.append("")

            csv_writer.writerow(prepare_line)
            counter += 1


def prepare_xrefs(identifier, pubchem_cids):
    dict_chemical_id_to_resource[identifier][1] = dict_chemical_id_to_resource[identifier][1].union(
        ["PubChem Compound:" + x for x in pubchem_cids])
    return '|'.join(dict_chemical_id_to_resource[identifier][1])


def compound_ttd_mapping():
    # save the identifier and the Raw_ID in a tsv file
    file_name = 'drug/drug_mapping.tsv'
    file_name_new = 'drug/drug_new.tsv'

    dict_new_nodes = {}
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["node_id", "identifier", "resource", "how_mapped", 'inchikey', 'smiles', 'xrefs']
        writer.writerow(line)
        query = "MATCH (n:TTD_Drug) Where (n)--() RETURN n.id, n.canonical_smiles, n.inchi_key, n.name, n.pubchem_cids, n.chebi_id, n.pubchem_sids, n "
        result = g.run(query)

        counter = 0
        counter_mapped = 0
        for record in result:
            [node_id, smiles, inchikey, name, pubchem_cids, chebi_id, pubchem_sids, node] = record.values()
            counter += 1
            mapping_found = False

            pubchem_cids = pubchem_cids if pubchem_cids else []

            if inchikey in dict_inchikey_to_chemical_ids:
                counter_mapped += 1
                mapping_found = True
                for identifier in dict_inchikey_to_chemical_ids[inchikey]:
                    writer.writerow([node_id, identifier,
                                     pharmebinetutils.resource_add_and_prepare(
                                         dict_chemical_id_to_resource[identifier][0],
                                         'TTD'), 'inchikey', inchikey, smiles, prepare_xrefs(identifier, pubchem_cids)])

            if mapping_found:
                continue

            if smiles is not None:
                if smiles in dict_smiles_to_chemicals:
                    counter_mapped += 1
                    mapping_found = True
                    for identifier in dict_smiles_to_chemicals[smiles]:
                        writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_id_to_resource[identifier][0], 'TTD'), 'smiles', inchikey, smiles,
                                         prepare_xrefs(identifier, pubchem_cids)])
            if mapping_found:
                continue

            # no mapping appeared I could not check the mapping!
            # if node_id in dict_ttd_id_to_identifiers:
            #     counter_mapped += 1
            #     mapping_found = True
            #     for identifier in dict_ttd_id_to_identifiers[node_id]:
            #         writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
            #             dict_chemical_id_to_resource[identifier][0], 'TTD'), 'ttd id', inchikey, smiles, prepare_xrefs(identifier,pubchem_cids)])
            #
            # if mapping_found:
            #     continue

            if len(pubchem_cids) > 0:
                # check that they are not combined compounds
                if name is None or not (' + ' in name or 'combination' in name.lower() or '; ' in name or '/ ' in name):
                    for pubchem_cid in pubchem_cids:
                        if pubchem_cid in dict_pubchem_c_ids_to_identifier:
                            mapping_found = True
                            for identifier in dict_pubchem_c_ids_to_identifier[pubchem_cid]:
                                writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
                                    dict_chemical_id_to_resource[identifier][0], 'TTD'), 'pubchem', inchikey, smiles,
                                                 prepare_xrefs(identifier, pubchem_cids)])
            if mapping_found:
                counter_mapped += 1
                continue

            if name is not None:
                name = name.lower()
                if name in dict_name_to_chemical_ids:
                    counter_mapped += 1
                    mapping_found = True
                    for identifier in dict_name_to_chemical_ids[name]:
                        writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_id_to_resource[identifier][0], 'TTD'), 'name', inchikey, smiles,
                                         prepare_xrefs(identifier, pubchem_cids)])
            if mapping_found:
                continue

            # no mapping is working new nodes with pubchem id are integrated
            if len(pubchem_cids) > 0:
                if len(pubchem_cids) == 1:
                    new_id = pubchem_cids[0]

                    xrefs = set(['Therapeutic Targets Database:' + node_id, 'PubChem Compound:' + new_id])
                    if chebi_id:
                        xrefs.add(chebi_id)

                    if pubchem_sids:
                        for pubchem_sid in pubchem_sids:
                            xrefs.add('PubChem Substance:' + pubchem_sid)

                    # prepare new node information and combine information
                    if new_id not in dict_new_nodes:
                        node = dict(node)
                        node['id'] = set([node['id']])
                        if 'drug_class' in node:
                            node['drug_class'] = set([node['drug_class']])
                        if 'company' in node:
                            node['company'] = set([node['company']])
                        if 'synonyms' in node:
                            node['synonyms'] = set(node['synonyms'])
                        if 'superdrug_atcs' in node:
                            node['superdrug_atcs'] = set(node['superdrug_atcs'])
                        node['xrefs'] = xrefs
                        dict_new_nodes[new_id] = node

                    else:
                        dict_to_up_date = dict_new_nodes[new_id]
                        dict_to_up_date['xrefs'] = dict_new_nodes[new_id]['xrefs'].union(xrefs)
                        for key, value in dict(node).items():
                            if key not in dict_to_up_date:
                                if key != 'synonyms':
                                    dict_to_up_date[key] = value
                                elif key in ['drug_class', 'company', 'superdrug_atcs']:
                                    dict_to_up_date[key] = set([value])
                                else:
                                    dict_to_up_date[key] = set(value)
                            elif key in ['id', 'drug_class', 'company', 'superdrug_atcs']:
                                dict_to_up_date[key].add(value)
                            elif key in ['synonyms']:
                                dict_to_up_date[key] = dict_to_up_date[key].union(value)
                            elif key in dict_to_up_date and not value == dict_to_up_date[key]:
                                # names add to synonyms but try to avoid name with start PMID
                                if 'name' == key:
                                    old_name = dict_to_up_date['name']
                                    if 'synonyms' not in dict_to_up_date:
                                        dict_to_up_date['synonyms'] = set()
                                    if old_name.startswith('PMID'):
                                        dict_to_up_date['synonyms'].add(old_name)
                                        dict_to_up_date['name'] = value
                                    else:
                                        dict_to_up_date['synonyms'].add(value)
                                    continue
                                # case which are not important to combine
                                elif key in ['highest_status']:
                                    continue
                                print('different values for the same key')
                                print(key, value)
                                print(dict_to_up_date[key], new_id, dict_to_up_date['id'], node_id)
                                # TODO

    print('number of nodes:', counter)
    print('number of mapped nodes:', counter_mapped)
    print("######### Start: Cypher #########")

    header = prepare_cypher_file_and_queries(file_name, file_name_new)

    print("######### End: Cypher #########")

    prepare_new_node_tsv(header, file_name_new, dict_new_nodes)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd')

    print(datetime.datetime.now())
    print('create connection')
    create_connection_with_neo4j()

    print('#' * 50)
    print(datetime.datetime.now())
    print('load chemical information')
    load_chemical_information()

    print('#' * 50)
    print(datetime.datetime.now())
    print('map compound')
    compound_ttd_mapping()

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
