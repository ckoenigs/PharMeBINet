import os
import csv, json
import datetime
import sys
import wget
import gzip
import lxml.etree as etree

sys.path.append("../..")
import pharmebinetutils

ns = '{http://uniprot.org/uniprot}'

# dictionary keywords
dict_keyword = {}

# set of disease
set_of_disease_ids = set()

# dictionary protein-disease ids to rela info
dict_protein_disease_pair = {}

# set of keyword_id and protein id
set_keyword_protein_pairs = set()

# set evidence
set_evidence = set()

# dict of evidence and protein id
dict_evidence_protein_pairs_to_info = {}

# dictionary uniprot accession to  set of uniprot identifiers
dict_up_accession_to_uniprot_id = {}

# list of interactions
list_of_interactions = []


def combine_xrefs(attributes):
    """
    combine source and id to one string
    :param attributes: kind of dict
    :return:
    """
    return attributes['type'] + ':' + attributes['id']


def add_to_dict_with_set(dictionary, key, attributes):
    """
    Add information to dictionary to set.
    :param dictionary: dictionary
    :param key: string
    :param attributes: kind of dictionary
    :return:
    """
    if key not in dictionary:
        dictionary[key] = set()
    dictionary[key].add(combine_xrefs(attributes))


def prepare_dbReference(dict_protein, attributes):
    """
    add refference to dictionary
    :param dict_protein:
    :param attributes:
    :return:
    """
    if not 'xrefs' in dict_protein:
        dict_protein['xrefs'] = set()
    att_type = attributes['type']
    if att_type in ['Pfam', 'GeneID']:
        if att_type == 'Pfam':
            add_to_dict_with_set(dict_protein, 'pfam', attributes)
        else:
            add_to_dict_with_set(dict_protein, 'gene_id', attributes)
        return
    if att_type in ['GO', 'Proteomes']:
        if att_type == 'GO':
            add_to_dict_with_set(dict_protein, 'go_classifiers', attributes)
            return
        else:
            add_to_dict_with_set(dict_protein, 'chromosome_location', attributes)
    dict_protein['xrefs'].add(combine_xrefs(attributes))
    evidence = attributes['evidence'] if 'evidence' in attributes else ''


# set of empty properties
set_of_empty_properties = set()


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
                if key not in set_of_empty_properties:
                    print('empty values')
                    print(key, value)
                    set_of_empty_properties.add(key)
                continue
            if type(value[0]) != str:
                value = [json.dumps(x) for x in value]
            value = "||".join(value)
        elif type(value) == dict:
            value = json.dumps(value)
        value = value.replace('\\"', '"')
        new_dictionary[key] = value
    return new_dictionary


def prepare_evidence(attrib, protein_id, parent=None):
    """
    Prepare evidence nodes and relationships. Some contains relationship information
    :param attrib: kind of dict
    :param protein_id: string
    :param parent: a xml node
    :return:
    """
    evidence_id = attrib['type']
    evidence_key = attrib['key']

    if evidence_id not in set_evidence:
        if 'evidence' not in dict_node_type_to_tsv:
            generates_node_tsv_file_and_cypher('evidence', ['id'], [])
            generates_rela_tsv_file_and_cypher('evidence',
                                               ['uniprot_id', 'evidence_id', 'sources', 'importedFrom', 'key'],
                                               'part_of',
                                               ['sources', 'importedFrom'])

        dict_node_type_to_tsv['evidence'].writerow({'id': evidence_id})
    set_evidence.add(evidence_id)

    if not (evidence_id, protein_id) in dict_evidence_protein_pairs_to_info:
        dict_evidence_protein_pairs_to_info[(evidence_id, protein_id)] = {}

    dict_pair = {'uniprot_id': protein_id, 'evidence_id': evidence_id, 'key': evidence_key}
    if parent is not None:
        for child in parent.iterchildren():
            tag = child.tag.replace(ns, '')
            if tag == 'source':
                tag = 'sources'
            if tag not in dict_pair:
                dict_pair[tag] = set()
            for dbRefs in child.iterchildren():
                db_ref_tag = dbRefs.tag.replace(ns, '')
                if db_ref_tag != 'dbReference':
                    sys.exit('evidence has not df Ref')
                dict_pair[tag].add(combine_xrefs(dbRefs.attrib))
            if len(child.attrib) > 0:
                dict_pair[tag].add('ref:' + child.attrib['ref'])
    for key, value in dict_pair.items():
        if type(value) in [set, list]:
            dict_pair[key] = '||'.join(value)
    dict_node_type_to_tsv['protein_evidence'].writerow(dict_pair)


def preparation_gene_location(dictionary, attributes, node=None):
    """
    Prepare the gene location information into a list of strings.
    :param dictionary: dictionary
    :param attributes: kind of dict
    :param node: xml node
    :return:
    """
    if 'gene_location' not in dictionary:
        dictionary['gene_location'] = set()
    type = attributes['type']
    evidence = attributes['evidence'] if 'evidence' in attributes else ''

    list_of_names = []
    if node is not None:
        for child in node.iterchildren():
            child_att = child.attrib
            name = ''
            if 'status' in child_att:
                name += child_att['status']
            name += ' ' + child.text
            list_of_names.append(name.strip())
    type += ' ' + '; '.join(list_of_names)
    dictionary['gene_location'].add(type.strip())


def add_name_or_ec_to_list_from_protein(node, dict_protein):
    """
    Add the name to the list of names and the ec to a ec-list.
    :param node: xml leaf
    :param dict_protein: dictionary
    :return:
    """
    subsub_tag = node.tag.replace(ns, '')
    evidence_protein_name = node.attrib['evidence'] if 'evidence' in node else ''
    if subsub_tag != 'ecNumber':
        dict_protein['protein_name'].append(node.text)
    else:
        if 'ec_number' not in dict_protein:
            dict_protein['ec_number'] = set()
        dict_protein['ec_number'].add(node.text)


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


def preparation_of_location_type(node, dictionary):
    """
    prepare location tag  and add into dictionary
    :param node: xml element
    :param dictionary: dictionary
    :return:
    """
    if len(node.attrib) > 0:
        for key, value in dict(node.attrib).items():
            dictionary[key] = value
    for subnode in node.iterchildren():
        subsub_tag = subnode.tag.replace(ns, '')
        text = ''
        subnode_attributes = subnode.attrib
        if 'status' in subnode_attributes:
            text += subnode_attributes['status']
        if 'position' in subnode_attributes:
            text += ' ' + subnode_attributes['position']
        subnode_evidence = subnode_attributes[
            'evidence'] if 'evidence' in subnode_attributes else ''
        dictionary[subsub_tag] = text.strip()


def run_trough_xml_and_parse_data():
    # counter of human entries
    counter_human = 0

    # set_of_protein_properties
    set_of_protein_propertie = set()

    generates_node_tsv_file_and_cypher('protein',
                                       ['identifier', 'polymorphism', 'developmental_stage', 'synonyms', 'name',
                                        'xrefs_with_infos', 'mass', 'RNA_editing', 'pathway', 'xrefs', 'entry_name',
                                        'tissue_specificity', 'gene_name', 'protein_existence', 'domain',
                                        'miscellaneous', 'catalytic_activity', 'as_sequence', 'sequenceLength',
                                        'online_information', 'function', 'activity_regulation', 'caution', 'subunit',
                                        'alternative_products', 'biophysicochemical_properties',
                                        'subcellular_locations',
                                        'PTM', 'mass_spectrometry', 'similarity', 'biotechnology', 'sequence_caution',
                                        'ec_number', 'accession', 'cofactor', 'references', 'feature', 'pharmaceutical',
                                        'induction', 'disease', 'gene_id', 'go_classifiers', 'chromosome_location',
                                        'pfam', 'gene_location', 'molecule', 'allergen', 'fragment'],
                                       ['xrefs', 'synonyms', 'xrefs_with_infos', 'RNA_editing', 'pathway',
                                        'tissue_specificity', 'gene_name', 'domain', 'miscellaneous',
                                        'catalytic_activity', 'online_information', 'function', 'activity_regulation',
                                        'caution', 'subunit', 'alternative_products', 'biophysicochemical_properties',
                                        'subcellular_locations', 'ec_number', 'accession', 'cofactor', 'references',
                                        'feature', 'pharmaceutical', 'induction', 'disease', 'gene_id',
                                        'go_classifiers', 'chromosome_location', 'pfam', 'gene_location', 'molecule',
                                        'allergen', 'mass_spectrometry', 'sequence_caution'])

    # download file
    # download url of swissprot

    if not os.path.exists('database/uniprot_sprot_human.xml.gz'):
        print('download')
        # url_path = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.xml.gz'
        # url_data = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz'
        url_path = 'ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/taxonomic_divisions/uniprot_sprot_human.xml.gz'
        # download ncbi human genes
        filename = wget.download(url_path, out='database/')
    else:
        filename = 'database/uniprot_sprot_human.xml.gz'

    # filename_without_gz = filename.rsplit('.', 1)[0]
    # file = io.TextIOWrapper(gzip.open(filename, 'rb'))
    file = gzip.open(filename, 'rb')

    # open xml file
    # file = open('test.xml', 'rb')
    # file = open(filename, 'rb')

    # go through the entries in uniprot xml
    for event, node in etree.iterparse(file, events=('end',), tag="{ns}entry".format(ns=ns)):

        # check if this is a human entry
        organism = node.find("{ns}organism".format(ns=ns))
        df_references = organism.findall("{ns}dbReference".format(ns=ns))

        has_ncbi_tax_id = False
        is_human = False
        for df_ref in df_references:
            df_ref_attributes = df_ref.attrib
            if "NCBI Taxonomy" == df_ref_attributes["type"]:
                has_ncbi_tax_id = True
                if df_ref_attributes["id"] == '9606':
                    is_human = True

        # check if at least one one ncbi tax entry
        if not has_ncbi_tax_id:
            sys.exit("a protein without a organism with ncbi tax")
        #  continue if it is not a human
        if not is_human:
            node.clear()
            continue

        counter_human += 1

        # dictionary of protein information
        dict_protein = {}

        # the identifier
        identifier = ''

        # accession first
        first_accession = True

        for child in node.iterchildren():

            tag = child.tag.replace(ns, '')
            # the attributes
            attributes = child.attrib

            if len(child):
                # print('has child')
                # print("%s - %s - %s" % (tag, child.text, child.attrib))
                # prepare the dbRefs with child to xrefs and into xrefs with additional info
                if tag == 'dbReference':
                    prepare_dbReference(dict_protein, attributes)
                    dict_xref = {'id': attributes['type'] + ':' + attributes['id']}
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag == 'property':
                            dict_xref[subchild.attrib['type']] = subchild.attrib['value']
                        else:
                            # print(dict_protein)
                            # print("%s - %s - %s" % (sub_tag, subchild.text, subchild.attrib))
                            dict_xref[sub_tag + '_id'] = subchild.attrib['id']
                            if subchild.text is not None:
                                sys.exit('molecule dbRef has text')
                            # print("molecular in dbRef")

                    if 'xrefs_with_infos' not in dict_protein:
                        dict_protein['xrefs_with_infos'] = []
                    dict_protein['xrefs_with_infos'].append(dict_xref)
                # evidence of the protein
                elif tag == 'evidence':
                    prepare_evidence(attributes, identifier, child)
                # different kind of features like mutation version/ regions/...
                elif tag == 'feature':

                    if tag not in dict_protein:
                        dict_protein[tag] = []
                    dict_feature = dict(attributes)
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag == 'original':
                            dict_feature[sub_tag] = subchild.text
                        elif sub_tag == 'variation':
                            add_key_value_to_dictionary_as_list(dict_feature, sub_tag, subchild.text)
                        # location
                        else:
                            preparation_of_location_type(subchild, dict_feature)
                    dict_protein[tag].append(dict_feature)
                # name of the gene
                elif tag == 'gene':
                    if 'gene_name' not in dict_protein:
                        dict_protein['gene_name'] = set()
                    for subchild in child.iterchildren():
                        subchild_type = subchild.attrib['type']
                        subchild_evidence = subchild.attrib['evidence'] if 'evidence' in subchild.attrib else ''
                        dict_protein['gene_name'].add(subchild_type + ':' + subchild.text)
                # location of the gene
                elif tag == 'geneLocation':
                    preparation_gene_location(dict_protein, attributes, child)

                # is already human
                elif tag == 'organism':
                    continue
                # protein contains name and ec-codes
                elif tag == 'protein':
                    dict_protein['protein_name'] = []
                    # dict_protein['ec_number']=set()
                    for subchild in child.iterchildren():
                        for subsubchild in subchild.iterchildren():
                            # fullname/alternativeName/submittedName/allergenName/biotechName/cdAntigenName/innName
                            if not len(subsubchild):
                                add_name_or_ec_to_list_from_protein(subsubchild, dict_protein)
                            # domain/component with the infos from before
                            else:
                                for subsubsubchild in subsubchild.iterchildren():
                                    add_name_or_ec_to_list_from_protein(subsubsubchild, dict_protein)

                elif tag == 'reference':
                    dict_ref = {}
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag != 'citation':
                            # source
                            if len(subchild):
                                for subsubchild in subchild.iterchildren():
                                    subsub_tag = subsubchild.tag.replace(ns, '')
                                    add_key_value_to_dictionary_as_list(dict_ref, subsub_tag, subsubchild.text)
                                    evidence_citation_group = subsubchild.attrib[
                                        'evidence'] if 'evidence' in subsubchild.attrib else ''
                            # scope
                            else:
                                add_key_value_to_dictionary_as_list(dict_ref, sub_tag, subchild.text)
                        # citation
                        else:
                            subchild_attributes = dict(subchild.attrib)
                            dict_ref.update(subchild_attributes)
                            for subsubchild in subchild.iterchildren():
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if not len(subsubchild) and subsub_tag != 'dbReference':
                                    dict_ref[subsub_tag] = subsubchild.text
                                elif subsub_tag == 'dbReference':
                                    subsub_att = subsubchild.attrib
                                    prepare_dbReference(dict_ref, subsub_att)
                                    if len(subsubchild):
                                        sys.exit('ref dbref has child nodes!')
                                # editorList/authorList
                                else:
                                    subsub_tag = subsub_tag.replace('List', '') + 's'
                                    dict_ref[subsub_tag] = []
                                    for subsubsubchild in subsubchild.iterchildren():
                                        dict_ref[subsub_tag].append(subsubsubchild.attrib['name'])
                    if 'xrefs' in dict_ref:
                        dict_ref['xrefs'] = list(dict_ref['xrefs'])
                    add_key_value_to_dictionary_as_list(dict_protein, 'references', dict_ref)


                elif tag == 'comment':
                    comment_type = child.attrib['type']
                    if child.text is not None and child.text.replace('\n', '').replace(' ', '') != '':
                        print('ok')
                        print(comment_type)
                        print(child.text)
                        print(identifier)
                        sys.exit('has text')
                    # contain evidence
                    dict_comment = dict(child.attrib)
                    del dict_comment['type']
                    # boolean if commant is a real node or a property
                    is_a_rela = False
                    # rela pair
                    pair = []
                    # name of second part
                    name_second_label_id = ''

                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag == 'molecule':
                            if len(subchild.attrib) > 0:
                                print(subchild.attrib)
                                print('identifier')
                                sys.exit('molecule has attributes')
                            dict_comment[sub_tag] = subchild.text
                        elif sub_tag == 'text':
                            sub_evidence = subchild.attrib['evidence'] if 'evidence' in subchild.attrib else ''
                            dict_comment[sub_tag] = subchild.text
                        elif sub_tag == 'location':
                            preparation_of_location_type(subchild, dict_comment)
                        elif sub_tag == 'disease':
                            # print('disease')
                            disease_id = subchild.attrib['id']
                            dict_disease_node = {'identifier': disease_id}
                            pair = [identifier, disease_id]
                            if disease_id not in set_of_disease_ids:
                                set_of_disease_ids.add(disease_id)
                                if 'disease' not in dict_node_type_to_tsv:
                                    generates_node_tsv_file_and_cypher('disease',
                                                                       ['identifier', 'name', 'acronym', 'description',
                                                                        'xrefs'], ['xrefs'])
                                    generates_rela_tsv_file_and_cypher('disease',
                                                                       ['protein_id', 'disease_id', 'evidence', 'text',
                                                                        'molecule'],
                                                                       'associates', [])
                                for subsubchild in subchild.iterchildren():
                                    subsub_tag = subsubchild.tag.replace(ns, '')
                                    if subsub_tag != 'dbReference':
                                        dict_disease_node[subsub_tag] = subsubchild.text
                                    else:
                                        prepare_dbReference(dict_disease_node, subsubchild.attrib)
                                        if len(subsubchild):
                                            print('ohje dbRfe has childs in disease')
                                            print(identifier)
                                            print(disease_id)
                                            sys.exit('dfRef disease')
                                dict_disease_node = prepare_tsv_dictionary(dict_disease_node)
                                dict_node_type_to_tsv['disease'].writerow(dict_disease_node)
                                # print(dict_disease_node.keys())
                            name_second_label_id = 'disease_id'
                            is_a_rela = True
                        # protein interaction
                        elif sub_tag == 'interactant':
                            # print('interaction')
                            if 'protein_protein' not in dict_node_type_to_tsv:
                                generates_rela_tsv_file_and_cypher('protein',
                                                                   ['protein_id', 'protein_id_2', 'organismsDiffer',
                                                                    'number_of_experiments', 'interaction_ids',
                                                                    'iso_of_protein_from', 'iso_of_protein_to'],
                                                                   'interaction',
                                                                   ['interaction_ids', 'number_of_experiments'])
                            interact_id = subchild.attrib['intactId']
                            add_key_value_to_dictionary_as_list(dict_comment, 'interaction_ids', interact_id)
                            interacter_uniprot_id_element = subchild.find("{ns}id".format(ns=ns))
                            pair.append(interacter_uniprot_id_element.text)
                            # for subsubchild in subchild.iterchildren():

                            name_second_label_id = 'protein_id_2'
                            is_a_rela = True
                        # event contains only type
                        elif sub_tag == 'event':
                            dict_comment['event'] = subchild.attrib['type']
                        elif sub_tag == 'isoform':
                            dict_isoform = {}
                            for subsubchild in subchild.iterchildren():

                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if subsub_tag in ['id']:
                                    dict_isoform[subsub_tag] = subsubchild.text
                                elif subsub_tag in ['name', 'text']:
                                    dict_isoform[subsub_tag] = subsubchild.text
                                    evidence_isoform = subsubchild.attrib[
                                        'evidence'] if 'evidence' in subsubchild.attrib else ''
                                elif subsub_tag == 'sequence':
                                    for key, value in dict(subsubchild.attrib).items():
                                        dict_isoform[subsub_tag + '_' + key] = value
                            add_key_value_to_dictionary_as_list(dict_comment, 'isoforms', dict_isoform)
                        elif sub_tag == 'cofactor':
                            cofactor_evidence = subchild.attrib['evidence'] if 'evidence' in subchild.attrib else ''
                            dict_cofactor = {}
                            for subsubchild in subchild.iterchildren():
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if subsub_tag == 'name':
                                    dict_cofactor[subsub_tag] = subsubchild.text
                                # dbRef
                                else:
                                    prepare_dbReference(dict_cofactor, subsubchild.attrib)
                                    if len(subsubchild):
                                        print('ohje dbRef has childs in cofactors')
                                        print(identifier)
                                        sys.exit('dfRef cofactors')

                            if 'xrefs' in dict_cofactor:
                                dict_cofactor['xrefs'] = list(dict_cofactor['xrefs'])
                            add_key_value_to_dictionary_as_list(dict_comment, 'cofactor', dict_cofactor)
                        # conflict
                        elif sub_tag == 'conflict':
                            dict_conflict = dict(subchild.attrib)
                            for subsubchild in subchild.iterchildren():
                                subsub_attribut = subsubchild.attrib
                                text = subsub_attribut['resource']
                                if 'version' in subsub_attribut:
                                    text += ' version ' + subsub_attribut['version']
                                if 'id' in subsub_attribut:
                                    text += ':' + subsub_attribut['id']
                                add_key_value_to_dictionary_as_list(dict_conflict, 'sequences', text)
                            # todo check if confilct appear multiple types
                            dict_comment['conflict'] = dict_conflict


                        elif sub_tag == 'subcellularLocation':
                            dict_subcellular_location = {}
                            for subsubchild in subchild.iterchildren():
                                evidence_of_sub = subsubchild.attrib['evidence'] if 'evidence' in subsubchild else ''
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if subsub_tag == 'location':
                                    dict_subcellular_location[subsub_tag] = subsubchild.text
                                else:
                                    add_key_value_to_dictionary_as_list(dict_subcellular_location, subsub_tag,
                                                                        subsubchild.text)
                            add_key_value_to_dictionary_as_list(dict_comment, 'subcellular_locations',
                                                                dict_subcellular_location)

                        elif sub_tag == 'reaction':
                            evidence_of_reaction = subchild.attrib['evidence'] if 'evidence' in subsubchild else ''
                            dict_reaction = {}
                            for subsubchild in subchild.iterchildren():
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if subsub_tag == 'text':
                                    dict_reaction[subsub_tag] = subsubchild.text
                                else:
                                    prepare_dbReference(dict_reaction, subsubchild.attrib)
                                    if len(subsubchild):
                                        print('ohje dbRef has childs in reaction')
                                        print(identifier)
                                        sys.exit('dfRef reaction')
                            if 'xrefs' in dict_reaction:
                                dict_reaction['xrefs'] = list(dict_reaction['xrefs'])
                            dict_comment['reaction'] = dict_reaction
                        elif sub_tag == 'physiologicalReaction':
                            # has evidence
                            dict_physiological_reaction = dict(subchild.attrib)
                            for subsubchild in subchild.iterchildren():
                                prepare_dbReference(dict_physiological_reaction, subsubchild.attrib)
                                if len(subsubchild):
                                    print('ohje dbRef has childs in physiological reaction')
                                    print(identifier)
                                    sys.exit('dfRef physiological reaction')
                            if 'xrefs' in dict_physiological_reaction:
                                dict_physiological_reaction['xrefs'] = list(dict_physiological_reaction['xrefs'])
                            add_key_value_to_dictionary_as_list(dict_comment, 'physiological_reaction',
                                                                dict_physiological_reaction)
                        elif sub_tag in ['kinetics', 'phDependence', 'redoxPotential', 'temperatureDependence',
                                         'absorption']:
                            dict_subchild_infos = {}
                            for subsubchild in subchild.iterchildren():
                                subchild_evidence = subsubchild.attrib[
                                    'evidence'] if 'evidence' in subsubchild.attrib else ''
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if subsub_tag != 'max':
                                    add_key_value_to_dictionary_as_list(dict_subchild_infos, subsub_tag,
                                                                        subsubchild.text)
                                else:
                                    dict_subchild_infos[subsub_tag] = subsubchild.text
                            add_key_value_to_dictionary_as_list(dict_comment, sub_tag, dict_subchild_infos)

                        # contains only a link contains  only url
                        elif sub_tag in ['link']:
                            dict_attributes = dict(subchild.attrib)
                            dict_comment.update(dict_attributes)
                        elif sub_tag in ['organismsDiffer', 'experiments']:
                            if "experiments" == sub_tag:
                                dict_comment['number_of_experiments'] = subchild.text
                            else:
                                dict_comment[sub_tag] = subchild.text

                        else:
                            print("%s - %s - %s" % (sub_tag, subchild.text, subchild.attrib))

                    if not is_a_rela:
                        if comment_type == 'subcellular location':
                            comment_type = 'subcellular_locations'
                        add_key_value_to_dictionary_as_list(dict_protein, comment_type.replace(' ', '_'), dict_comment)
                    else:
                        # print(dict_comment.keys())
                        dict_rela = {'protein_id': pair[0], name_second_label_id: pair[1]}
                        dict_rela.update(dict_comment)
                        dict_rela = prepare_tsv_dictionary(dict_rela)
                        if name_second_label_id == 'disease_id':
                            dict_node_type_to_tsv['protein_disease'].writerow(dict_rela)
                        elif name_second_label_id == 'protein_id_2':
                            list_of_interactions.append(dict_rela)
                            # dict_node_type_to_tsv['protein_protein'].writerow(dict_rela)
                else:
                    print("%s - %s - %s" % (tag, child.text, child.attrib))
            else:
                if tag in ["accession", "name"]:
                    if tag not in dict_protein:
                        dict_protein[tag] = []
                        # get the node identifier
                        if tag == 'accession':
                            dict_protein['identifier'] = child.text
                            identifier = child.text

                            first_accession = False
                            if child.text not in dict_up_accession_to_uniprot_id:
                                dict_up_accession_to_uniprot_id[child.text] = set()
                            dict_up_accession_to_uniprot_id[child.text].add(identifier)
                            continue
                    if 'accession' == tag:
                        if child.text not in dict_up_accession_to_uniprot_id:
                            dict_up_accession_to_uniprot_id[child.text] = set()
                        dict_up_accession_to_uniprot_id[child.text].add(identifier)
                    dict_protein[tag].append(child.text)
                # sequence information
                elif tag == 'sequence':
                    dict_protein["as_sequence"] = child.text
                    dict_protein['sequenceLength'] = attributes['length']
                    dict_protein['mass'] = attributes['mass']
                    if 'fragment' in attributes:
                        dict_protein['fragment'] = attributes['fragment']
                # reference information
                elif tag == 'dbReference':
                    prepare_dbReference(dict_protein, attributes)
                # kind of existence of the protein
                elif tag == 'proteinExistence':
                    dict_protein['protein_existence'] = attributes['type']
                # classification of the protein
                elif tag == 'keyword':
                    keyword_id = attributes['id']
                    if keyword_id not in dict_keyword:
                        dict_node_keyword = {'id': keyword_id, 'name': child.text}
                        if 'keyword' not in dict_node_type_to_tsv:
                            generates_node_tsv_file_and_cypher('keyword', ['id', 'name'], [])
                            # rela
                            generates_rela_tsv_file_and_cypher('keyword', ['uniprot_id', 'keyword_id'], 'part_of', [])
                        dict_keyword[keyword_id] = child.text
                        dict_node_type_to_tsv['keyword'].writerow(dict_node_keyword)
                    evidence_keyword = attributes['evidence'] if 'evidence' in attributes else ''
                    set_keyword_protein_pairs.add((keyword_id, identifier))
                    dict_node_type_to_tsv['protein_keyword'].writerow(
                        {'uniprot_id': identifier, 'keyword_id': keyword_id})
                # evidence of the protein
                elif tag == 'evidence':
                    prepare_evidence(attributes, identifier)
                # location of the gene
                elif tag == 'geneLocation':
                    preparation_gene_location(dict_protein, attributes)

                elif tag == 'comment':
                    comment_type = child.attrib['type']
                    if child.text is not None:
                        print('ok')
                        print(comment_type)
                        sys.exit('has text')
                    dict_comment = dict(child.attrib)
                    del dict_comment['type']
                    add_key_value_to_dictionary_as_list(dict_protein, comment_type.replace(' ', '_'), dict_comment)

                else:
                    print('not')
                    print("%s - %s - %s" % (tag, child.text, child.attrib))
        # print(dict_protein)
        # print('This is the identifier:', identifier)
        # prepare name
        dict_protein['entry_name'] = dict_protein['name']
        dict_protein['name'] = dict_protein['protein_name'][0]
        dict_protein['synonyms'] = dict_protein['protein_name'][1:]
        del dict_protein['protein_name']

        set_of_protein_propertie = set_of_protein_propertie.union(dict_protein.keys())
        dict_protein = prepare_tsv_dictionary(dict_protein)
        dict_node_type_to_tsv['protein'].writerow(dict_protein)
        node.clear()

        # if counter_human > 1500:
        #     break
    print('set of protein properties')
    print(set_of_protein_propertie)
    print("number of human proteins:", counter_human)


dict_node_type_to_tsv = {}


def generate_tsv_file(label, properties):
    """
    Prepare a filename. The generate a file and make a tsv writer on it.
    :param label: string
    :param properties: list
    :return: string
    """
    file_name = 'output/' + label + '.tsv'
    file = open(file_name, 'w')
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
    query = '''Create (n:%s_Uniprot{ '''

    query = query % (label.capitalize())

    for property in properties:
        if property in list_properties:
            if property in ['chromosome_location', 'accession']:
                query += property + 's:split(line.' + property + ',"||"), '
            else:
                query += property + ':split(line.' + property + ',"||"), '
        else:
            query += property + ':line.' + property + ', '
    query = query[:-2] + '})'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/uniProt/{file_name}', query)
    cypherfile.write(query)
    query = pharmebinetutils.prepare_index_query(label.capitalize() + '_Uniprot', properties[0])
    cypherfile.write(query)


def prepare_edge_cypher_query(file_name, label, rela_name, properties, list_properties):
    """
    Prepare the cypher query fo a node.
    :param file_name: string
    :param label: string
    :param properties: list
    :param list_properties: list
    :return:
    """
    query = '''Match (n:Protein_Uniprot{identifier:line.%s}), (b:%s_Uniprot{%s:line.%s}) Create (n)-[:%s'''

    query = query + '{' if len(properties) > 2 else query
    if label in ['protein', 'disease']:
        query = query % (properties[0], label.capitalize(), 'identifier', properties[1], rela_name)
    else:
        query = query % (properties[0], label.capitalize(), 'id', properties[1], rela_name)
    for property in properties[2:]:
        if property in list_properties:
            query += property + ':split(line.' + property + ',"||"), '
        else:
            query += property + ':line.' + property + ', '
    query = query[:-2] + '}]->(b)' if len(properties) > 2 else query + ']->(b)'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/uniProt/{file_name}', query)
    cypherfile.write(query)


def generates_node_tsv_file_and_cypher(label, properties, list_properties):
    """

    :return:
    """
    file_name = generate_tsv_file(label, properties)

    prepare_node_cypher_query(file_name, label, properties, list_properties)


def generates_rela_tsv_file_and_cypher(label, properties, rela_name, list_properties):
    """
    Generate the tsv file for rela. Also add cypher query to cypher file.
    :param label: string
    :param properties: list
    :param rela_name: string
    :param list_properties:  list
    :return:
    """
    file_name = generate_tsv_file('protein_' + label, properties)

    prepare_edge_cypher_query(file_name, label, rela_name, properties, list_properties)


def check_for_protein(protein_id):
    """
    Check if the protein id or the not isoform is in the dict_up_accession_to_uniprot_id
    :param protein_id: string
    :return: found id in dict, protein id, isoform
    """
    if '-' in protein_id:
        without_iso = protein_id.split('-')[0]
        if without_iso in dict_up_accession_to_uniprot_id:
            return True, without_iso, protein_id
        else:
            print('accession not in dictionary?', protein_id)
            return False, '', ''
    else:
        if protein_id in dict_up_accession_to_uniprot_id:
            return True, protein_id, ''
        else:
            print('accession not in dictionary?', protein_id)
            return False, '', ''


def write_interaction_rela_into_tsv():
    for dict_rela in list_of_interactions:
        protein_id_1 = dict_rela['protein_id']
        protein_id_2 = dict_rela['protein_id_2']

        found_id_1, protein_id_1, protein_1_iso = check_for_protein(protein_id_1)
        if not found_id_1:
            continue
        found_id_2, protein_id_2, protein_2_iso = check_for_protein(protein_id_2)
        if not found_id_2:
            continue

        for identifier1 in dict_up_accession_to_uniprot_id[protein_id_1]:
            for identifier2 in dict_up_accession_to_uniprot_id[protein_id_2]:
                dict_rela['protein_id'] = identifier1
                dict_rela['protein_id_2'] = identifier2
                dict_rela['iso_of_protein_from'] = protein_1_iso
                dict_rela['iso_of_protein_to'] = protein_2_iso
                dict_node_type_to_tsv['protein_protein'].writerow(dict_rela)


def main():
    global path_of_directory
    # path to project dictionary
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print('#############################################################')
    print(datetime.datetime.now())
    print('parse xml data ')

    run_trough_xml_and_parse_data()

    print('#############################################################')
    print(datetime.datetime.now())
    print('write protein-protein pairs into tsv file')

    write_interaction_rela_into_tsv()

    print('#############################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
