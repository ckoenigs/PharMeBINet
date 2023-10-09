import os, csv, sys

sys.path.append("../..")
import pharmebinetutils


def generate_files(path_of_directory, file_name, source, label_bindingdb, label_pharmebinet, id_property_bindingdbs):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_path = os.path.join(path_of_directory, file_name)
    header = ['node_id', 'pharmebinet_node_id', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8', newline="")
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/DisGeNet/
    prepare_where_string = ''
    for id_property_bindingdb in id_property_bindingdbs:
        prepare_where_string += f'n.{id_property_bindingdb}=line.node_id or '
    query = f' Match (n:{label_bindingdb}), (v:{label_pharmebinet}{{identifier:line.pharmebinet_node_id}}) Where {prepare_where_string[:-3]} Set v.bindingdb="yes", v.resource=split(line.resource,"|") Create (v)-[:equal_to_bindingDB_{label_pharmebinet.lower()}{{mapped_with:line.mapping_method}}]->(n)'
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name,
                                              query)
    query = query.replace("/", "")
    cypher_file.write(query)
    return csv_mapping
