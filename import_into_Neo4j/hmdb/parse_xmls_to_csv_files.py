import os
import csv, json
import datetime
import sys
import wget
import lxml.etree as etree
from zipfile import ZipFile

ns = '{http://www.hmdb.ca}'


def prepare_tsv_dictionary(dictionary):
    """
    Prepare dictionary for writing into tsv file with only strings.
    :param dictionary: dictionary
    :return: dictionary
    """
    new_dictionary = {}
    for key, value in dictionary.items():
        # print(key, value)
        if type(value) in [set, list]:
            value = list(value)
            if len(value) == 0:
                # print('empty values')
                # print(key, value)
                continue
            if type(value[0]) != str:
                value = [json.dumps(x) for x in value]
            value = "||".join(value)
        elif type(value) == dict:
            value = json.dumps(value)
        elif type(value) == str:
            value = value.replace('\n', '').strip()
        if value is None or value == '':
            continue
        value = value.replace('\\"', '"')
        new_dictionary[key] = value
    return new_dictionary


def add_key_value_to_dictionary_as_list(dictionary, key, value):
    """
    Add a key value pair into a dictionary with a list.
    :param dictionary: dictionary
    :param key:  string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)


dict_node_type_to_tsv = {}


def generate_tsv_file(label, properties):
    """
    Prepare a filename. The generate a file and make a csv writer on it.
    :param label: string
    :param properties: list
    :return: string
    """
    file_name = 'output/' + label + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file, fieldnames=properties, delimiter='\t', quotechar='"')
    csv_writer.writeheader()

    dict_node_type_to_tsv[label] = csv_writer
    return file_name


# cypher file
cypherfile = open('output/cypher.cypher', 'w')


def prepare_node_cypher_query(file_name, label, properties, list_properties):
    """
    Prepare the cypher query fo a node.
    :param file_name: string
    :param label: string
    :param properties: list
    :param list_properties: list
    :return:
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/hmdb/%s" As line Fieldterminator '\\t' Create (n:%s_HMDB{ '''

    query = query % (file_name, label.capitalize())

    for property in properties:
        if property in list_properties:
            query += property + ':split(line.' + property + ',"||"), '
        else:
            query += property + ':line.' + property + ', '
    query = query[:-2] + '});\n'
    cypherfile.write(query)
    query = 'Create Constraint On (node:%s_HMDB) Assert node.%s Is Unique;\n'
    query = query % (label.capitalize(), properties[0])
    cypherfile.write(query)


def prepare_edge_cypher_query(file_name, label_from, label, rela_name, properties, list_properties):
    """
    Prepare the cypher query fo a node.
    :param file_name: string
    :param label: string
    :param properties: list
    :param list_properties: list
    :return:
    """
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/hmdb/%s" As line Fieldterminator '\\t' Match (n:%s_HMDB{identifier:line.%s}), (b:%s_HMDB{%s:line.%s}) Create (n)-[:%s'''

    query = query + '{' if len(properties) > 2 else query
    query = query % (
        file_name, label_from.capitalize(), properties[0], label.capitalize(), 'identifier', properties[1], rela_name)
    # if label in ['pathway', 'disease']:
    #     query = query % (file_name,label_from.capitalize(), properties[0], label.capitalize(), 'identifier', properties[1], rela_name)
    # else:
    #     query = query % (file_name, label_from.capitalize(), properties[0], label.capitalize(), 'id', properties[1], rela_name)
    for property in properties[2:]:
        if property in list_properties:
            query += property + ':split(line.' + property + ',"||"), '
        else:
            query += property + ':line.' + property + ', '
    query = query[:-2] + '}]->(b);\n' if len(properties) > 2 else query + ']->(b);\n'
    cypherfile.write(query)


def generates_node_tsv_file_and_cypher(label, properties, list_properties):
    """

    :return:
    """
    file_name = generate_tsv_file(label, properties)

    prepare_node_cypher_query(file_name, label, properties, list_properties)


def generates_rela_tsv_file_and_cypher(label_from, label, properties, rela_name, list_properties):
    """
    Generate the tsv file for rela. Also add cypher query to cypher file.
    :param label: string
    :param properties: list
    :param rela_name: string
    :param list_properties:  list
    :return:
    """
    file_name = generate_tsv_file(label_from + '_' + label, properties)

    prepare_edge_cypher_query(file_name, label_from, label, rela_name, properties, list_properties)


# dictionary pathway to pathway
dict_pathway_to_pathway_info = {}

# dictionary disease to name
dict_disease_id_to_name = {}

# dictionary protein- metabolite to rela info
dict_protein_metabolite_to_rela_info = {}

# dictionary go classifier category to go id/description to description
dict_go_classifier_to_id_to_description = {}

# dictionary ontology to ontology info
dict_ontology_id_to_ontology_info = {}

# set of ontology_tuples
set_of_ontologies_tuples = set()


def get_pathway_information(node):
    """
    extract pathway information from xml node and return identifier
    :param node: xml pathway node
    :return: string identifier
    """
    pathway_name = node.findtext('{ns}name'.format(ns=ns))
    pathway_smpdb_id = node.findtext('{ns}smpdb_id'.format(ns=ns))
    pathway_kegg_map_id = node.findtext('{ns}kegg_map_id'.format(ns=ns))
    dict_pathway = {'name': pathway_name, 'smpdb_id': pathway_smpdb_id,
                    'kegg_map_id': pathway_kegg_map_id}
    if pathway_kegg_map_id and pathway_smpdb_id:
        pathway_identifier = pathway_kegg_map_id
        if pathway_kegg_map_id not in dict_pathway_to_pathway_info:
            dict_pathway_to_pathway_info[pathway_kegg_map_id] = dict_pathway
    elif pathway_kegg_map_id:
        pathway_identifier = pathway_kegg_map_id
        if pathway_kegg_map_id not in dict_pathway_to_pathway_info:
            dict_pathway_to_pathway_info[pathway_kegg_map_id] = dict_pathway
    elif pathway_smpdb_id:
        pathway_identifier = pathway_smpdb_id
        if pathway_smpdb_id not in dict_pathway_to_pathway_info:
            dict_pathway_to_pathway_info[pathway_smpdb_id] = dict_pathway
    else:
        pathway_identifier = pathway_name
        if pathway_name not in dict_pathway_to_pathway_info:
            dict_pathway_to_pathway_info[pathway_name] = dict_pathway
    return pathway_identifier


def prepare_reference(reference):
    """
    extract reference information from refernce node and add to dictionary.
    :param reference: reference xml node
    :return: dictionary
    """
    dict_reference = {}
    for reference_info in reference.iterchildren():
        reference_info_tag = reference_info.tag.replace(ns, '')
        if  reference_info.text is None:
            continue
        dict_reference[reference_info_tag] = reference_info.text.replace('"','\'')
    return dict_reference


def prepare_references(references):
    """
    Prepare references properties into a list of dictionaries.
    :param references: node references
    :return: list of dictionary
    """
    list_references = []
    for reference in references.iterchildren():
        dict_reference = prepare_reference(reference)
        list_references.append(dict_reference)
    return list_references


def prepare_cypher_files_and_tsv():
    generates_node_tsv_file_and_cypher('pathway', ['identifier', 'name', 'smpdb_id', 'kegg_map_id'], [])
    generates_node_tsv_file_and_cypher('protein',
                                       ['identifier', 'creation_date', 'version', 'gene_name', 'protein_type',
                                        'update_date', 'xrefs', "uniprot_name", "general_function", "specific_function",
                                        'secondary_accessions', 'synonyms', 'pdb_ids',
                                        'gene_properties_chromosome_location', 'gene_properties_gene_sequence',
                                        'gene_properties_locus', 'protein_properties_theoretical_pi',
                                        'protein_properties_molecular_weight',
                                        'protein_properties_polypeptide_sequence', 'protein_properties_residue_number',
                                        'protein_properties_pfams_id_name', 'protein_properties_transmembrane_regions',
                                        'protein_properties_signal_regions', 'subcellular_locations',
                                        'general_references'],
                                       ['xrefs', 'synonyms', 'secondary_accessions', 'pdb_ids',
                                        'protein_properties_pfams_id_name', 'protein_properties_transmembrane_regions',
                                        'protein_properties_signal_regions', 'subcellular_locations',
                                        'general_references'])
    generates_node_tsv_file_and_cypher('ontology',
                                       ['identifier', 'term', 'definition', 'level', 'synonyms', 'parent_id'],
                                       ['synonyms'])
    generates_node_tsv_file_and_cypher('disease', ['identifier', 'name'], [])
    generates_node_tsv_file_and_cypher('metabolite',
                                       ['identifier', 'creation_date', 'version', 'traditional_iupac',
                                        'monisotopic_molecular_weight', 'inchi', 'description', 'iupac_name',
                                        'synthesis_reference', 'inchikey', 'cas_registry_number',
                                        'average_molecular_weight', 'status', 'state', 'name', 'chemical_formula',
                                        'update_date', 'xrefs', 'smiles', 'taxonomy_direct_parent',
                                        'secondary_accessions', 'taxonomy_alternative_parents', 'synonyms',
                                        'taxonomy_sub_class', 'taxonomy_substituents', 'taxonomy_kingdom',
                                        'taxonomy_class', 'taxonomy_description', 'taxonomy_external_descriptors',
                                        'taxonomy_molecular_framework', 'taxonomy_super_class',
                                        'experimental_properties', "predicted_properties", 'spectra',
                                        'biospecimen_locations', 'cellular_locations', 'tissue_locations',
                                        'general_references'],
                                       ['xrefs', 'synonyms', 'taxonomy_alternative_parents', 'taxonomy_substituents',
                                        'taxonomy_external_descriptors', 'experimental_properties',
                                        "predicted_properties", 'spectra', 'biospecimen_locations',
                                        'cellular_locations', 'tissue_locations', 'general_references',
                                        'secondary_accessions'])

    generates_rela_tsv_file_and_cypher('metabolite', 'pathway', ['metabolite_id', 'pathway_id'], 'associates', [])
    generates_rela_tsv_file_and_cypher('metabolite', 'disease', ['metabolite_id', 'disease_id', 'references'],
                                       'associates', ['references'])
    generates_rela_tsv_file_and_cypher('metabolite', 'ontology', ['metabolite_id', 'identifier'], 'associates', [])
    generates_rela_tsv_file_and_cypher('protein', 'pathway', ['protein_id', 'pathway_id'], 'associates', [])
    generates_rela_tsv_file_and_cypher('protein', 'metabolite', ['protein_id', 'metabolite_id', 'references'],
                                       'associates', ['references'])
    generates_rela_tsv_file_and_cypher('ontology', 'ontology', ['ontology_id1', 'ontology_id2'], 'associates', [])

# to avoid double edges without information
set_protein_pathway=set()

def run_trough_xml_and_parse_data_protein():
    # counter of human entries
    counter_human = 0

    # set_of_protein_properties
    set_of_protein_propertie = set()

    # download file
    # download url of swissprot

    if not os.path.exists('database/hmdb_proteins.zip'):
        print('download')
        url_path = 'https://hmdb.ca/system/downloads/current/hmdb_proteins.zip'
        # download ncbi human genes
        filename = wget.download(url_path, out='database/')
    else:
        filename = 'database/hmdb_proteins.zip'

    with ZipFile(filename) as z:
        with z.open("hmdb_proteins.xml") as file:
            # file= unzip_file.read("hmdb_proteins.xml")
            # file = open("database/hmdb_proteins.xml", "rb")

            subtags = set()

            # go through the entries in uniprot xml
            for event, node in etree.iterparse(file, events=('end',), tag="{ns}protein".format(ns=ns)):

                # dictionary of protein information
                dict_protein = {}

                # the identifier
                identifier = ''

                for child in node.iterchildren():

                    # print(child)

                    tag = child.tag.replace(ns, '')
                    # the attributes
                    attributes = child.attrib

                    if len(child):
                        if tag in ['secondary_accessions', 'synonyms', 'pdb_ids', 'subcellular_locations']:
                            for subchild in child.iterchildren():
                                subchild_tag = subchild.tag.replace(ns, '')
                                # print('subchild')
                                # print("%s - %s - %s" % (subchild_tag, subchild.text, subchild.attrib))
                                add_key_value_to_dictionary_as_list(dict_protein, tag, subchild.text)
                        elif tag in ['gene_properties', 'protein_properties']:
                            for subchild in child.iterchildren():
                                subchild_tag = subchild.tag.replace(ns, '')
                                if len(subchild):
                                    subchild_text = subchild.text.strip()
                                    if subchild_tag == 'pfams' and len(subchild):
                                        for subsubchild in subchild.iterchildren():
                                            pfam_id = subsubchild.findtext('{ns}pfam_id'.format(ns=ns))
                                            pfam_name = subsubchild.findtext('{ns}name'.format(ns=ns))
                                            add_key_value_to_dictionary_as_list(dict_protein,
                                                                                tag + '_' + subchild_tag + '_id_name',
                                                                                pfam_id + ':' + pfam_name)
                                    elif subchild_tag in ['transmembrane_regions', 'signal_regions']:
                                        if len(subchild):
                                            for region in subchild.findall('{ns}region'.format(ns=ns)):
                                                region_text = region.text
                                                if not region_text in ['[]', 'None']:
                                                    add_key_value_to_dictionary_as_list(dict_protein,
                                                                                        tag + '_' + subchild_tag,
                                                                                        region_text)
                                    else:
                                        if len(subchild):
                                            # print(subchild_tag)
                                            for subsubchild in subchild.iterchildren():
                                                subsubchild_tag = subsubchild.tag.replace(ns, '')
                                                # subtags.add(subsubchild_tag)
                                                print("%s - %s - %s" % (
                                                subsubchild_tag, subsubchild.text, subsubchild.attrib))
                                                print(len(subsubchild))
                                                print(identifier)
                                                sys.exit('ohno protein or gene properties')
                                    # if len(subchild_text)>0 or len(subchild.attrib)>0:
                                    #     print('ohje')
                                    #     print(subchild_tag)
                                    #     print(len(subchild.text))
                                    #     print("%s - %s - %s" % (subchild_tag, subchild.text, subchild.attrib))
                                else:
                                    dict_protein[tag + '_' + subchild_tag] = subchild.text
                        elif tag == 'pathways':
                            for subchild in child.iterchildren():
                                pathway_identifier = get_pathway_information(subchild)
                                if not (identifier, pathway_identifier) in set_protein_pathway:
                                    dict_node_type_to_tsv['protein_pathway'].writerow(
                                        {'protein_id': identifier, 'pathway_id': pathway_identifier})
                                    set_protein_pathway.add((identifier,pathway_identifier))

                        elif tag == 'metabolite_associations':
                            for subchild in child.iterchildren():
                                metabolite_name = subchild.findtext('{ns}name'.format(ns=ns))
                                metabolit_accession = subchild.findtext('{ns}accession'.format(ns=ns))
                                dict_protein_metabolite_to_rela_info[(identifier, metabolit_accession)] = []
                                if not metabolit_accession:
                                    print('ohgot this metabolite has no id:', metabolite_name)
                                    sys.exit('metabolite-protein')

                        elif tag == 'go_classifications':
                            for subchild in child.iterchildren():
                                go_category = subchild.findtext('{ns}category'.format(ns=ns))
                                go_id = subchild.findtext('{ns}go_id'.format(ns=ns))
                                go_description = subchild.findtext('{ns}description'.format(ns=ns))
                                go_label = go_category.replace(' ', '')
                                if go_label not in dict_go_classifier_to_id_to_description:
                                    generates_node_tsv_file_and_cypher(go_label, ['identifier', 'description'], [])
                                    generates_rela_tsv_file_and_cypher('protein', go_label,
                                                                       ['protein_id', 'identifier'],
                                                                       'associates', [])
                                    dict_go_classifier_to_id_to_description[go_label] = {}
                                if go_id:
                                    go_identifier = go_id
                                else:
                                    go_identifier = go_description
                                dict_node_type_to_tsv['protein_' + go_label].writerow(
                                    {'protein_id': identifier, 'identifier': go_identifier})
                                if not go_identifier in dict_go_classifier_to_id_to_description[go_label]:
                                    dict_go_classifier_to_id_to_description[go_label][go_identifier] = go_description

                        elif tag == 'general_references':
                            list_references = prepare_references(child)
                            dict_protein[tag] = list_references
                        elif tag == 'metabolite_references':
                            for subchild in child.iterchildren():
                                metabolite = subchild.find('{ns}metabolite'.format(ns=ns))
                                reference = subchild.find('{ns}reference'.format(ns=ns))
                                metabolite_accession = metabolite.findtext('{ns}accession'.format(ns=ns))
                                dict_reference = prepare_reference(reference)
                                if (identifier, metabolite_accession) not in dict_protein_metabolite_to_rela_info:
                                    dict_protein_metabolite_to_rela_info[identifier, metabolite_accession] = []
                                # print(dict_reference)
                                dict_protein_metabolite_to_rela_info[identifier, metabolite_accession].append(
                                    dict_reference)

                        else:
                            print("%s - %s - %s" % (tag, child.text, child.attrib))
                            sys.exit('with child protein problem')
                    else:
                        if tag in ["version", "creation_date", "update_date", "protein_type", "gene_name",
                                   "uniprot_name",
                                   "general_function", "specific_function"]:
                            dict_protein[tag] = child.text
                        elif tag in ["hgnc_id", "geneatlas_id", "genbank_gene_id", "genecard_id", "genbank_protein_id",
                                     "uniprot_id"]:
                            if not child.text is None:
                                add_key_value_to_dictionary_as_list(dict_protein, 'xrefs', tag + ':' + child.text)
                        elif tag == 'accession':
                            identifier = child.text
                            dict_protein['identifier'] = identifier
                        # tags from tags with childs but no childs are there
                        elif tag in ["pdb_ids", "metabolite_references", "go_classifications", "pathways", "synonyms",
                                     "subcellular_locations", "metabolite_associations", "general_references",
                                     "secondary_accessions"]:
                            continue
                        else:
                            print('not')
                            print("%s - %s - %s" % (tag, child.text, child.attrib))
                            sys.exit()
                # print(dict_protein)
                # print('This is the identifier:', identifier)
                # prepare name
                # dict_protein['synonyms'] = dict_protein['name']
                # dict_protein['name'] = dict_protein['protein_name'][0]
                # dict_protein['synonyms'].extend(dict_protein['protein_name'][1:])
                # del dict_protein['protein_name']

                set_of_protein_propertie = set_of_protein_propertie.union(dict_protein.keys())
                dict_protein = prepare_tsv_dictionary(dict_protein)
                # print(dict_protein)
                dict_node_type_to_tsv['protein'].writerow(dict_protein)
                node.clear()

                # if counter_human > 1500:
                #     break
    print('set of protein properties')
    print(set_of_protein_propertie)
    print("number of human proteins:", counter_human)
    print('pfams tags', subtags)


def go_trough_ontology_and_write_information(descendant, parent_node_id, node_id):
    """
    Prepare node information then if not add already add to dictionary.Write parent child relationship into file.
    Depending on the type a relationship to metabolite is generated or more descendates are there.
    :param descendant:
    :param parent_node_id:
    :param node_id:
    :return:
    """
    # get ontology node information
    name = descendant.findtext('{ns}term'.format(ns=ns)).strip()
    definition = descendant.findtext('{ns}definition'.format(ns=ns))
    level = descendant.findtext('{ns}level'.format(ns=ns))
    parent_id = descendant.findtext('{ns}parent_id'.format(ns=ns))
    synonyms = []
    ontology_synonyms = descendant.find('{ns}synonyms'.format(ns=ns))
    for synonym in ontology_synonyms.iterchildren():
        synonyms.append(synonym.text)
    dict_node = {'identifier': name, 'term': name,
                 'definition': definition, 'level': level,
                 'parent_id': parent_id, 'synonyms': synonyms}
    # det ontology id
    ontology_id = name

    # add ontology info to dictionary if not exists
    if ontology_id not in dict_ontology_id_to_ontology_info:
        dict_ontology_id_to_ontology_info[ontology_id] = dict_node
        # print(dict_node)
        dict_node = prepare_tsv_dictionary(dict_node)
        dict_node_type_to_tsv['ontology'].writerow(dict_node)

    # add parent child relationship
    if (parent_node_id, ontology_id) not in set_of_ontologies_tuples:
        dict_node_type_to_tsv['ontology_ontology'].writerow(
            {'ontology_id1': parent_node_id, 'ontology_id2': ontology_id})
        set_of_ontologies_tuples.add((parent_node_id, ontology_id))

    # get type of ontology node for metabolite child is connected to metabolite, parent is only ontology
    ontology_type = descendant.findtext('{ns}type'.format(ns=ns))
    if ontology_type == 'parent':
        descendants = descendant.find('{ns}descendants'.format(ns=ns))
        for child in descendants.iterchildren():
            go_trough_ontology_and_write_information(child, ontology_id, node_id)
    else:
        dict_node_type_to_tsv['metabolite_ontology'].writerow({'metabolite_id': node_id, 'identifier': ontology_id})


def run_trough_xml_and_parse_data_metabolite():
    # set_of_metabolite_properties
    set_of_metabolite_properties = set()

    if not os.path.exists('database/hmdb_metabolites.zip'):
        print('download')
        url_path = 'https://hmdb.ca/system/downloads/current/hmdb_metabolites.zip'
        # download ncbi human genes
        filename = wget.download(url_path, out='database/')
    else:
        filename = 'database/hmdb_metabolites.zip'

    with ZipFile(filename) as z:
        with z.open("hmdb_metabolites.xml") as file:

            # go through the entries in xml
            for event, node in etree.iterparse(file, events=('end',), tag="{ns}metabolite".format(ns=ns)):

                # dictionary of protein information
                dict_node = {}

                # the identifier
                identifier = ''

                for child in node.iterchildren():

                    tag = child.tag.replace(ns, '')

                    if len(child):
                        if tag in ['secondary_accessions', 'synonyms']:
                            for subchild in child.iterchildren():
                                add_key_value_to_dictionary_as_list(dict_node, tag, subchild.text)
                        elif tag == 'taxonomy':
                            for subchild in child.iterchildren():
                                subchild_tag = subchild.tag.replace(ns, '')
                                if len(subchild):
                                    list_elements = []
                                    for subsubchild in subchild.iterchildren():
                                        list_elements.append(subsubchild.text)
                                    dict_node[tag + '_' + subchild_tag] = list_elements
                                else:
                                    dict_node[tag + '_' + subchild_tag] = subchild.text
                        elif tag == 'ontology':
                            for root in child.iterchildren():
                                ontology_name = root.findtext('{ns}term'.format(ns=ns)).strip()
                                ontology_definition = root.findtext('{ns}definition'.format(ns=ns))
                                ontology_level = root.findtext('{ns}level'.format(ns=ns))
                                ontology_parent_id = root.findtext('{ns}parent_id'.format(ns=ns))
                                dict_head = {'identifier': ontology_name, 'term': ontology_name,
                                             'definition': ontology_definition, 'level': ontology_level,
                                             'parent_id': ontology_parent_id}
                                ontology_id = ontology_name
                                if ontology_id not in dict_ontology_id_to_ontology_info:
                                    dict_ontology_id_to_ontology_info[ontology_id] = dict_head
                                    # print(dict_head)
                                    dict_head = prepare_tsv_dictionary(dict_head)
                                    dict_node_type_to_tsv['ontology'].writerow(dict_head)
                                ontology_type = root.findtext('{ns}type'.format(ns=ns))
                                if ontology_type == 'parent':
                                    descendants = root.find('{ns}descendants'.format(ns=ns))
                                    for descendant in descendants.iterchildren():
                                        go_trough_ontology_and_write_information(descendant, ontology_id, identifier)
                                else:
                                    dict_node_type_to_tsv['metabolite_ontology'].writerow(
                                        {'metabolite_id': identifier, 'identifier': ontology_id})


                        elif tag in ['experimental_properties', "predicted_properties", 'spectra']:
                            list_properties = []
                            for subchild in child.iterchildren():
                                dict_property = {}
                                for subsubchild in subchild.iterchildren():
                                    subsubchild_tag = subsubchild.tag.replace(ns, '')
                                    dict_property[subsubchild_tag] = subsubchild.text
                                list_properties.append(dict_property)
                            dict_node[tag] = list_properties
                        elif tag == 'biological_properties':
                            for subchild in child.iterchildren():
                                subchild_tag = subchild.tag.replace(ns, '')
                                list_of_props = []
                                for subsubchild in subchild.iterchildren():
                                    subsubchild_tag = subsubchild.tag.replace(ns, '')
                                    if subsubchild_tag != 'pathway':
                                        list_of_props.append(subsubchild.text)
                                    else:
                                        pathway_identifier = get_pathway_information(subsubchild)
                                        dict_node_type_to_tsv['metabolite_pathway'].writerow(
                                            {'metabolite_id': identifier, 'pathway_id': pathway_identifier})
                                if subchild_tag != 'pathways':
                                    dict_node[subchild_tag] = list_of_props
                        elif tag in ['normal_concentrations', 'abnormal_concentrations']:
                            list_of_concentrations = []
                            for subchild in child.iterchildren():
                                subchild_tag = subchild.tag.replace(ns, '')
                                if subchild_tag != 'concentration':
                                    sys.exit('concentration has other child then concentration :O')
                                dict_concentration = {}
                                for subsubchild in subchild.iterchildren():
                                    subsubchild_tag = subsubchild.tag.replace(ns, '')
                                    if subsubchild_tag != 'references':
                                        dict_concentration[subsubchild_tag] = subsubchild.text
                                    else:
                                        list_references = prepare_references(subsubchild)
                                        dict_concentration[subsubchild_tag] = list_references

                                list_of_concentrations.append(dict_concentration)
                            dict_property[tag] = list_of_concentrations
                        elif tag == 'diseases':
                            for subchild in child.iterchildren():
                                disease_name = subchild.findtext('{ns}name'.format(ns=ns)).strip()
                                disease_omim_id = subchild.findtext('{ns}omim_id'.format(ns=ns))
                                references = subchild.find('{ns}references'.format(ns=ns))
                                list_references = []
                                for reference in references.iterchildren():
                                    dict_reference = prepare_reference(reference)
                                    list_references.append(dict_reference)

                                disease_id = disease_omim_id if disease_omim_id else disease_name
                                if disease_id not in dict_disease_id_to_name:
                                    dict_disease_id_to_name[disease_id] = disease_name
                                    dict_node_type_to_tsv['disease'].writerow(
                                        {'identifier': disease_id, 'name': disease_name})

                                dict_rela = {'metabolite_id': identifier, 'disease_id': disease_id,
                                             'references': list_references}
                                dict_rela = prepare_tsv_dictionary(dict_rela)
                                dict_node_type_to_tsv['metabolite_disease'].writerow(dict_rela)
                        elif tag == 'general_references':
                            list_references = prepare_references(child)
                            dict_concentration[tag] = list_references
                        elif tag == 'protein_associations':
                            for protein in child.iterchildren():
                                protein_accession = protein.findtext('{ns}protein_accession'.format(ns=ns))
                                if (protein_accession, identifier) not in dict_protein_metabolite_to_rela_info:
                                    dict_protein_metabolite_to_rela_info[(protein_accession, identifier)] = []
                        else:
                            print("%s - %s - %s" % (tag, child.text, child.attrib))
                            sys.exit('with child metabolite problem')
                    else:
                        if tag in ["version", "creation_date", "update_date", "status", "name", "description",
                                   "chemical_formula", "average_molecular_weight", "monisotopic_molecular_weight",
                                   "iupac_name",
                                   "traditional_iupac", "cas_registry_number", "smiles", "inchi", "inchikey", "state",
                                   "synthesis_reference"]:
                            dict_node[tag] = child.text
                        elif tag in ["kegg_id", "chemspider_id", "foodb_id", "drugbank_id", "pubchem_compound_id",
                                     "chebi_id",
                                     "pdb_id", "knapsack_id", "wikipedia_id", "biocyc_id",
                                     "phenol_explorer_compound_id",
                                     "bigg_id", "metlin_id", "vmh_id", "fbonto_id"]:
                            if not child.text is None:
                                add_key_value_to_dictionary_as_list(dict_node, 'xrefs', tag + ':' + child.text)
                        elif tag == 'accession':
                            identifier = child.text
                            dict_node['identifier'] = identifier
                        # tags from tags with childs but no childs are there
                        elif tag in ["experimental_properties", "spectra", "diseases", "normal_concentrations",
                                     "protein_associations", "abnormal_concentrations", "ontology",
                                     "general_references",
                                     "synonyms", "taxonomy", "secondary_accessions"]:
                            continue
                        else:
                            print('not')
                            print("%s - %s - %s" % (tag, child.text, child.attrib))
                            print(identifier)
                            sys.exit()

                set_of_metabolite_properties = set_of_metabolite_properties.union(dict_node.keys())
                dict_node = prepare_tsv_dictionary(dict_node)
                # print(dict_node)
                dict_node_type_to_tsv['metabolite'].writerow(dict_node)
                node.clear()


def write_pathways_into_csv_file():
    """
    Add information into csv file.
    :return:
    """
    for identifier, dict_pathway in dict_pathway_to_pathway_info.items():
        dict_pathway['identifier'] = identifier
        dict_node_type_to_tsv['pathway'].writerow(dict_pathway)


def write_go_information_into_csv_files():
    """
    Add information into csv file.
    :return:
    """
    for label, dict_id_to_description in dict_go_classifier_to_id_to_description.items():
        for identifier, description in dict_id_to_description.items():
            dict_go = {'identifier': identifier, 'description': description}
            dict_node_type_to_tsv[label].writerow(dict_go)


def write_protein_metabolite_rela_into_csv():
    """
    Write rela information after preparation into csv file.
    :return: 
    """
    for (protein_id, metabolite_id), list_references in dict_protein_metabolite_to_rela_info.items():
        dict_rela = {'protein_id': protein_id, 'metabolite_id': metabolite_id, 'references': list_references}
        dict_rela = prepare_tsv_dictionary(dict_rela)
        dict_node_type_to_tsv['protein_metabolite'].writerow(dict_rela)


def main():
    global path_of_directory
    # path to project dictionary
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print('#############################################################')
    print(datetime.datetime.utcnow())
    print('prepare cypherfile and tsv files ')

    prepare_cypher_files_and_tsv()

    print('#############################################################')
    print(datetime.datetime.utcnow())
    print('parse xml data protein ')

    run_trough_xml_and_parse_data_protein()

    print('#############################################################')
    print(datetime.datetime.utcnow())
    print('parse xml data metabolite ')

    run_trough_xml_and_parse_data_metabolite()

    print('#############################################################')
    print(datetime.datetime.utcnow())
    print('generate pathway ')

    write_pathways_into_csv_file()

    print('#############################################################')
    print(datetime.datetime.utcnow())
    print('generate go ')

    write_go_information_into_csv_files()

    print('#############################################################')
    print(datetime.datetime.utcnow())
    print('write protein-metabolite pairs into tsv file')

    write_protein_metabolite_rela_into_csv()

    print('#############################################################')
    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
