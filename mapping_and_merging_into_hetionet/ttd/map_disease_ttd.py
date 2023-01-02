import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped, dict_resource):
    """
    Write mapped identifier into file
    :param csv_writer:
    :param raw_id:
    :param mapped_ids:
    :param how_mapped:
    :return:
    """
    for map_id in mapped_ids:
        csv_writer.writerow(
            [raw_id, map_id, pharmebinetutils.resource_add_and_prepare(dict_resource[map_id], "TTD"),
             how_mapped])


def load_disease_or_symptom_information(label, dictionary_label_to_mapper_to_key_values, dict_id_to_resource):
    """
    Load disease or symptom information into different dictionaries
    :return:
    """

    query = f'MATCH (n:{label}) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms'
    result = g.run(query)

    dictionary_label_to_mapper_to_key_values[label] = {
        'icd9': {},
        'icd10': {},
        'icd11': {},
        'name': {}
    }

    for identifier, xref, resource, name, synonyms, in result:

        dict_id_to_resource[identifier] = resource

        if xref is not None:
            for x in xref:
                if x.startswith('ICD11'):
                    id = x.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dictionary_label_to_mapper_to_key_values[label]['icd11'],
                                                              id,
                                                              identifier)
                elif x.startswith('ICD10'):
                    id = x.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dictionary_label_to_mapper_to_key_values[label]['icd10'],
                                                              id,
                                                              identifier)
                elif x.startswith('ICD9'):
                    id = x.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dictionary_label_to_mapper_to_key_values[label]['icd9'],
                                                              id,
                                                              identifier)
        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dictionary_label_to_mapper_to_key_values[label]['name'],
                                                      name.lower(), identifier)

        if synonyms is not None:
            for synonym in synonyms:
                synonym = pharmebinetutils.prepare_obo_synonyms(synonym).lower()
                pharmebinetutils.add_entry_to_dict_to_set(dictionary_label_to_mapper_to_key_values[label]['name'],
                                                          synonym, identifier)


def compound_ttd_mapping():
    # save the identifier and the Raw_ID in a tsv file
    file_name = 'disease/disease_mapping.tsv'
    file_name_symptom='disease/symptom_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["node_id", "identifier", "resource", "how_mapped"]
        writer.writerow(line)
        tsv_file_symptom=open(file_name_symptom,'w',encoding='utf-8')
        writer_symptom=csv.writer(tsv_file_symptom, delimiter='\t')
        writer_symptom.writerow(line)

        query = "MATCH (n:TTD_Disease) RETURN n.id,  n.name, n.ICD9, n.ICD10 ,n.ICD11"
        result = g.run(query)

        counter = 0
        counter_mapped = 0
        for node_id, name, icd9s, icd10s, icd11s, in result:
            counter += 1
            mapping_found = False

            if name is not None:
                # some have at the end of the name the icd11 number
                if '[ICD-11:' in name:
                    name = name.split(' [ICD-11:')[0]
                name = name.lower()
                if name in dictionary_label_to_mapper_to_key_values['Disease']['name']:
                    counter_mapped += 1
                    mapping_found = True
                    write_infos_into_file(writer, node_id,
                                          dictionary_label_to_mapper_to_key_values['Disease']['name'][name], 'name',
                                          dict_disease_id_to_resource)

            if mapping_found:
                continue

            if name in dictionary_label_to_mapper_to_key_values['Symptom']['name']:
                counter_mapped += 1
                mapping_found = True
                write_infos_into_file(writer_symptom, node_id,
                                      dictionary_label_to_mapper_to_key_values['Symptom']['name'][name], 'name',
                                      dict_symptom_id_to_resource)

            if mapping_found:
                continue

            if icd11s:
                for icd11 in icd11s:
                    if icd11 in dictionary_label_to_mapper_to_key_values['Disease']['icd11']:
                        counter_mapped += 1
                        mapping_found = True
                        write_infos_into_file(writer, node_id,
                                          dictionary_label_to_mapper_to_key_values['Disease']['icd11'][icd11], 'icd11',
                                          dict_disease_id_to_resource)

            if mapping_found:
                continue

            # if icd10s:
            #     for icd10 in icd10s:
            #         if icd10 in dictionary_label_to_mapper_to_key_values['Disease']['icd10']:
            #             counter_mapped += 1
            #             mapping_found = True
            #             write_infos_into_file(writer, node_id,
            #                               dictionary_label_to_mapper_to_key_values['Disease']['icd10'][icd10], 'icd10',
            #                               dict_disease_id_to_resource)
            #
            # if mapping_found:
            #     continue

            if icd10s:
                for icd10 in icd10s:
                    if icd10 in dictionary_label_to_mapper_to_key_values['Symptom']['icd10']:
                        counter_mapped += 1
                        mapping_found = True
                        write_infos_into_file(writer_symptom, node_id,
                                          dictionary_label_to_mapper_to_key_values['Symptom']['icd10'][icd10], 'icd10',
                                          dict_symptom_id_to_resource)

            if mapping_found:
                continue

            # if icd9s:
            #     for icd9 in icd9s:
            #         if icd9 in dictionary_label_to_mapper_to_key_values['Disease']['icd9']:
            #             counter_mapped += 1
            #             mapping_found = True
            #             write_infos_into_file(writer, node_id,
            #                               dictionary_label_to_mapper_to_key_values['Disease']['icd9'][icd9], 'icd9',
            #                               dict_disease_id_to_resource)

            if mapping_found:
                counter_mapped += 1
                continue

            if icd9s:
                for icd9 in icd9s:
                    if icd9 in dictionary_label_to_mapper_to_key_values['Symptom']['icd9']:
                        counter_mapped += 1
                        mapping_found = True
                        write_infos_into_file(writer_symptom, node_id,
                                          dictionary_label_to_mapper_to_key_values['Symptom']['icd9'][icd9], 'icd9',
                                          dict_symptom_id_to_resource)

            if mapping_found:
                counter_mapped += 1
                continue
        tsv_file_symptom.close()

    print('number of nodes:', counter)
    print('number of mapped nodes:', counter_mapped)
    print("######### Start: Cypher #########")

    # cypher file
    with open("output/cypher.cypher", "a", encoding="utf-8") as cypher_file:
        query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/ttd/{file_name}" As line fieldterminator "\t" '
        query = query_start + f'Match (p1:TTD_Disease{{id:line.node_id}}),(p2:Disease{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.ttd="yes" Create (p1)-[:equal_to_ttd_disease{{how_mapped:line.how_mapped }}]->(p2);\n'
        cypher_file.write(query)
        query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/ttd/{file_name_symptom}" As line fieldterminator "\t" '
        query = query_start + f'Match (p1:TTD_Disease{{id:line.node_id}}),(p2:Symptom{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.ttd="yes" Create (p1)-[:equal_to_ttd_disease{{how_mapped:line.how_mapped }}]->(p2);\n'
        cypher_file.write(query)

    print("######### End: Cypher #########")


def main():
    global path_of_directory, dictionary_label_to_mapper_to_key_values, dict_symptom_id_to_resource
    global dict_disease_id_to_resource
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd')

    print(datetime.datetime.now())
    print('create connection')
    create_connection_with_neo4j()

    print('#' * 50)
    print(datetime.datetime.now())
    print('load disease and symptom information')
    dictionary_label_to_mapper_to_key_values = {}
    dict_disease_id_to_resource = {}
    dict_symptom_id_to_resource = {}
    load_disease_or_symptom_information('Disease', dictionary_label_to_mapper_to_key_values,
                                        dict_disease_id_to_resource)
    load_disease_or_symptom_information('Symptom', dictionary_label_to_mapper_to_key_values,
                                        dict_symptom_id_to_resource)

    print('#' * 50)
    print(datetime.datetime.now())
    print('map compound')
    compound_ttd_mapping()


if __name__ == "__main__":
    # execute only if run as a script
    main()
