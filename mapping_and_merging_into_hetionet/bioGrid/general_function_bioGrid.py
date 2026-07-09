import os, csv, sys

sys.path.append("../..")
import pharmebinetutils

license = pharmebinetutils.dict_source_to_license['biogrid']

def generate_files(path_of_directory, file_name, source, label_biogrid, label_pharmebinet, id_property_biogrids):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_path = os.path.join(path_of_directory, file_name)
    header = ['node_id', 'pharmebinet_node_id', 'resource', 'mapping_method', 'licenses']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    prepare_where_string = ''
    for id_property_biogrid in id_property_biogrids:
        prepare_where_string += f'n.{id_property_biogrid}=line.node_id or '
    query = f' Match (n:{label_biogrid}), (v:{label_pharmebinet}{{identifier:line.pharmebinet_node_id}}) Where {prepare_where_string[:-3]} Set v.biogrid=true, v.resource=split(line.resource,"|"), v.licenses=split(line.licenses,"|") Create (v)-[:equal_to_bioGrid_{label_pharmebinet.lower()}{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    cypher_file.write(query)
    return csv_mapping

def write_to_tsv_file(dict_pharmebinet_id_to_resource,csv_mapping, identifier, pharmebinet_id, mapping_method):
    dict_pharmebinet_id_to_resource[pharmebinet_id][1].add(pharmebinetutils.dict_source_to_license['biogrid'])
    csv_mapping.writerow(
        [identifier, pharmebinet_id,
         pharmebinetutils.resource_add_and_prepare(dict_pharmebinet_id_to_resource[pharmebinet_id][0],
                                                   "BioGRID"),
         mapping_method, '|'.join(dict_pharmebinet_id_to_resource[pharmebinet_id][1])])