import xml.etree.ElementTree as ET
from collections import defaultdict
import os, sys, csv


def transform_label(text):
    """
    transform the real name in a neo4j label and addd source at the end
    :param text: string
    :return: string
    """
    return text.replace(' ', '_') + '_MEDRT'


# dictionary type short to full name
dict_short_to_full_name = {
    'MoA': transform_label('Mechanisms of Action'),
    'PE': transform_label('Physiologic Effects'),
    'EPC': transform_label('FDA Established Pharmacologic Classes'),
    'APC': transform_label('Additional Pharmacologic Classes'),
    'PK': transform_label('Pharmacokinetics'),
    'TC': transform_label('Therapeutic Categories'),
    'EXT': transform_label('Terminology Extensions for Classification'),
    'Chemical_Ingredient': transform_label('Chemical_Ingredient'),
    'Disease_Finding': transform_label('Disease_Finding'),
    'other': transform_label('other'),
    'HC': transform_label('local hierarchical concept'),
    'Dose_Form': transform_label('Dose Form'),
    'VA_Product': transform_label('VA Product')
}


def merge_dicts(x, y):
    """
    combine to dictionaries to one
    :param x:
    :param y:
    :return:
    """
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


def parse_CUI_line(line, xref_start, namespace):
    """
    parse the content to the different names. generate new file if this label has not already a file.
    Write the line infos as node in the file. And return the mapping between ID and cui.
    :param line: a line in one of the files
    :param xref_start: string
    :return: string (ID), dictionary
    """
    ID = line[0]
    tmp = line[1].strip(']').split('[')
    synonym1 = tmp[0].split(',')
    if len(tmp) == 1:
        print(ID)
        print(xref_start)
        filename = 'other'
    else:
        filename = tmp[1].replace('/', '_').replace(' ', '_')

        # some have no label but still a [] as name
        if filename not in dict_short_to_full_name:
            filename = 'other'
            synonym1 = line[0].split(',')
    # all rxcui are durgs
    if filename == 'other' and namespace == 'RxCUI':
        filename = 'Chemical_Ingredient'

    if not filename in dict_of_file_names:
        filename = filename.replace(' ', '_')
        csv_writer = generate_node_csv_files(filename)
        dict_of_file_names[filename] = csv_writer

    cui = line[2]
    tmp1 = line[3].split('[')
    synonym2 = tmp1[0].split(',')
    dict_id_to_label[ID] = filename

    synonym = set(synonym1).union(synonym2)
    info = {'id': ID, 'name': synonym.pop(), 'synonyme': '|'.join(synonym), 'xref': xref_start + ':' + cui}
    dict_of_file_names[filename].writerow(info)
    return ID, {'synonym': synonym, 'cui': cui}


def CUI_to_dic(CUI, xref_start):
    """
    generate dictionary with cui to n identifier
    :param CUI:
    :param xref_start:
    :return:
    """
    with open(CUI, 'r', encoding='utf-8') as c:
        csv_reader = csv.reader(c, delimiter='|')
        dic = dict(parse_CUI_line(l, xref_start, xref_start) for l in csv_reader)
    return {e['cui']: ID for ID, e in dic.items()}


def generate_rela_file_and_query(filename, from_label, to_label, path):
    """
    Generate for rela csv fiel and return it. Also, it add the query for this relationship with this types
    :param filename: string
    :param from_label: string
    :param to_label: string
    :param path: string
    :return: csv writer dictionary
    """
    filename = filename.replace(' ', '_')
    combinde_name = path + from_label + '_' + to_label + '_' + filename + '.csv'
    header = ["from_code", "to_code", "qualifier"]
    file = open(combinde_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header)
    csv_writer.writeheader()

    query_rela = query % (path_of_directory, combinde_name)
    query_rela += 'MAtch (from:%s {id: line.from_code}), (to:%s {id: line.to_code}) Create (from)-[:%s {qualifier: line.qualifier}]->(to);\n'
    query_rela = query_rela % (dict_short_to_full_name[from_label], dict_short_to_full_name[to_label], filename)
    cypher_file.write(query_rela)

    return csv_writer


# set of nodes which are generated without information
set_nodes_from_rela = set()


def add_nodes_without_infos(code, name, namespace, filename):
    """
    add node from mesh or rxnorm without known type
    :param code: string
    :param namespace: string
    :param name: string
    """
    if not filename in dict_of_file_names:
        csv_writer = generate_node_csv_files(filename)
        dict_of_file_names[filename] = csv_writer

    dict_id_to_label[code] = filename

    if not code in set_nodes_from_rela:
        infos = {'id': code, 'namespace': namespace, 'name': name}
        dict_of_file_names[filename].writerow(infos)
        set_nodes_from_rela.add(code)


def prepare_rela_and_add_to_file(root, dic, fIDName, path):
    """
    for geting the associations
    :param root:
    :param dic:
    :param fIDName:
    :return:
    """
    as_dic = defaultdict(dict)

    with open(fIDName, 'a+', encoding='utf-8') as fID:
        csv_writer = csv.writer(fID)
        csv_writer.writerow(["ID", "name", "namespace"])
        for ass in root.iter('association'):
            filename = ass.find('name').text
            namespace = ass.find('namespace').text
            to_code = ass.find('to_code').text
            from_code = ass.find('from_code').text
            qual = ass.find('qualifier')
            qname = qual.find('name').text
            qnamespace = qual.find('namespace').text
            qvalue = qual.find('value').text

            if to_code[0] != 'N':
                if to_code in dic:
                    to_code = dic[to_code]

                else:
                    to_name = ass.find('to_name').text
                    to_namespace = ass.find('to_namespace').text
                    if to_namespace == 'RxNorm':
                        add_nodes_without_infos(to_code, to_name, to_namespace, 'Chemical_Ingredient')
                    else:
                        add_nodes_without_infos(to_code, to_name, to_namespace, 'other')
                        csv_writer.writerow([to_code, filename, namespace])

            if from_code[0] != 'N':
                if from_code in dic:
                    from_code = dic[from_code]

                else:

                    from_name = ass.find('from_name').text
                    from_namespace = ass.find('from_namespace').text
                    if from_namespace == 'RxNorm':
                        add_nodes_without_infos(from_code, from_name, from_namespace, 'Chemical_Ingredient')
                    else:
                        add_nodes_without_infos(from_code, from_name, from_namespace, 'other')
                        csv_writer.writerow([from_code, filename, namespace])

            label_from = dict_id_to_label[from_code]
            label_to = dict_id_to_label[to_code]
            if (label_from, label_to) not in as_dic[filename]:
                csv_writer_rela = generate_rela_file_and_query(filename, label_from, label_to, 'output/')
                as_dic[filename][(label_from, label_to)] = csv_writer_rela

            as_dic[filename][(label_from, label_to)].writerow({'to_code': to_code,
                                                               'from_code': from_code,
                                                               'qualifier': qnamespace + ':' + qname + ':' + qvalue})

    return as_dic


# dictionary id to label
dict_id_to_label = {}

# header
header = ['id', 'status', 'namespace', 'name', 'propertys', 'synonyme', 'xref']

# dictionary of file names to file
dict_of_file_names = {}

# cypher file
cypher_file = open('cypher_med.cypher', 'w', encoding='utf-8')

# cypher file delete
cypher_file_delete = open('cypher_delete.cypher', 'w', encoding='utf-8')

# query sstart (FIELDTERMINATOR '\\t')
query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/import_into_Neo4j/med_rt/%s" As line  '''


def generate_node_csv_files(file_name):
    """
    generate csv file for node type and return. Additionaly add query to integrate this node type into neo4j
    :param file_name: string
    :return: csv writer dict
    """
    file_name = file_name.replace(' ', '_')
    file_name_short = 'output/' + file_name + '.csv'
    file = open(file_name_short, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=header)
    csv_writer.writeheader()

    query_node = query % (path_of_directory, file_name_short)
    query_node += 'Create (n:%s {'
    for head in header:
        if head in ['synonyme', 'propertys']:
            query_node += head + ': split(line.' + head + ',"|"), '
        else:
            query_node += head + ': line.' + head + ', '

    query_node = query_node[:-2] + '});\n'
    query_node = query_node % (dict_short_to_full_name[file_name])
    cypher_file.write(query_node)
    query_constraint = '''CREATE CONSTRAINT ON (n:%s) ASSERT n.id IS UNIQUE;\n''' % (dict_short_to_full_name[file_name])
    cypher_file.write(query_constraint)

    query_delete = 'Match (s:%s) Where not (s)--() Delete s;\n' % (dict_short_to_full_name[file_name])
    cypher_file_delete.write(query_delete)

    return csv_writer


def prepare_node_and_rela_and_write_to_files(fIDName):
    """
    
    :param fIDName: 
    :return: 
    """
    path = 'data/Core_MEDRT_XML/'
    xml_files = [f for f in os.listdir(path) if f.endswith('.xml')]
    if len(xml_files) == 1:
        file_name = xml_files[0]
    else:
        sys.exit('xml not in path ' + path)
    tree = ET.parse(path + file_name)
    root = tree.getroot()

    xml_dic = defaultdict(dict)
    for con in root.iter('concept'):
        propertys = []
        synonyme = []
        namespace = con.find('namespace').text
        tmp = con.find('name').text.strip(']').split('[')
        # if len(tmp) == 2:
        #     filename = tmp[1]
        #
        # else:
        #     filename = 'other'

        name = tmp[0]
        status = con.find('status').text
        code = con.find('code').text
        synonyms = con.findall('synonym')
        for s in synonyms:
            synonym = s.find('to_name').text
            if synonym not in synonyme:
                synonyme.append(synonym)
        prop = con.findall('property')
        for p in prop:
            pnamespace = p.find('namespace').text
            pname = p.find('name').text
            pvalue = p.find('value').text
            propertys.append(pnamespace + ':' + pname + ':' + pvalue)

            if pname == 'CTY':
                filename = pvalue

        if not filename in dict_of_file_names:
            csv_writer = generate_node_csv_files(filename)
            dict_of_file_names[filename] = csv_writer

        dict_id_to_label[code] = filename

        infos = {'id': code, 'status': status, 'namespace': namespace, 'name': name, 'propertys': '|'.join(propertys),
                 'synonyme': '|'.join(synonyme)}
        dict_of_file_names[filename].writerow(infos)

    # to avoid problems with data
    path = 'data/Core_MEDRT_Accessory_Files/'
    txt_files = [f for f in os.listdir(path) if 'DTS' not in f]
    for txt_file in txt_files:
        if 'mesh' in txt_file.lower():
            Mesh_CUI = path + txt_file
        elif 'rxnorm' in txt_file.lower():
            Rx_CUI = path + txt_file

    Mesh_map = CUI_to_dic(Mesh_CUI, 'MeSH')
    Rx_map = CUI_to_dic(Rx_CUI, 'RxCUI')
    dic = merge_dicts(Mesh_map, Rx_map)

    prepare_rela_and_add_to_file(root, dic, fIDName, path)

    return xml_dic


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path MED-RT')

    prepare_node_and_rela_and_write_to_files('falseID.csv')
    # nicht nötig da kene N...IDs in den Dateien vorhanden
    # xml_dic= look_synonyms(Rx_dic,xml_dic)
    # xml_dic= look_synonyms(Mesh_dic,xml_dic)


if __name__ == "__main__":
    # execute only if run as a script
    main()
