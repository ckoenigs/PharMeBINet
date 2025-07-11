import csv
import ujson, sys
from typing import Dict, Set, Tuple
import datetime

sys.path.append("../..")
import pharmebinetutils

# generate cypher file
cypher_file = open('output/cypher.cypher', 'w')
cypher_file_edge = open('output/cypher_edge.cypher', 'w')


def generate_cypher_queries(file_name, label, properties, list_properties):
    """
    generate cypher queries for nodes and add to cypher file
    :param file_name: string
    :param label: string
    :param properties: list of string
    :param list_properties: list of string
    :return:
    """
    query_node = ' Create (n:%s_dbSNP{'
    for x in properties:
        if x in list_properties:
            query_node += x + ':split(line.' + x + ',"||"), '
        else:
            query_node += x + ':line.' + x + ', '

    query_node = query_node + ' license:"https://www.ncbi.nlm.nih.gov/home/about/policies/"})'
    query_node = query_node % (label)
    file_name_split = file_name.split('/', 1)
    query_node = pharmebinetutils.get_query_import(file_name_split[0], file_name_split[1], query_node)
    cypher_file.write(query_node)

    cypher_file.write(pharmebinetutils.prepare_index_query(label + '_dbSNP', 'identifier'))


def generate_cypher_queries_for_relationships(file_name, label1, label2, rela_name, properties, list_properties):
    """
    generate cypher queries for relationships and add to cypher file
    :param file_name: string
    :param label1: string
    :param label2: string
    :param rela_name:string
    :param properties: list of string
    :param list_properties: list of string
    :return:
    """
    query_node = ' Match (n:%s_dbSNP{identifier:line.%s}), (m:%s_dbSNP{identifier:line.%s}) Create (n)-[:%s{'
    for x in properties[2:]:
        if x in list_properties:
            query_node += x + ':split(line.' + x + ',"||"), '
        else:
            query_node += x + ':line.' + x + ', '

    query_node = query_node + ' license:"CC0 1.0"}]->(m)'
    query_node = query_node % (label1, properties[0], label2, properties[1], rela_name)
    file_name_split = file_name.split('/', 1)
    query_node = pharmebinetutils.get_query_import(file_name_split[0], file_name_split[1], query_node)
    cypher_file_edge.write(query_node)


# dict_label_to_set_of_ids
dict_label_to_set_of_ids: Dict[str, Set[str]] = {}


def add_label_set_of_ids_if_not_exists(label: str) -> bool:
    """
    check if label exists in a dictionary or not and if not add with value an empty set
    :param label:
    :return:
    """
    if label not in dict_label_to_set_of_ids:
        dict_label_to_set_of_ids[label] = set()
        return True
    return False


def add_id_to_label_set_of_ids_if_not_exists(label: str, _id: str) -> bool:
    """
    check if id in set if not add
    :param label:
    :param _id:
    :return:
    """
    if _id not in dict_label_to_set_of_ids[label]:
        dict_label_to_set_of_ids[label].add(_id)
        # print(sum([len(dict_label_to_set_of_ids[x]) for x in dict_label_to_set_of_ids]))
        return True
    return False


# dictionary label or rela_label to file
dict_label_to_tsv_file = {}

# test
path_to_data = ''

# header snp
header_snp = ['is_top_level', 'is_chromosome', 'supporting_subsnps', 'position', 'is_alt', 'deleted_sequence',
              'other_rsids_in_cur_release', 'variant_type', 'mol_type', 'xrefs', 'anchor', 'create_date',
              'clinical_variant_ids', 'last_update_date', 'dbsnp1_merges', 'assembly_accession',
              'is_patch', 'seq_id', 'subsnps', 'hgvs_list', 'identifier', 'citations', 'frequencies_list', 'seq_type',
              'inserted_sequence', 'last_update_build_id', 'assembly_name', 'sequence_position_deletion_insertions',
              'chromosome']

# header snp where the property is a list
header_snp_list = ['frequencies_list', 'sequence_position_deletion_insertions', 'xrefs',
                   'other_rsids_in_cur_release', 'hgvs_list', 'clinical_variant_ids', 'dbsnp1_merges', 'citations',
                   'supporting_subsnps', 'subsnps']


def generate_csv_file_and_add_to_dictionary(label, header):
    """
    generate for a given label a tsv file and add it to dictionary
    :param label: string
    :param header: list of stings
    :return: file name
    """
    file_name = path_to_data + 'output/' + label + '.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_file = csv.DictWriter(file, delimiter='\t', fieldnames=header)
    csv_file.writeheader()
    dict_label_to_tsv_file[label] = csv_file
    return file_name


def prepare_own_set(dictionary, dict_node):
    """
    generate a set if a specific type in the dictionary
    if so add this information to the node dictionary
    if it is clinvar the type is xref and and value is transformed
    :param dictionary: dictionary where the information came from
    :param dict_node: dictionary where the information goes
    :return: found True or False
    """
    if dictionary['type'] == 'clinvar':
        dictionary['type'] = 'xref'
        dictionary['value'] = 'clinvar:' + dictionary['value']
    type_plural = dictionary['type'] + 's'
    if not type_plural in header_snp:
        return
    if type_plural not in dict_node:
        dict_node[type_plural] = set()
        set_headers_node.add(type_plural)
    dict_node[type_plural].add(dictionary['value'])
    set_headers_node.add(type_plural)


def add_information_from_one_dict_to_another_and_prepare_as_string(from_dict, to_dict, key):
    """
       write a information from one dictionary into another with the same key but in every time as string
       :param from_dict: dictionary
       :param to_dict: dictionary
       :param key: string
       :return:
       """
    # print(from_dict)
    # print(key)
    if key in from_dict:
        if type(from_dict[key]) in [set, list]:
            if len(from_dict[key]) > 0 and type(from_dict[key][0]) == int:
                from_dict[key] = [str(x) for x in from_dict[key]]
            to_dict[key] = "||".join(list(from_dict[key]))
        else:
            to_dict[key] = from_dict[key]


def add_information_from_one_dict_to_another(from_dict, to_dict, key):
    """
    write a information from one dictionary into another with the same key
    :param from_dict: dictionary
    :param to_dict: dictionary
    :param key: string
    :return:
    """
    # print(from_dict)
    # print(key)
    if key in from_dict:
        if key not in header_snp:
            return
        if key in to_dict and from_dict[key] != to_dict[key]:
            # some have multiple possibilities for the insertion
            if key == 'inserted_sequence':
                if not from_dict[key] in to_dict[key]:
                    to_dict[key] += '/' + from_dict[key]
                return
            if type(from_dict[key]) == str and (from_dict[key] == '' or to_dict[key] == ''):
                return
            elif type(from_dict[key]) == list and (len(from_dict[key]) == 0 or len(to_dict[key]) == 0):
                return
            # are rs ids snps on the same position but different changes
            if key == 'other_rsids_in_cur_release':
                to_dict[key] = set(to_dict[key]).union(from_dict[key])
                return
            print(key)
            print(from_dict[key])
            print(to_dict[key])
        to_dict[key] = from_dict[key]
        set_headers_node.add(key)


def return_seq_ontology_names(dictionary):
    """
    return only the names of sequence-ontology as as string of combined of |
    :param dictionary: dictionary
    :return: string
    """
    return "||".join([x['name'] for x in dictionary['sequence_ontology']])


def generate_files_with_node_and_rela(label_node, label_other_node, node_properties):
    """
    if the label has not already a tsv file generate the tsv file and the relationship files
    for rna and protein
    :param label_node: string
    :param label_other_node: string
    :param node_properties: list of string
    :return:
    """
    if label_node not in dict_label_to_tsv_file:
        # generate tsv file for rna
        file_name = generate_csv_file_and_add_to_dictionary(label_node, node_properties)
        generate_cypher_queries(file_name, label_node, node_properties, [])

        # rela
        dict_rela_label_to_pairs['snp_' + label_node] = set()
        dict_rela_label_to_pairs[label_other_node + '_' + label_node] = set()
        file_name = generate_csv_file_and_add_to_dictionary('snp_' + label_node,
                                                            ['snp_id', label_node + '_id',
                                                             'sequence_ontology',
                                                             'deleted_sequence',
                                                             'inserted_sequence', 'position'])
        generate_cypher_queries_for_relationships(file_name, 'snp', label_node, 'associates',
                                                  ['snp_id', label_node + '_id', 'sequence_ontology',
                                                   'deleted_sequence',
                                                   'inserted_sequence',
                                                   'position'], [])

        file_name = generate_csv_file_and_add_to_dictionary(label_other_node + '_' + label_node,
                                                            [label_other_node + '_id', label_node + '_id'])
        generate_cypher_queries_for_relationships(file_name, label_other_node, label_node, 'associates',
                                                  [label_other_node + '_id', label_node + '_id'], [])


def combine_spdi_to_string(spdi, dictionary: Dict[str, Set[str]]):
    """
    combine the spdi (Sequence Position Deletion Insertion) to a string
    :param dictionary:
    :param spdi: dictionary
    :return:
    """
    if spdi['deleted_sequence'] != spdi['inserted_sequence']:
        spdi_string = spdi['seq_id'] + ':' + str(spdi['position']) + ':' + spdi['deleted_sequence'] + ':' + spdi[
            'inserted_sequence']
        if 'sequence_position_deletion_insertions' not in dictionary:
            dictionary['sequence_position_deletion_insertions'] = set()
        dictionary['sequence_position_deletion_insertions'].add(spdi_string)
        set_headers_node.add('sequence_position_deletion_insertions')

final_disease_counter=0

def find_disease_id_generate_xref_name_and_synonyms(disease_names, disease_ids):
    """

    :param disease_names:
    :param disease_ids:
    :return:
    """
    global final_disease_counter
    final_disease_id = ''
    xrefs = set()
    found_on_id_in_set = False
    name = ''
    synonyms = set(disease_names)
    # check if one of the id is already in set
    # else take one of the ids as disease id
    if len(disease_ids) > 0:
        for disease_id in disease_ids:
            disease_id = disease_id['organization'] + ':' + disease_id['accession']
            if disease_id in dict_label_to_set_of_ids['disease']:
                final_disease_id = disease_id
                found_on_id_in_set = True
            xrefs.add(disease_id)
        if not found_on_id_in_set:
            final_disease_id = xrefs.pop()
    else:
        for name in disease_names:
            if name in dict_label_to_set_of_ids['disease']:
                final_disease_id = name
                found_on_id_in_set = True
        if not found_on_id_in_set and len(synonyms)>0:
            final_disease_id = synonyms.pop()
            name = final_disease_id
        elif not found_on_id_in_set:
            print('disease has no id and no name')
            final_disease_id=final_disease_counter
            final_disease_counter+=1

    if name == '' and len(synonyms) > 0:
        name = synonyms.pop()

    return final_disease_id, xrefs, name, synonyms


# set_headers_node
set_headers_node = set()

# dictionary of rela label to the pairs
dict_rela_label_to_pairs: Dict[str, Set[Tuple[str, str]]] = {}

# set of all headers which are list
set_header_node_list = set()


def prepare_dict_node_to_be_string(dict_node):
    """
    go through the dictionary and change the list/sets to strings
    :param dict_node:
    :return:
    """
    for key, value in dict_node.items():
        if type(value) in [set, list]:
            if len(value) > 0 and type(list(value)[0]) == int:
                value = [str(x) for x in value]
            set_header_node_list.add(key)
            dict_node[key] = "||".join(list(value))


# header_snp
# header_snp=set(['refsnp_id','citations',])

# counter not used nodes
counter_not_used_nodes = 0


def add_to_node_information(key, value, dict_node):
    """
    add only values which should be add into dictionary
    :param key:
    :param value:
    :param dict_node:
    :return:
    """
    if key in header_snp:
        dict_node[key] = value

set_of_unique_snp_ids=set()

def prepare_json_information_to_tsv(data, chromosome_number=None):
    """
    information about the different properties of the json are from https://github.com/ncbi/dbsnp/blob/master/specs/refsnp_specification_deprecated.yaml
    only the interesting information were taken
    :param json_string:
    :return:
    """
    global counter_not_used_nodes
    if chromosome_number is not None:
        dict_node = {'chromosome': chromosome_number}
    else:
        dict_node = {}

    snp_id = ''
    for key, value in data.items():
        if type(value) == str:
            if key == 'refsnp_id':
                key = 'identifier'
                snp_id = value
                # print(snp_id)
            add_to_node_information(key, value, dict_node)
            set_headers_node.add(key)
            continue
        # pubmed citations
        if key == 'citations':
            add_to_node_information(key, value, dict_node)
            set_headers_node.add(key)
            continue

        # the merged ids
        if key == 'dbsnp1_merges':
            list_merge_ids = [x['merged_rsid'] for x in value]
            add_to_node_information(key, list_merge_ids, dict_node)
            set_headers_node.add(key)
            continue
        if key == 'primary_snapshot_data':
            # print(value.keys())
            for property, values in value.items():
                if type(values) == str:
                    add_to_node_information(property, values, dict_node)
                    set_headers_node.add(property)
                    continue
                # contains only subsnp, frequency and clinvar
                if property == 'support':
                    for dictionary in values:
                        id_dict = dictionary['id']
                        prepare_own_set(id_dict, dict_node)
                    continue
                if property == 'placements_with_allele':
                    for allele_dictionary in values:

                        # has top level placement (ptlp) //and assembly info
                        if allele_dictionary['is_ptlp']:
                            add_information_from_one_dict_to_another(allele_dictionary, dict_node, 'seq_id')
                            placement_annot = allele_dictionary['placement_annot']
                            add_information_from_one_dict_to_another(placement_annot, dict_node, 'seq_type')
                            add_information_from_one_dict_to_another(placement_annot, dict_node, 'mol_type')
                            if len(placement_annot['seq_id_traits_by_assembly']) > 1:
                                print('is longer than  1 ;(')
                                print(placement_annot['seq_id_traits_by_assembly'])
                            if len(placement_annot['seq_id_traits_by_assembly']) == 1:
                                add_information_from_one_dict_to_another(
                                    placement_annot['seq_id_traits_by_assembly'][0],
                                    dict_node, 'assembly_name')
                                add_information_from_one_dict_to_another(
                                    placement_annot['seq_id_traits_by_assembly'][0],
                                    dict_node, 'assembly_accession')
                                # todo if I really want this

                                #  True if the sequence is top-level (the most highly assembled sequences
                                #           in a genome assembly).
                                add_information_from_one_dict_to_another(
                                    placement_annot['seq_id_traits_by_assembly'][0],
                                    dict_node, 'is_top_level')
                                # True if this placement's sequence is an alternative loci (a sequence
                                #           that provides an alternate representation of a locus found in a
                                #           largely haploid assembly)
                                add_information_from_one_dict_to_another(
                                    placement_annot['seq_id_traits_by_assembly'][0],
                                    dict_node, 'is_alt')
                                # True if this placement's sequence is a patch sequence (a contig
                                #           sequence that is released outside of the full assembly release cycle.
                                #           These sequences are meant to add information to the assembly without
                                #           disrupting the stable coordinate system)
                                add_information_from_one_dict_to_another(
                                    placement_annot['seq_id_traits_by_assembly'][0],
                                    dict_node, 'is_patch')
                                # True if this placement's sequence is a chromosome sequence (a relatively
                                #           complete pseudo-molecule assembled from smaller sequences (components)
                                #           that represent a biological chromosome)
                                add_information_from_one_dict_to_another(
                                    placement_annot['seq_id_traits_by_assembly'][0],
                                    dict_node, 'is_chromosome')

                            for allele in allele_dictionary['alleles']:
                                spdi = allele['allele']['spdi']
                                if 'frameshift' in allele['allele']:
                                    print('framshift allele')
                                    print(frameshift)
                                    print(allele)

                                if 'warnings' in spdi:
                                    print('warning')
                                    print(spdi)
                                # to get the mutation version and not the normal gene check if delete and inserte are
                                # not equal
                                if spdi['deleted_sequence'] != spdi['inserted_sequence']:
                                    add_information_from_one_dict_to_another(spdi, dict_node, 'deleted_sequence')
                                    add_information_from_one_dict_to_another(spdi, dict_node, 'inserted_sequence')
                                    add_information_from_one_dict_to_another(spdi, dict_node, 'position')

                                if 'hgvs_list' not in dict_node:
                                    dict_node['hgvs_list'] = set()
                                dict_node['hgvs_list'].add(allele['hgvs'])
                                set_headers_node.add('hgvs_list')
                        else:
                            # get all possible hgvs
                            for allele in allele_dictionary['alleles']:
                                if 'hgvs_list' not in dict_node:
                                    dict_node['hgvs_list'] = set()
                                dict_node['hgvs_list'].add(allele['hgvs'])
                                set_headers_node.add('hgvs_list')
                    continue

                # allele annotation ready
                if property == 'allele_annotations':
                    # print('allele annotations')
                    # print(values)
                    for dictionary in values:
                        for head, item in dictionary.items():
                            if head == 'frequency':
                                list_frequencies = []
                                for frequence in item:
                                    study_name = frequence['study_name']
                                    allele_count_without_snp = frequence['allele_count']
                                    total_count = frequence['total_count']
                                    observation = frequence['observation']
                                    # if observation['deleted_sequence'] == observation['inserted_sequence']:
                                    #     # compute the frequence one value is the number of alleles where no snp is and the
                                    #     # total number of alleles found. To get the frequence for the snp you have to get
                                    #     # the difference and divided by the total number
                                    #     difference = int(total_count) - int(allele_count_without_snp)
                                    #     frequency = (difference) / float(total_count)
                                    #     frequency_string = "{:.5f}".format(frequency) + '(' + str(
                                    #         difference) + '/' + str(
                                    #         total_count) + ' ' + study_name + ')'
                                    # else:
                                    frequency = (allele_count_without_snp) / float(total_count)
                                    frequency_string = observation['deleted_sequence'] + '>' + observation[
                                        'inserted_sequence'] + ":{:.5f}".format(frequency) + '(' + str(
                                        allele_count_without_snp) + '/' + str(
                                        total_count) + ' ' + study_name + ')'
                                    list_frequencies.append(frequency_string)
                                if 'frequencies_list' not in dict_node:
                                    dict_node['frequencies_list'] = set()
                                    set_headers_node.add('frequencies')
                                dict_node['frequencies_list'] = dict_node['frequencies_list'].union(list_frequencies)

                                continue
                            if head == 'clinical':
                                clinvar_variant_ids = set()
                                for clinical in item:
                                    clinvar_variant_ids.add(clinical['measure_set_id'])
                                    if 'xrefs' not in dict_node:
                                        dict_node['xrefs'] = set()
                                    for variant_id in clinical['variant_identifiers']:
                                        dict_node['xrefs'].add(
                                            variant_id['organization'] + ':' + variant_id['accession'])

                                    if add_label_set_of_ids_if_not_exists('disease'):
                                        properties_disease = ['identifier', 'name', 'synonyms',
                                                              'xrefs']
                                        file_name = generate_csv_file_and_add_to_dictionary('disease',
                                                                                            properties_disease)
                                        generate_cypher_queries(file_name, 'disease', properties_disease,
                                                                ['synonyms', 'xrefs'])

                                        dict_rela_label_to_pairs['snp_disease'] = set()
                                        file_name = generate_csv_file_and_add_to_dictionary('snp_disease',
                                                                                            ['snp_id', 'disease_id',
                                                                                             'clinical_significances',
                                                                                             'origins',
                                                                                             'collection_method',
                                                                                             'citations',
                                                                                             'review_status'])
                                        generate_cypher_queries_for_relationships(file_name, 'snp',
                                                                                  'disease', 'associates',
                                                                                  ['snp_id', 'disease_id',
                                                                                   'clinical_significances', 'origins',
                                                                                   'collection_method', 'citations',
                                                                                   'review_status'],
                                                                                  ['citations', 'origins'])

                                    disease_id, disease_xrefs, disease_name, disease_synonyms = find_disease_id_generate_xref_name_and_synonyms(
                                        clinical['disease_names'], clinical['disease_ids'])

                                    if add_id_to_label_set_of_ids_if_not_exists('disease', disease_id):
                                        dict_disease = {'identifier': disease_id, 'name': disease_name,
                                                        'xrefs': "||".join(list(disease_xrefs)),
                                                        'synonyms': "||".join(list(disease_synonyms))}
                                        dict_label_to_tsv_file['disease'].writerow(dict_disease)

                                    if (snp_id, disease_id) not in dict_rela_label_to_pairs['snp_disease']:
                                        # dict_rela_label_to_pairs['snp_disease'].add((snp_id, disease_id))
                                        dict_snp_disease = {'snp_id': snp_id, 'disease_id': disease_id}
                                        add_information_from_one_dict_to_another_and_prepare_as_string(clinical,
                                                                                                       dict_snp_disease,
                                                                                                       'clinical_significances')
                                        add_information_from_one_dict_to_another_and_prepare_as_string(clinical,
                                                                                                       dict_snp_disease,
                                                                                                       'review_status')
                                        add_information_from_one_dict_to_another_and_prepare_as_string(clinical,
                                                                                                       dict_snp_disease,
                                                                                                       'origins')
                                        add_information_from_one_dict_to_another_and_prepare_as_string(clinical,
                                                                                                       dict_snp_disease,
                                                                                                       'collection_method')
                                        add_information_from_one_dict_to_another_and_prepare_as_string(clinical,
                                                                                                       dict_snp_disease,
                                                                                                       'citations')
                                        dict_label_to_tsv_file['snp_disease'].writerow(dict_snp_disease)

                                if 'clinical_variant_ids' not in dict_node:
                                    dict_node['clinical_variant_ids'] = set()
                                    set_headers_node.add('clinical_variant_ids')
                                dict_node['clinical_variant_ids'] = dict_node['clinical_variant_ids'].union(
                                    clinvar_variant_ids)
                                continue
                            if head == 'submissions':
                                if 'supporting_subsnps' not in dict_node:
                                    dict_node['supporting_subsnps'] = set()
                                    set_headers_node.add('supporting_subsnps')
                                dict_node['supporting_subsnps'] = dict_node['supporting_subsnps'].union(item)
                                continue
                            if head == 'assembly_annotation':
                                for assembly_annotation in item:
                                    # is every time human
                                    # if 'homo sapiens' in assembly_annotation['annotation_release'].lower():
                                    #     is_human = True
                                    # else:
                                    #     print('not human?')
                                    #     print(assembly_annotation['annotation_release'])
                                    # print(assembly_annotation)
                                    for gene in assembly_annotation['genes']:

                                        gene_id = gene['id']
                                        add_label_set_of_ids_if_not_exists('gene')
                                        if add_id_to_label_set_of_ids_if_not_exists('gene', gene_id):
                                            if 'gene' not in dict_label_to_tsv_file:
                                                properties_gene = ['identifier', 'name', 'locus',
                                                                   'is_pseudo',
                                                                   'orientation']
                                                # generate tsv file for gene
                                                file_name = generate_csv_file_and_add_to_dictionary('gene',
                                                                                                    properties_gene)
                                                generate_cypher_queries(file_name, 'gene', properties_gene, [])

                                                dict_rela_label_to_pairs['snp_gene'] = set()
                                                file_name = generate_csv_file_and_add_to_dictionary('snp_gene',
                                                                                                    ['snp_id',
                                                                                                     'gene_id',
                                                                                                     'sequence_ontology'])
                                                generate_cypher_queries_for_relationships(file_name, 'snp',
                                                                                          'gene', 'associates',
                                                                                          ['snp_id',
                                                                                           'gene_id',
                                                                                           'sequence_ontology'], [])
                                            dict_gene = {}
                                            dict_gene['identifier'] = gene_id
                                            add_information_from_one_dict_to_another_and_prepare_as_string(gene,
                                                                                                           dict_gene,
                                                                                                           'name')
                                            add_information_from_one_dict_to_another_and_prepare_as_string(gene,
                                                                                                           dict_gene,
                                                                                                           'locus')
                                            add_information_from_one_dict_to_another_and_prepare_as_string(gene,
                                                                                                           dict_gene,
                                                                                                           'is_pseudo')
                                            add_information_from_one_dict_to_another_and_prepare_as_string(gene,
                                                                                                           dict_gene,
                                                                                                           'orientation')
                                            dict_label_to_tsv_file['gene'].writerow(dict_gene)

                                        if (snp_id, gene_id, return_seq_ontology_names(gene)) not in \
                                                dict_rela_label_to_pairs['snp_gene']:
                                            dict_snp_gene = {}
                                            dict_snp_gene['snp_id'] = snp_id
                                            dict_snp_gene['gene_id'] = gene_id
                                            dict_snp_gene['sequence_ontology'] = return_seq_ontology_names(gene)
                                            dict_label_to_tsv_file['snp_gene'].writerow(dict_snp_gene)
                                            dict_rela_label_to_pairs['snp_gene'].add(
                                                (snp_id, gene_id, return_seq_ontology_names(gene)))

                                        if add_label_set_of_ids_if_not_exists('rna'):
                                            generate_files_with_node_and_rela('rna', 'gene',
                                                                              ['identifier', 'product_id'])
                                        for rna in gene['rnas']:
                                            rna_id = rna['id']
                                            # rna
                                            if add_id_to_label_set_of_ids_if_not_exists('rna', rna_id):
                                                dict_rna = {}
                                                dict_rna['identifier'] = rna_id
                                                add_information_from_one_dict_to_another_and_prepare_as_string(rna,
                                                                                                               dict_rna,
                                                                                                               'product_id')
                                                dict_label_to_tsv_file['rna'].writerow(dict_rna)

                                            # snp-rna relationship
                                            # print(rna)
                                            sequence_ontology = return_seq_ontology_names(rna)

                                            dict_rela_snp_rna = {}
                                            dict_rela_snp_rna['snp_id'] = snp_id
                                            dict_rela_snp_rna['rna_id'] = rna_id
                                            dict_rela_snp_rna['sequence_ontology'] = sequence_ontology
                                            if 'codon_aligned_transcript_change' in rna:
                                                codon_aligned_transcript_change = rna['codon_aligned_transcript_change']
                                                if (snp_id, rna_id, codon_aligned_transcript_change['position']) not in \
                                                        dict_rela_label_to_pairs['snp_rna']:
                                                    if codon_aligned_transcript_change['deleted_sequence'] != \
                                                            codon_aligned_transcript_change['inserted_sequence']:
                                                        dict_rela_label_to_pairs['snp_rna'].add((snp_id, rna_id,
                                                                                                 codon_aligned_transcript_change[
                                                                                                     'position']))

                                                        add_information_from_one_dict_to_another_and_prepare_as_string(
                                                            codon_aligned_transcript_change, dict_rela_snp_rna,
                                                            'deleted_sequence')
                                                        add_information_from_one_dict_to_another_and_prepare_as_string(
                                                            codon_aligned_transcript_change, dict_rela_snp_rna,
                                                            'inserted_sequence')
                                                        add_information_from_one_dict_to_another_and_prepare_as_string(
                                                            codon_aligned_transcript_change, dict_rela_snp_rna,
                                                            'position')

                                                        dict_label_to_tsv_file['snp_rna'].writerow(dict_rela_snp_rna)
                                            else:
                                                if (snp_id, rna_id, sequence_ontology) not in dict_rela_label_to_pairs[
                                                    'snp_rna']:
                                                    dict_rela_label_to_pairs['snp_rna'].add(
                                                        (snp_id, rna_id, sequence_ontology))
                                                    dict_label_to_tsv_file['snp_rna'].writerow(dict_rela_snp_rna)

                                            # gene rna relationship
                                            if (gene_id, rna_id) not in dict_rela_label_to_pairs['gene_rna']:
                                                dict_rela_label_to_pairs['gene_rna'].add((gene_id, rna_id))
                                                dict_gene_rna = {'gene_id': gene_id, 'rna_id': rna_id}
                                                dict_label_to_tsv_file['gene_rna'].writerow(dict_gene_rna)

                                            if 'protein' in rna:
                                                protein = rna['protein']
                                                sequence_ontology_protein = return_seq_ontology_names(protein)
                                                if add_label_set_of_ids_if_not_exists('protein'):
                                                    generate_files_with_node_and_rela('protein', 'rna',
                                                                                      ['identifier'])

                                                dict_snp_protein = {'snp_id': snp_id,
                                                                    'sequence_ontology': sequence_ontology_protein}

                                                if 'spdi' in protein['variant']:
                                                    spdi = protein['variant']['spdi']
                                                    protein_id = spdi['seq_id']
                                                    # protein node
                                                    if add_id_to_label_set_of_ids_if_not_exists('protein', protein_id):
                                                        dict_protein = {'identifier': protein_id}
                                                        dict_label_to_tsv_file['protein'].writerow(dict_protein)

                                                    # snp-protein rela
                                                    if spdi['deleted_sequence'] != spdi['inserted_sequence']:
                                                        if (snp_id, protein_id) not in dict_rela_label_to_pairs[
                                                            'snp_protein']:
                                                            dict_snp_protein['protein_id'] = protein_id
                                                            dict_rela_label_to_pairs['snp_protein'].add(
                                                                (snp_id, protein_id))
                                                            add_information_from_one_dict_to_another_and_prepare_as_string(
                                                                spdi,
                                                                dict_snp_protein,
                                                                'deleted_sequence')
                                                            add_information_from_one_dict_to_another_and_prepare_as_string(
                                                                spdi,
                                                                dict_snp_protein,
                                                                'inserted_sequence')
                                                            add_information_from_one_dict_to_another_and_prepare_as_string(
                                                                spdi,
                                                                dict_snp_protein,
                                                                'position')
                                                            dict_label_to_tsv_file['snp_protein'].writerow(
                                                                dict_snp_protein)
                                                # elif 'frameshift' in protein['variant']:
                                                else:
                                                    frameshift = protein['variant']['frameshift']
                                                    protein_id = frameshift['seq_id']
                                                    # snp protein rela from frameshift
                                                    if (snp_id, protein_id) not in dict_rela_label_to_pairs[
                                                        'snp_protein']:
                                                        dict_snp_protein['protein_id'] = protein_id
                                                        add_information_from_one_dict_to_another_and_prepare_as_string(
                                                            frameshift,
                                                            dict_snp_protein,
                                                            'position')
                                                        dict_label_to_tsv_file['snp_protein'].writerow(dict_snp_protein)

                                                # rna protein relationship
                                                if (rna_id, protein_id) not in dict_rela_label_to_pairs['rna_protein']:
                                                    dict_rela_label_to_pairs['rna_protein'].add((rna_id, protein_id))
                                                    dict_rna_protein = {'rna_id': rna_id, 'protein_id': protein_id}
                                                    dict_label_to_tsv_file['rna_protein'].writerow(dict_rna_protein)
            continue

        # this has only the information from before but are not in the current
        # this do not mak sense to included this information
        if key == 'lost_obs_movements':
            continue
            # if len(value) > 0:
            # print(snp_id)
            # print(value)
            # print(dict_node)

        if key == 'present_obs_movements':
            # print(dict_node)
            for observed_movement in value:
                for info_dictionary in observed_movement['component_ids']:
                    prepare_own_set(info_dictionary, dict_node)

                dict_observation_spdi = observed_movement['observation']
                combine_spdi_to_string(dict_observation_spdi, dict_node)

                dict_allele_in_current_release = observed_movement['allele_in_cur_release']
                if dict_allele_in_current_release['deleted_sequence'] != dict_allele_in_current_release[
                    'inserted_sequence']:
                    add_information_from_one_dict_to_another(dict_allele_in_current_release, dict_node,
                                                             'seq_id')
                    add_information_from_one_dict_to_another(dict_allele_in_current_release, dict_node,
                                                             'deleted_sequence')
                    add_information_from_one_dict_to_another(dict_allele_in_current_release, dict_node,
                                                             'inserted_sequence')
                    add_information_from_one_dict_to_another(dict_allele_in_current_release, dict_node, 'position')

                add_information_from_one_dict_to_another(observed_movement, dict_node, 'other_rsids_in_cur_release')

                # add_information_from_one_dict_to_another(observed_movement, dict_node, 'last_added_to_this_rs')
                # print(observed_movement)
            continue

        if key in ['withdrawn_snapshot_data', 'merged_snapshot_data', 'unsupported_snapshot_data']:
            counter_not_used_nodes += 1
            return

        if key == 'nosnppos_snapshot_data':
            print(key)
            print(value)

    prepare_dict_node_to_be_string(dict_node)
    if dict_node['identifier'] in set_of_unique_snp_ids:
        print('double',dict_node['identifier'] )
        return
    set_of_unique_snp_ids.add(dict_node['identifier'])
    dict_label_to_tsv_file['snp'].writerow(dict_node)


def prepare_snp_file():
    """
    prepare snp tsv file and cypher query
    :return:
    """
    if not 'snp' in dict_label_to_tsv_file:
        # #the node tsv file for generating snp nodes
        file_name = generate_csv_file_and_add_to_dictionary('snp', header_snp)

        generate_cypher_queries(file_name, 'snp', header_snp, header_snp_list)


def run_through_list_of_nodes_as_json_string(path_directory, path_data, json_file, chr):
    """
    if not snp in dictionary label to tsv then generate file and cypher query. Run through all lines in json file and
    parse the data
    :param path_directory:
    :param path_data:
    :param json_file:
    :param chr:
    :return:
    """
    global path_to_data, path_of_directory
    path_of_directory = path_directory
    path_to_data = path_data

    if not 'snp' in dict_label_to_tsv_file:
        # #the node tsv file for generating snp nodes
        file_name = generate_csv_file_and_add_to_dictionary('snp', header_snp)

        generate_cypher_queries(file_name, 'snp', header_snp, header_snp_list)

    counter = 0
    for line in json_file:
        counter += 1
        # if counter == 15727:
        #     print('huhu')

        # print(json_string)
        data = ujson.loads(line)
        prepare_json_information_to_tsv(data, chr)
        # prepare_json_information_to_tsv(line, chr)
        if counter % 10000 == 0:
            print(counter)
            print(datetime.datetime.now())
