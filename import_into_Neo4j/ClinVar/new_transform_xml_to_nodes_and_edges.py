import csv
import datetime
import gzip
import json
import os.path
import re
import sys
from typing import Dict, List, Union

sys.path.append("../..")
import pharmebinetutils

import lxml.etree as etree

# dictionary of trait set
dict_trait_sets = {}

# dictionary of trait
dict_traits = {}

# dictionary of relationships
dict_edges = {}

# dictionary of relationship types combination to tsv
dict_edge_types_to_tsv = {}

# trait set type to trait set node
dict_trait_set_type_dictionary = {}

# trait type to trait set node
dict_trait_type_dictionary = {}

# dictionary trait rela
dict_edge_traits = {}

# trait set type to tsv
dict_trait_set_typ_to_tsv = {}

# trait set type to tsv
dict_trait_typ_to_tsv = {}

# dictionary relationship counter for each pair
dict_rela_type_pair_to_count = {}

edge_information = ['variant_id', 'trait_set_id', 'title', 'assertion', 'review_status', 'observations',
                    'citations', 'attributes', 'study_description', 'comments', 'study_name', 'variation_attributes',
                    'variation_rela', 'accession_clinvar', 'xrefs', 'citations_info', 'clinical_significance',
                    'germline_classification', 'somatic_clinicalImpact', 'noClassification',
                    'oncogenicity_classification', 'accession_clinvar', 'general_type', 'trait_set_type']

# dictionary of measure set properties which are list
dict_measure_set_properties_which_are_sets = set()

# dictionary of genotype properties which are list
dict_genotype_properties_which_are_list = set()


def prepare_for_file_name_and_label(type_name):
    """
    prepare string for file name and label
    :param type_name: string
    :return: string
    """
    return type_name.replace(' ', '_').replace(',', '')


def for_citation_extraction_to_list(node, dict_to_use=None):
    """
    prepare the citation information
    """
    all_citation = []
    all_pubmeds = []
    for citation in node.iterfind('Citation'):
        citation_info = {}
        for id in citation.iterfind('ID'):
            citation_info[id.get('Source')] = id.text
        check_for_information_and_add_to_dictionary_with_extra_name('URL', citation, citation_info, name='url')
        check_for_information_and_add_to_dictionary_with_extra_name('CitationText', citation, citation_info,
                                                                    name='citation_text')
        if 'PubMed' in citation_info:
            all_pubmeds.append(citation_info['PubMed'])
        all_citation.append(citation_info)

    if dict_to_use is not None:
        if len(all_citation) > 0:
            if 'citations_info' not in dict_to_use:
                dict_to_use['citations_info'] = all_citation
            else:
                dict_to_use['citations_info'] = all_citation.extend(dict_to_use['citations_info'])
        if len(all_pubmeds) > 0:
            if 'citations' not in dict_to_use:
                dict_to_use['citations'] = all_pubmeds
            else:
                dict_to_use['citations'] = all_pubmeds.union(dict_to_use['citations'])
        return dict_to_use

    return all_citation


def preparation_of_xrefs_variation(node, dict_to_use):
    """
    preparation of xrefs for variation file
    """
    xref_list = node.find('XRefList')
    if xref_list is not None:
        all_xrefs = set()
        for xref in xref_list.iterfind('XRef'):
            all_xrefs.add(xref.get('DB') + ':' + xref.get('ID'))
        if len(all_xrefs) > 0:
            dict_to_use['xrefs'] = list(all_xrefs)


def preparation_of_xrefs(node, dict_to_use):
    """
    preparation of xrefs
    """
    all_xrefs = set()
    for xref in node.iterfind('XRef'):
        all_xrefs.add(xref.get('DB') + ':' + xref.get('ID'))
    if dict_to_use is not None:
        if len(all_xrefs) > 0:
            if 'xrefs' not in dict_to_use:
                dict_to_use['xrefs'] = list(all_xrefs)
            else:
                dict_to_use['xrefs'] = list(all_xrefs.union(dict_to_use['xrefs']))
        return dict_to_use

    return list(all_xrefs)


def for_multiple_tags_at_one(node, tag):
    """
    for multiple information
    """
    list_of_this_tags_outputs = []
    for comment in node.iterfind(tag):
        list_of_this_tags_outputs.append(comment.text.replace('"', '\''))
    return list_of_this_tags_outputs


def get_xrefs_wih_other_tag_system(node):
    """
    get external reference with other tags
    """
    result = node.find('ExternalID')
    list_xrefs = []
    if result is not None:
        if 'Type' in result:
            external_id = result.get('DB') + ':' + result.get('ID') + '(' + result.get('Type') + ')'
        else:
            external_id = result.get('DB') + ':' + result.get('ID')
        list_xrefs.append(external_id)
    return list_xrefs


def prepare_clinical_significance(node):
    """
    In new version clinical significance is called classification
    """
    clinical_significance = node.find('Classification')
    if clinical_significance is not None:
        date = clinical_significance.get('DateLastEvaluated')
        dict_significance = {'date': date} if date is not None else {}
        check_for_information_and_add_to_dictionary_with_extra_name('ReviewStatus', clinical_significance,
                                                                    dict_significance,
                                                                    name='review_status')

        check_for_information_and_add_to_dictionary_with_extra_name('Description', clinical_significance,
                                                                    dict_significance,
                                                                    name='description')

        check_for_information_and_add_to_dictionary_with_extra_name('Explanation', clinical_significance,
                                                                    dict_significance,
                                                                    name='explanation')

        preparation_of_xrefs(clinical_significance, dict_significance)

        for_citation_extraction_to_list(clinical_significance, dict_significance)

        comment_dict = for_multiple_tags_at_one(clinical_significance, 'Comment')
        build_low_dict_into_higher_dict(dict_significance, comment_dict, 'comments')

        # todo external id, but if have to check what it stands for !
        xrefs = get_xrefs_wih_other_tag_system(clinical_significance)
        if len(xrefs) > 0:
            dict_significance['xrefs'] = xrefs

        return True, dict_significance
    return False, {}


def prepare_set_element(node, set_element_type):
    """
    prepare set_element
    """
    dict_all_elements = {}
    for element in node.iterfind(set_element_type):
        element_value = element.find('ElementValue')
        type = element_value.get('Type')
        value = element_value.text
        if type not in dict_all_elements:
            dict_all_elements[type] = set()
        dict_all_elements[type].add(value)

        # for_citation_extraction_to_list(element, dict_one_element)
        # preparation_of_xrefs(element, dict_one_element)
        #
        # comment_dict = perare_comments(element)
        # build_low_dict_into_higher_dict(dict_one_element, comment_dict, 'comments')
        #
    return dict_all_elements


def check_for_information_and_add_to_dictionary_with_extra_name(tag, node, dictionary, name=None, gets=None):
    """
    get information from node and put in dictionary
    """
    result = node.find(tag)
    if result is not None:
        value = result.text
        if value is not None:
            value = value.replace('"', '\'')

        if name is None and gets is not None:
            dictionary[result.get(gets)] = value
        elif name is not None and gets is None:
            dictionary[name] = value
        else:
            sys.exit('I have to think about this case')
    # return list_to_add


def prepare_specific_classification_information(node, review_status_list, node_property_name, dictionary):
    """
    extract from the different classes of classification (germline_classification, oncogenicity_classification, NoClassification, somatic_clinicalImpact)
    the review status and additional information
    """
    if node is not None:
        # TODO extract more information?
        review_status = node.find('ReviewStatus').text
        review_status_list.add(review_status)
        description = node.find('Description')
        if description is not None:
            description = description.text
        else:
            description = ''
        dictionary[node_property_name] = review_status + ':' + description


def prepareClassificationInformation(node, dictionary):
    """
    get information from node and put in dictionary
    """
    classification = node.find('Classifications')
    review_status_list = set()
    germline_classification = classification.find('GermlineClassification')
    prepare_specific_classification_information(germline_classification, review_status_list, 'germline_classification',
                                                dictionary)

    oncogenicity_classification = classification.find('OncogenicityClassification')
    prepare_specific_classification_information(oncogenicity_classification, review_status_list,
                                                'oncogenicity_classification', dictionary)

    no_classification = classification.find('NoClassification')
    prepare_specific_classification_information(no_classification, review_status_list, 'noClassification', dictionary)

    # TODO multiple possible
    somatic_clinical_impact = classification.find('SomaticClinicalImpact')
    prepare_specific_classification_information(somatic_clinical_impact, review_status_list, 'somatic_clinicalImpact',
                                                dictionary)
    dictionary['review_status'] = review_status_list


def check_for_information_and_add_to_list_with_extra_name(tag, node, list_of_infos, name=None, gets=None):
    """
    get information from node and put in list
    """
    result = node.find(tag)
    if result is not None:
        value = result.text
        if value is None:
            set_of_values = set()
            for key in result.keys():
                if key != gets:
                    set_of_values.add(key)
            if len(set_of_values) == 1:
                value = result.get(set_of_values.pop())
            elif len(set_of_values) > 1:
                print(set_of_values)
                print(gets)
                # sys.exit('ohno')

        if name is None and gets is not None and value is not None:
            list_of_infos.append(result.get(gets) + ':' + value)
        elif name is not None and gets is None:
            list_of_infos.append(name + ':' + value)
        elif name is None and gets is None and value is not None:
            list_of_infos.append(value)
        elif gets is not None and value is None:
            list_of_infos.append(result.get(gets))
        else:
            sys.exit('should not exist ;)')


def build_low_dict_into_higher_dict_with_list(top_dict, lower_dict, name, names):
    """
    higher into lower but with list of elements
    """
    if len(lower_dict) > 0:
        if names not in top_dict:
            top_dict[names] = []
        top_dict[names].append({name: lower_dict})


def build_low_dict_into_higher_dict(top_dict, lower_dict, name):
    """
    add set to a set but transform into string before
    """
    if len(lower_dict) > 0:
        if name not in top_dict:
            top_dict[name] = lower_dict
        else:
            top_dict[name] = [top_dict[name], lower_dict]


def add_name_and_synonyms_to_dict(node, dictionary, variation_id=None):
    """
    Add name to and synonyms to dictionary
    """
    dict_names = prepare_set_element(node, 'Name')
    synonyms = set()
    for type, set_names in dict_names.items():
        if type != 'Preferred':
            synonyms = synonyms.union(set_names)
    synonyms = set(synonyms)
    if 'Preferred' in dict_names:
        name_s = dict_names['Preferred']
        if 'name' in dictionary:
            name = name_s.pop()
            if name != dictionary['name']:
                synonyms.add(name)
        else:
            dictionary['name'] = name_s.pop()
        if len(name_s) > 0:
            for name in name_s:
                synonyms.add(name)

    elif len(synonyms) > 0:
        if 'name' not in dictionary:
            dictionary['name'] = synonyms.pop()

    if len(synonyms) > 0:
        if 'synonyms' not in dictionary:
            dictionary['synonyms'] = list(synonyms)
        else:
            dictionary['synonyms'] = list(synonyms.union(dictionary['synonyms']))


'''
prepare symbol
'''


def prepare_symbol(node, dictionary, dictionary_name):
    dict_elements = prepare_set_element(node, 'Symbol')
    element_list = set()
    for type, element in dict_elements.items():
        element_list = element_list.union(element)
    # element_list= [element_list.union(x) for type, x in dict_elements.items()]
    if len(dict_elements) > 0:
        if dictionary_name not in dictionary:
            dictionary[dictionary_name] = list(element_list)
        else:
            dictionary[dictionary_name] = list(element_list.union(dictionary[dictionary_name]))


'''
add dictionary to list with an name as dictionary
'''


def add_dictionary_to_a_list_as_dict_with_a_name(list, value, name):
    list.append({name: value})


'''
add list to dictionary with label but first checking if it is not empty 
'''


def add_list_to_dict_if_not_empty(list_of_elements, dictionary, name):
    if len(list_of_elements) > 0:
        dictionary[name] = list_of_elements


'''
add element to dictionary with value from node.get
'''


def add_element_to_dictionary_with_get(dictionary, node, dictionary_property_name, get_name):
    dictionary[dictionary_property_name] = node.get(get_name)


'''
work with sequence location and take only the current one and add to dictionary
'''


def add_current_sequence_location_to_dictionary(dictionary, node):
    for seq_location in node.iterfind('SequenceLocation'):
        if seq_location.get('AssemblyStatus') == 'current':
            dict_seq_location = {}
            for key, value in seq_location.items():
                split_key_for_capital_letters = re.findall('([A-Z][a-z]*)', key)
                if len(split_key_for_capital_letters) > 0:
                    key = '_'.join(split_key_for_capital_letters).lower()
                dict_seq_location[key] = value
            # dictionary['sequence_location'] = to_json_and_replace(dict_seq_location)
            dictionary['sequence_location'] = dict_seq_location


'''
preparation of attributes
'''


def preparation_attributions(node):
    list_attributes = set()
    for attribute in node.iterfind('AttributeSet'):
        list_attributes.add(attribute.find('Attribute').get('Type'))
    return list(list_attributes)


'''
preparation of attributes with get and value
'''


def preparation_attributes_with_get_and_value(node, list_attributes):
    for attribute in node.iterfind('AttributeSet'):
        check_for_information_and_add_to_list_with_extra_name('Attribute', attribute, list_attributes,
                                                              gets='Type')


# set of property which appears with different values
set_properties_with_different_values = set()
'''
fusion measure set (hope only variant) with single measure
'''


def fusion_of_them(node_dictionary, list_measures):
    for dict_measures in list_measures:
        for key, value in dict_measures.items():
            if key == 'allele_id':
                if value in dict_allele_id_to_variant_id:
                    print(value)
                    print('exist', dict_allele_id_to_variant_id[value])
                    print('new', node_dictionary['identifier'])
                    print('allele and variant id are not unique?')
                    dict_allele_id_to_variant_id[value].add(node_dictionary['identifier'])
                else:
                    dict_allele_id_to_variant_id[value] = set([node_dictionary['identifier']])
            if key not in node_dictionary:
                node_dictionary[key] = value
            else:
                if value != node_dictionary[key] and type(value) in [list, set]:
                    node_dictionary[key] = set(node_dictionary[key]).union(value)
                    if key not in set_properties_with_different_values:
                        set_properties_with_different_values.add(key)

    # del node_dictionary['measures']


'''
go through dictionary and prepare the values into strings and add all list values names to a set
'''


def perpare_dictionary_values(dictionary, specific_type, dict_type_s_to_list_property_list):
    if specific_type not in dict_type_s_to_list_property_list:
        dict_type_s_to_list_property_list[specific_type] = set()
    dict_properties_which_are_set = dict_type_s_to_list_property_list[specific_type]
    for type_part, value in dictionary.items():
        if type(value) in [list, set]:
            list_string = ''
            for part in value:
                if type(part) in [list, dict]:
                    list_string += to_json_and_replace(part) + '|'

                else:
                    list_string += part + '|'
            dictionary[type_part] = list_string[:-1]
            if type_part not in dict_properties_which_are_set:
                dict_properties_which_are_set.add(type_part)


'''
go through dictionary and prepare the values into strings and add all list values names to a set
'''


def perpare_dictionary_values_add_to_set(dictionary, set_properties_which_are_set_or_list, variant_id):
    for type_part, value in dictionary.items():
        if type(value) in [list, set]:
            list_string = ''
            for part in value:
                if type(part) in [list, dict]:
                    list_string += to_json_and_replace(part) + '|'

                else:
                    list_string += part + '|'
            dictionary[type_part] = list_string[:-1]
            set_properties_which_are_set_or_list.add(type_part)
        elif type(value) == dict:
            if 'date' in value and value['date'] == '2015-01-07' and 'citations_info' in value:
                print('problem?', variant_id, type_part, value)
                print(json.dumps(value))
            dictionary[type_part] = json.dumps(value)


'''
perpare the location information
'''


def preparation_location(node, dictionary_used):
    location = node.find('Location')
    if location is not None:
        check_for_information_and_add_to_dictionary_with_extra_name('CytogeneticLocation', location,
                                                                    dictionary_used,
                                                                    name='cytogenetic_location')

        add_current_sequence_location_to_dictionary(dictionary_used, location)

    check_for_information_and_add_to_dictionary_with_extra_name('Haploinsufficiency', node, dictionary_used,
                                                                name='haploinsufficiency')
    check_for_information_and_add_to_dictionary_with_extra_name('Triplosensitivity', node, dictionary_used,
                                                                name='triplo sensitivity')


'''
prepare the hgvs information and return the list with the information
'''


def prepare_hgvs(node):
    hgvs_list = []
    list_hgvs = node.find('HGVSlist')
    if list_hgvs is not None:
        for hgvs in list_hgvs.iterfind('HGVS'):
            dict_hgvs = {}
            nucleotide_expression = hgvs.find('NucleotideExpression')
            if nucleotide_expression is not None:
                check_for_information_and_add_to_dictionary_with_extra_name('Expression', nucleotide_expression,
                                                                            dict_hgvs,
                                                                            name='nucleotide expression')
            protein_expression = hgvs.find('ProteinExpression')
            if protein_expression is not None:
                check_for_information_and_add_to_dictionary_with_extra_name('Expression', protein_expression,
                                                                            dict_hgvs,
                                                                            name='protein expression')
            molecular_consequences = set()
            for consequence in hgvs.iterfind('MolecularConsequence'):
                molecular_consequences.add(consequence.get('Type'))
            if len(molecular_consequences) > 0:
                dict_hgvs['molecular_consequence'] = list(molecular_consequences)
            json_dump_hgvs = to_json_and_replace(dict_hgvs)
            hgvs_list.append(json_dump_hgvs)
    return hgvs_list


def to_json_and_replace(dictionary: Union[Dict, List]) -> str:
    """
    to json and replace
    """
    dump_dictionary = json.dumps(dictionary)
    return dump_dictionary.replace('\\"', '"')


def prepare_synonyms(node, dictionary):
    """
    prepare synonyms from clinvar variant
    """
    list_synonyms = set()
    other_names = node.find('OtherNameList')
    if other_names is not None:
        for name in other_names.iterfind('Name'):
            list_synonyms.add(name.text)
    if len(list_synonyms) > 0:
        dictionary['synonyms'] = list(list_synonyms)


'''
prepare functional consequence
'''


def prepare_functional_consequence(node):
    list_functional_consequences = []
    for functional_consequence in node.iterfind('FunctionalConsequence'):
        dict_consequence = {}
        dict_consequence['functional_consequence'] = functional_consequence.get('Value')
        for_citation_extraction_to_list(functional_consequence, dict_consequence)
        preparation_of_xrefs(functional_consequence, dict_consequence)
        comment_dict = for_multiple_tags_at_one(functional_consequence, 'Comment')
        build_low_dict_into_higher_dict(dict_consequence, comment_dict, 'comments')

        list_functional_consequences.append(dict_consequence)
    return list_functional_consequences


'''
prepare relationship between variation
'''


def prepare_rela_between_variations(node, variant_id, id_name, tag_name, from_type, to_type):
    for single_allele in node.iterfind(tag_name):
        single_variation_id = single_allele.get('VariationID')
        if not (from_type, to_type) in edge_between_variations:
            dict_rela_type_pair_to_count[(from_type, to_type)] = 0
            edge_between_variations[(from_type, to_type)] = set()
            file_name = path_of_clinvar_data + 'data/edge_' + prepare_for_file_name_and_label(
                from_type) + '_' + prepare_for_file_name_and_label(
                to_type) + '.tsv'
            file_edge = open(file_name, 'w', encoding='utf-8')
            csv_writer = csv.writer(file_edge, delimiter='\t')
            csv_writer.writerow([id_name, 'other_id'])
            dict_tsv_edge_variations[(from_type, to_type)] = csv_writer

            query = query_edge_variation % (

                prepare_for_file_name_and_label(from_type), id_name,
                prepare_for_file_name_and_label(to_type), 'other_id')
            query = pharmebinetutils.get_query_import('', file_name, query)
            cypher_file_edges.write(query)
        if (variant_id, single_variation_id) not in edge_between_variations[(from_type, to_type)]:
            dict_rela_type_pair_to_count[(from_type, to_type)] += 1
            edge_between_variations[(from_type, to_type)].add(
                (from_type, to_type))
            dict_tsv_edge_variations[(from_type, to_type)].writerow(
                [variant_id, single_variation_id])


'''
fill the list with single allels
'''


def get_all_single_allele_infos_and_add_to_list(node, variation_id=None):
    list_single = []
    specific_type = ''
    for single_allele in node.iterfind('SimpleAllele'):

        dict_single = {}

        check_for_information_and_add_to_dictionary_with_extra_name('VariantType', single_allele, dict_single,
                                                                    name='specific_type')
        specific_type = dict_single['specific_type']
        if 'Variant' not in dict_variation_to_node_ids:
            dict_variation_to_node_ids['Variant'] = {}
            dict_tsv_file_variation['Variant'] = {}
        if specific_type not in dict_variation_to_node_ids['Variant']:
            dict_specific_to_general_type[specific_type] = 'Variant'
            dict_variation_to_node_ids['Variant'][specific_type] = set()
            file_name = path_of_clinvar_data + 'data/' + prepare_for_file_name_and_label(specific_type) + '.tsv'
            file_type = open(file_name, 'w', encoding='utf-8')
            # csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=header_variation, escapechar="\\",
            #                                  doublequote=False)
            csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=header_variation, quotechar='"')
            csv_writer_type.writeheader()
            dict_tsv_file_variation['Variant'][specific_type] = csv_writer_type

        allele_id = single_allele.get('AlleleID')
        single_variation_id = single_allele.get('VariationID')
        # dict_allele_id_to_variant_id[allele_id]=variation_id
        dict_single['allele_id'] = allele_id

        if variation_id not in dict_variation_to_node_ids['Variant'][specific_type]:

            genes_list = single_allele.find('GeneList')
            if genes_list is not None:
                list_genes = []
                for gene in genes_list.iterfind('Gene'):
                    dict_gene = {}

                    preparation_location(gene, dict_gene)

                    dict_gene['gene_name'] = gene.get('FullName')
                    dict_gene['gene_id'] = gene.get('GeneID')
                    gene_symbol = gene.get('Symbol') if 'Symbol' in gene else ''
                    if gene_symbol != '':
                        dict_gene['symbol'] = gene_symbol
                    list_genes.append(dict_gene)
                dict_single['genes'] = to_json_and_replace(list_genes)

            preparation_location(single_allele, dict_single)

            prepare_synonyms(single_allele, dict_single)

            hgvs_list = prepare_hgvs(single_allele)
            build_low_dict_into_higher_dict(dict_single, hgvs_list, 'hgvs_json_list')

            allele_frequencies = single_allele.find('AlleleFrequencyList')
            list_of_frequencies = []
            if allele_frequencies is not None:
                for allele_frequency in allele_frequencies.iterfind('AlleleFrequency'):
                    list_of_frequencies.append(
                        {'frequency': allele_frequency.get('Value'), 'source': allele_frequency.get('Source')})
                add_list_to_dict_if_not_empty(list_of_frequencies, dict_single, 'frequencies')

            global_minor_allele_frequency = single_allele.find('GlobalMinorAlleleFrequency')
            if global_minor_allele_frequency is not None:
                dict_global_allele_frequency = {}
                add_element_to_dictionary_with_get(dict_global_allele_frequency, global_minor_allele_frequency,
                                                   'frequency', 'Value')
                add_element_to_dictionary_with_get(dict_global_allele_frequency, global_minor_allele_frequency,
                                                   'source', 'Source')
                add_element_to_dictionary_with_get(dict_global_allele_frequency, global_minor_allele_frequency,
                                                   'minor_allele', 'MinorAllele')
                dict_single['global_minor_allele_frequency'] = to_json_and_replace(dict_global_allele_frequency)

            list_functional_consequences = prepare_functional_consequence(single_allele)
            add_list_to_dict_if_not_empty(list_functional_consequences, dict_single, 'functional_consequences')

            preparation_of_xrefs_variation(single_allele, dict_single)
            comment_dict = for_multiple_tags_at_one(single_allele, 'Comment')
            build_low_dict_into_higher_dict(dict_single, comment_dict, 'comments')
            list_single.append(dict_single)

        else:
            return True, [], ''
    return False, list_single, specific_type


'''
observation information preparation
'''


def observation_information_preparation(node, dict_used):
    # check if this relationship appears at least in human
    found_human = False
    observation_list = []
    for observation in node.iterfind('ObservedIn'):
        observation_dict_one = {}
        sample = observation.find('Sample')
        sample_information = {}
        species = sample.find('Species')
        if species is not None and species.text is not None:
            species_text = species.text.lower()
            if species_text == 'human' or species_text == 'homo sapiens':
                found_human = True
            else:
                if species_text not in set_of_species:
                    print(species_text)
                    print('other than human')
                    print(node.get('ID'))
                    set_of_species.add(species_text)
                # sys.exit('other the human')

        check_for_information_and_add_to_dictionary_with_extra_name('Origin', sample, sample_information,
                                                                    name='origin')

        check_for_information_and_add_to_dictionary_with_extra_name('SomaticVariantInNormalTissue', sample,
                                                                    sample_information,
                                                                    name='somatic_variant_in_normal_tissue')

        check_for_information_and_add_to_dictionary_with_extra_name('SomaticVariantAlleleFraction', sample,
                                                                    sample_information,
                                                                    name='somatic_variant_allele_fraction')

        for age in sample.iterfind('Age'):
            sample_information['Age ' + age.get('Type')] = age.text + ' ' + age.get('age_unit')

        check_for_information_and_add_to_dictionary_with_extra_name('NumberTested', sample, sample_information,
                                                                    name='number_tested')
        check_for_information_and_add_to_dictionary_with_extra_name('NumberMales', sample, sample_information,
                                                                    name='number_tested_males')
        check_for_information_and_add_to_dictionary_with_extra_name('NumberFemales', sample, sample_information,
                                                                    name='number_tested_females')
        check_for_information_and_add_to_dictionary_with_extra_name('NumberChrTested', sample,
                                                                    sample_information,
                                                                    name='number_tested_children')
        check_for_information_and_add_to_dictionary_with_extra_name('GeographicOrigin', sample,
                                                                    sample_information,
                                                                    name='geographic_origin')

        check_for_information_and_add_to_dictionary_with_extra_name('Ethnicity', sample, sample_information,
                                                                    name='ethnicity')

        for_citation_extraction_to_list(sample, sample_information)
        preparation_of_xrefs(sample, sample_information)

        comment_dict = for_multiple_tags_at_one(sample, 'Comment')
        build_low_dict_into_higher_dict(sample_information, comment_dict, 'comments')
        build_low_dict_into_higher_dict(observation_dict_one, sample_information, 'sample')

        method_list = []
        for method in observation.iterfind('Method'):
            result = method.find('MethodType')
            if result is not None:
                value = result.text
                method_list.append(value)
        if len(method_list) > 0:
            observation_dict_one['methods'] = method_list

        observed_data_set = {}
        for observed_data in observation.iterfind('ObservedData'):
            one_observation = {}
            attribute = observed_data.find('Attribute')
            one_observation[attribute.get('Type')] = attribute.text
            for_citation_extraction_to_list(observed_data, one_observation)
            preparation_of_xrefs(observed_data, one_observation)
            comment_dict = for_multiple_tags_at_one(observation, 'Comment')
            build_low_dict_into_higher_dict(one_observation, comment_dict, 'comments')
            if len(one_observation) > 1 and 'Description' in one_observation and 'citations' in one_observation:
                del one_observation['Description']

            build_low_dict_into_higher_dict_with_list(observation_dict_one, one_observation, 'observation_data',
                                                      'observation_data_multiple')

        # build_low_dict_into_higher_dict(observation_dict_one, observed_data_set, 'observation_data_multiple')

        co_occurrences_set = {}
        for co_occurrence in observation.iterfind('Co-occurrenceSet'):
            # print('co-occurences')

            one_co_occurrence = {}
            check_for_information_and_add_to_dictionary_with_extra_name('Zygosity', co_occurrence,
                                                                        one_co_occurrence,
                                                                        name='zygosity')
            check_for_information_and_add_to_dictionary_with_extra_name('Count', co_occurrence,
                                                                        one_co_occurrence,
                                                                        name='count')
            allels = {}
            for allele in co_occurrence.iterfind('AlleleDescSet'):
                one_allel_set = {}
                check_for_information_and_add_to_dictionary_with_extra_name('RelativeOrientation', allele,
                                                                            one_allel_set,
                                                                            name='relative_orientation')
                check_for_information_and_add_to_dictionary_with_extra_name('Zygosity', allele, one_allel_set,
                                                                            name='zygosity')
                check_for_information_and_add_to_dictionary_with_extra_name('Name', allele, one_allel_set,
                                                                            name='name')
                found_clinical, dict_significance = prepare_clinical_significance(allele)
                if found_clinical:
                    build_low_dict_into_higher_dict(one_allel_set, dict_significance, 'clinical_singnificant')

                build_low_dict_into_higher_dict_with_list(one_co_occurrence, one_allel_set, 'allel', 'allels')
            # build_low_dict_into_higher_dict(one_co_occurrence, allels, 'allels')

            build_low_dict_into_higher_dict_with_list(observation_dict_one, one_co_occurrence, 'co-occurrence',
                                                      'co-occurrences')
        # build_low_dict_into_higher_dict(observation_dict_one,co_occurrences_set,'co-occurrences')
        add_dictionary_to_a_list_as_dict_with_a_name(observation_list, observation_dict_one, 'observation')

    # build_low_dict_into_higher_dict_with_list(observation_list, observation_dict_one, 'observation')
    # add_dictionary_to_a_list_as_dict_with_a_name(observation_list, observation_dict_one, 'observation')
    dict_used['observations'] = observation_list
    return found_human


def prepareMeasureOrGenotypeInfo(assertion, dict_to_add):
    # measureSet or genotype
    measure_set = assertion.find('MeasureSet')
    genotype = assertion.find('GenotypeSet')
    general_type = ""
    variant_id = ""
    if measure_set is not None:
        type_measure_set = measure_set.get('Type')
        identifier = measure_set.get('ID')
        variant_id = identifier
        accession = measure_set.get('Acc')
        list_attributes_variations = []

        if type_measure_set == 'Variant':
            variation_rela = []

            general_type = type_measure_set
            # if variant_id not in dict_variation_to_node_ids[type_measure_set][measure_set.find('Measure').get('Type')]:
            #     print('variant id not in list')
            #     print(variant_id)
            for measure in measure_set.iterfind('Measure'):

                preparation_attributes_with_get_and_value(measure, list_attributes_variations)

                for measure_rela in measure.iterfind('MeasureRelationship'):
                    dict_rela = {}
                    add_name_and_synonyms_to_dict(measure_rela, dict_rela)
                    prepare_symbol(measure_rela, dict_rela, 'symbols')
                    preparation_of_xrefs(measure_rela, dict_rela)
                    dict_rela_optimised = {}
                    for key, value in dict_rela.items():
                        if type(value) == str:
                            dict_rela_optimised[key] = value
                        elif type(value) == list:
                            dict_rela_optimised[key] = [t for t in value]
                        elif value is None:
                            print("problem NONE!!!!!!!!!!!!!!!", key, value)
                        else:
                            print(type(value), value)
                            value = {key_v: value_v for key_v, value_v in value.items()}
                            dict_rela_optimised[key] = value
                    variation_rela.append(dict_rela_optimised)
                if len(list_attributes_variations) > 0:
                    dict_to_add['variation_attributes'] = "|".join(list_attributes_variations)
                if len(variation_rela) > 0:
                    dict_to_add['variation_rela'] = to_json_and_replace(variation_rela)



        else:
            general_type = dict_specific_to_general_type[
                type_measure_set] if type_measure_set in dict_specific_to_general_type else ''
            if variant_id not in dict_variation_to_node_ids[general_type][type_measure_set]:

                dict_haplotype = {}
                dict_haplotype['accession'] = measure_set.get('Acc')
                number_of_chr = measure_set.get('NumberOfChromosomes')
                if number_of_chr is not None:
                    dict_haplotype['number_of_chromosomes'] = number_of_chr
                add_name_and_synonyms_to_dict(measure_set, dict_haplotype)
                prepare_symbol(measure_set, dict_haplotype, 'symbols')

                for_citation_extraction_to_list(measure_set, dict_haplotype)
                preparation_of_xrefs(measure_set, dict_haplotype)

                comment_dict = for_multiple_tags_at_one(measure_set, 'Comment')
                build_low_dict_into_higher_dict(dict_haplotype, comment_dict, 'comments')

                dict_attributes_set = []

                if len(dict_attributes_set) > 0:
                    dict_haplotype['attributes'] = dict_attributes_set

                perpare_dictionary_values(dict_haplotype, type_measure_set, dict_type_to_list_property_list)

                dict_tsv_file_variation[general_type][type_measure_set].writerow(dict_haplotype)
                dict_variation_to_node_ids[general_type][type_measure_set].add(variant_id)

                for measure in measure_set.iterfind('Measure'):
                    preparation_attributes_with_get_and_value(measure, list_attributes_variations)
                    measure_type = measure.get('Type')
                    allele_id = measure.get('ID')
                    if allele_id in dict_allele_id_to_variant_id:
                        for measure_id in dict_allele_id_to_variant_id[allele_id]:
                            if not (type_measure_set, measure_type) in edge_between_variations:
                                dict_rela_type_pair_to_count[(type_measure_set, measure_type)] = 0
                                edge_between_variations[(type_measure_set, measure_type)] = set()
                                file_name = path_of_clinvar_data + 'data/edge_' + prepare_for_file_name_and_label(
                                    type_measure_set) + '_' + prepare_for_file_name_and_label(
                                    measure_type) + '.tsv'
                                file_edge = open(file_name, 'w', encoding='utf-8')
                                csv_writer = csv.writer(file_edge, delimiter='\t')
                                csv_writer.writerow(['haplo', 'other_id'])
                                dict_tsv_edge_variations[(type_measure_set, measure_type)] = csv_writer

                                query = query_edge_variation % (
                                    prepare_for_file_name_and_label(type_measure_set), 'haplo',
                                    prepare_for_file_name_and_label(measure_type), 'other_id')
                                query = pharmebinetutils.get_query_import('',
                                                                          file_name,
                                                                          query)
                                cypher_file_edges.write(query)
                            if (variant_id, measure_id) not in edge_between_variations[
                                (type_measure_set, measure_type)]:
                                dict_rela_type_pair_to_count[(type_measure_set, measure_type)] += 1
                                edge_between_variations[(type_measure_set, measure_type)].add(
                                    (type_measure_set, measure_type))
                                dict_tsv_edge_variations[(type_measure_set, measure_type)].writerow(
                                    [variant_id, measure_id])
                    else:
                        print(variant_id)
                        print(allele_id)
                        print(type_measure_set)
                        print(measure_type)
                        print('allele id which do not exist in clinvar variationa?')
                        # sys.exit('allele id which do not exist in clinvar variationa?')

    elif genotype is not None:
        identifier = genotype.get('ID')
        type_genotype = genotype.get('Type')
        accession = genotype.get('Acc')

        general_type = dict_specific_to_general_type[
            type_genotype] if type_genotype in dict_specific_to_general_type else ''

        variant_id = identifier
    dict_to_add["variant_id"] = variant_id if variant_id else ""
    dict_to_add['general_type'] = general_type


def prepareTraitSets(assertion, dict_info):
    trait_set = assertion.find('TraitSet')
    trait_set_id = trait_set.get('ID')
    trait_set_type = trait_set.get('Type')
    if trait_set_id is None:
        return

    if not trait_set_type in dict_trait_set_type_dictionary:
        dict_trait_set_type_dictionary[trait_set_type] = set()
        file_name = path_of_clinvar_data + 'data/trait_set_' + trait_set_type + '.tsv'
        writer = open(file_name, 'w', encoding='utf-8')
        # csv_writer = csv.DictWriter(writer, delimiter='\t', fieldnames=list_head_trait, escapechar="\\",
        #                             doublequote=False)
        csv_writer = csv.DictWriter(writer, delimiter='\t', fieldnames=list_head_trait, quotechar='"')
        csv_writer.writeheader()
        dict_trait_set_typ_to_tsv[trait_set_type] = csv_writer

    if not trait_set_id in dict_trait_set_type_dictionary[trait_set_type]:
        dict_trait_set = {}

        for trait in trait_set.iterfind('Trait'):
            dict_trait = {}

            trait_type = trait.get('Type')
            trait_identifier = trait.get('ID')

            dict_trait['type'] = trait_type
            dict_trait['identifier'] = trait_identifier

            if (trait_set_type, trait_type) not in dict_edge_traits:
                dict_rela_type_pair_to_count[(trait_set_type, trait_type)] = 0
                dict_edge_traits[(trait_set_type, trait_type)] = set()
                file_name = path_of_clinvar_data + 'data/edge_' + prepare_for_file_name_and_label(
                    trait_set_type) + '_' + prepare_for_file_name_and_label(trait_type) + '.tsv'
                file_edge = open(file_name, 'w', encoding='utf-8')
                csv_writer = csv.writer(file_edge, delimiter='\t')
                csv_writer.writerow(['trait_set_id', 'trait_id'])
                dict_tsv_edge_variations[(trait_set_type, trait_type)] = csv_writer

                query = query_edge_variation % (
                    'trait_set_' + prepare_for_file_name_and_label(trait_set_type),
                    'trait_set_id', 'trait_' + prepare_for_file_name_and_label(trait_type), 'trait_id')
                query = pharmebinetutils.get_query_import('', file_name, query)
                cypher_file_edges.write(query)
            if (trait_set_id, trait_identifier) not in dict_edge_traits[(trait_set_type, trait_type)]:
                dict_rela_type_pair_to_count[(trait_set_type, trait_type)] += 1
                dict_edge_traits[(trait_set_type, trait_type)].add(
                    (trait_set_id, trait_identifier))
                dict_tsv_edge_variations[(trait_set_type, trait_type)].writerow(
                    [trait_set_id, trait_identifier])

            if not trait_type in dict_trait_type_dictionary:
                dict_trait_type_dictionary[trait_type] = set()
                file_name = path_of_clinvar_data + 'data/trait_' + trait_type + '.tsv'
                writer = open(file_name, 'w', encoding='utf-8')
                # csv_writer = csv.DictWriter(writer, delimiter='\t', fieldnames=list_head_trait, escapechar="\\",
                #                             doublequote=False)
                csv_writer = csv.DictWriter(writer, delimiter='\t', fieldnames=list_head_trait, quotechar='"')
                csv_writer.writeheader()
                dict_trait_typ_to_tsv[trait_type] = csv_writer

            if trait_identifier not in dict_trait_type_dictionary[trait_type]:

                add_name_and_synonyms_to_dict(trait, dict_trait)
                prepare_symbol(trait, dict_trait, 'symbols')

                list_attributes = []
                preparation_attributes_with_get_and_value(trait, list_attributes)
                if len(list_attributes) > 0:
                    build_low_dict_into_higher_dict_with_list(dict_trait, list_attributes, 'attribute',
                                                              'attributes')

                list_trait_rela = []
                for trait_rela in trait.iterfind('TraitRelationship'):
                    combine_text = trait_rela.get('Type') + ':' + trait_rela.get('ID') if trait_rela.get(
                        'ID') else trait_rela.get('Type')
                    list_trait_rela.append(combine_text)
                if len(list_trait_rela) > 0:
                    dict_trait['trait_rela'] = list_trait_rela

                for_citation_extraction_to_list(trait, dict_trait)
                preparation_of_xrefs(trait, dict_trait)
                comment_dict = for_multiple_tags_at_one(trait, 'Comment')
                build_low_dict_into_higher_dict(dict_trait, comment_dict, 'comments')

                perpare_dictionary_values(dict_trait, trait_type, dict_type_to_list_property_list)

                dict_trait_typ_to_tsv[trait_type].writerow(dict_trait)
                dict_trait_type_dictionary[trait_type].add(trait_identifier)
            # build_low_dict_into_higher_dict_with_list(dict_trait_set, dict_trait, 'trait', 'traits')

        dict_trait_set['type'] = trait_set_type
        dict_trait_set['identifier'] = trait_set_id

        add_name_and_synonyms_to_dict(trait_set, dict_trait_set)
        prepare_symbol(trait_set, dict_trait_set, 'symbols')

        list_attributes = preparation_attributions(trait_set)
        build_low_dict_into_higher_dict_with_list(dict_trait_set, list_attributes, 'attribute', 'attributes')

        add_name_and_synonyms_to_dict(trait_set, dict_trait_set)
        prepare_symbol(trait_set, dict_trait_set, 'symbols')
        for_citation_extraction_to_list(trait_set, dict_trait_set)
        preparation_of_xrefs(trait_set, dict_trait_set)
        comment_dict = for_multiple_tags_at_one(trait_set, 'Comment')
        build_low_dict_into_higher_dict(dict_trait_set, comment_dict, 'comments')

        perpare_dictionary_values(dict_trait_set, trait_set_type, dict_type_to_list_property_list)

        dict_trait_set_type_dictionary[trait_set_type].add(trait_set_id)
        dict_trait_set_typ_to_tsv[trait_set_type].writerow(dict_trait_set)

    dict_info["trait_set_id"] = trait_set_id
    dict_info["trait_set_type"] = trait_set_type


# dictionary from specific typ to general type
dict_specific_to_general_type = {}

# dictionary for every pair which properties are lists
dict_edge_trait_set_variation_pair_to_list_of_list_properties = {}
# set for edge pairs which properties are lists
set_edge_trait_set_variation_pair_to_list_of_list_properties = set()

# head of all trait files
list_head_trait = ['identifier', 'accession', 'name', 'synonyms', 'symbols', 'comments',
                   'citations', 'citations_info', 'xrefs', 'attributes', 'traits', 'type', 'trait_rela']

# type with multiple measure
type_with_multiple_measure = set()

# dictionary allele id to variant id
dict_allele_id_to_variant_id = {}

# species set
set_of_species = set()

# all assertion
assertions_set = set()

# cypher file nodes
cypher_file_nodes = open('output/cypher_file_node.cypher', 'w', encoding='utf-8')

# cypher files edges
cypher_file_edges = open('output/cypher_file_edges.cypher', 'w', encoding='utf-8')

'''
extract relationships information from full release
'''


def get_information_from_full_release():
    print(datetime.datetime.now(), 'start download')

    filename = path_of_clinvar_data + 'ClinVarRCVRelease_00-latest.xml.gz'
    if not os.path.exists(filename):
        # url = 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/ClinVarFullRelease_00-latest.xml.gz'
        url = 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/RCV_release/ClinVarRCVRelease_00-latest.xml.gz'
        filename = pharmebinetutils.download_file(url, out=path_of_clinvar_data)
    file = gzip.open(filename, 'rb')
    print(datetime.datetime.now(), 'end download')
    # file = open('ClinVarFullRelease_00-latest.xml', 'rb')
    # file = open(path_of_clinvar_data + 'ClinVarRCVRelease_00-latest.xml/part.xml', 'rb')

    # counter not human
    counter_not_human = 0

    for event, node in etree.iterparse(file, events=('end',), tag='ClinVarSet'):
        # all edge information
        dict_edge_info = {}

        trait_set_id = ''
        variant_id = ''
        dict_edge_info['title'] = node.find('Title').text if node.find('Title') is not None else ''
        reference_assertion = node.find('ReferenceClinVarAssertion')

        # everything from reference
        if reference_assertion is not None:
            dict_reference_info = {}
            assertion = reference_assertion.find('Assertion').get('Type')
            dict_reference_info['assertion'] = assertion
            if assertion not in assertions_set:
                assertions_set.add(assertion)
            prepareClassificationInformation(reference_assertion, dict_reference_info)

            preparation_of_xrefs(reference_assertion, dict_reference_info)
            dict_reference_info['accession_clinvar'] = reference_assertion.find('ClinVarAccession').get('Acc')

            list_attributes = preparation_attributions(reference_assertion)
            build_low_dict_into_higher_dict_with_list(dict_reference_info, list_attributes, 'attribute', 'attributes')

            xrefs = get_xrefs_wih_other_tag_system(reference_assertion)
            if len(xrefs) > 0:
                dict_reference_info['xrefs'] = xrefs

            # check if this relationship appears at least in human
            found_human = observation_information_preparation(reference_assertion, dict_reference_info)
            if not found_human:
                counter_not_human += 1
                node.clear()
                continue

            # measureSet or genotype
            prepareMeasureOrGenotypeInfo(reference_assertion, dict_reference_info)

            # trait Set
            prepareTraitSets(reference_assertion, dict_reference_info)

            for_citation_extraction_to_list(reference_assertion, dict_reference_info)
            comment_dict = for_multiple_tags_at_one(reference_assertion, 'Comment')
            build_low_dict_into_higher_dict(dict_reference_info, comment_dict, 'comments')
            dict_edge_info["assertion"] = {assertion: dict_reference_info}

        clinvar_assertions = node.findall('ClinVarAssertion')
        dict_clinvar_assertion_to_assertion_info = {}
        if clinvar_assertions is not None:
            for clinvar_assertion in clinvar_assertions:
                assertion = clinvar_assertion.find('Assertion').get('Type')
                # if assertion != final_assertion:
                #     final_split = final_assertion.split(' ')
                #     assertion_split = assertion.split(' ')
                #     if not (final_split[0] == assertion_split[0] and final_split[-1] == assertion_split[-1]):
                #         print('different assertion')
                #         print(final_assertion)
                #         print(assertion)
                #         print(variant_id)
                #         print(trait_set_id)

                if assertion not in assertions_set:
                    assertions_set.add(assertion)

                if assertion not in dict_clinvar_assertion_to_assertion_info:
                    dict_clinvar_assertion_to_assertion_info[assertion] = []
                dict_clinvar_assertion = {}
                dict_clinvar_assertion['assertion'] = assertion
                dict_clinvar_assertion['accession_clinvar'] = clinvar_assertion.find('ClinVarAccession').get('Acc')
                xrefs = get_xrefs_wih_other_tag_system(clinvar_assertion)
                if len(xrefs) > 0:
                    dict_clinvar_assertion['xrefs'] = xrefs
                found_clinical, dict_significance = prepare_clinical_significance(clinvar_assertion)
                if found_clinical:
                    dict_clinvar_assertion['clinical_significance'] = dict_significance

                # check if this relationship appears at least in human
                observation_information_preparation(clinvar_assertion, dict_clinvar_assertion)

                # todo maybe measure set and trait set like up
                prepareMeasureOrGenotypeInfo(clinvar_assertion, dict_clinvar_assertion)

                # trait Set
                prepareTraitSets(clinvar_assertion, dict_clinvar_assertion)

                study_name = clinvar_assertion.find('StudyName')
                if study_name is not None:
                    dict_clinvar_assertion['study_name'] = study_name.text

                study_description = clinvar_assertion.find('StudyDescription')
                if not study_description is None:
                    dict_clinvar_assertion['study_description'] = study_description.text

                for_citation_extraction_to_list(clinvar_assertion, dict_clinvar_assertion)

                preparation_of_xrefs(clinvar_assertion, dict_clinvar_assertion)

                list_attributes = preparation_attributions(clinvar_assertion)
                build_low_dict_into_higher_dict_with_list(dict_clinvar_assertion, list_attributes, 'attribute',
                                                          'attributes')

                comment_dict = for_multiple_tags_at_one(clinvar_assertion, 'Comment')
                build_low_dict_into_higher_dict(dict_clinvar_assertion, comment_dict, 'comments')
                dict_clinvar_assertion_to_assertion_info[assertion].append(dict_clinvar_assertion)

        for assertion, list_of_dict_assertion_info in dict_clinvar_assertion_to_assertion_info.items():
            dict_pair_combined_assertion_info = {}
            for dict_clinvar_assertion in list_of_dict_assertion_info:
                variant_id = dict_clinvar_assertion['variant_id'] if 'variant_id' in dict_clinvar_assertion else None
                trait_set_id = dict_clinvar_assertion[
                    'trait_set_id'] if 'trait_set_id' in dict_clinvar_assertion else None
                if not variant_id or not trait_set_id:
                    continue
                if not (variant_id, trait_set_id) in dict_pair_combined_assertion_info:
                    dict_pair_combined_assertion_info[(variant_id, trait_set_id)] = {}
                dict_combined_assertion_info = dict_pair_combined_assertion_info[(variant_id, trait_set_id)]
                for key, value in dict_clinvar_assertion.items():
                    if not key in dict_combined_assertion_info:
                        dict_combined_assertion_info[key] = value
                    elif dict_combined_assertion_info[key] != value:
                        if key in ['accession_clinvar', 'clinical_significance', 'variation_attributes',
                                   'variation_rela', 'general_type', 'study_name']:
                            if type(dict_combined_assertion_info[key]) in [str, dict]:
                                dict_combined_assertion_info[key] = [dict_combined_assertion_info[key]]
                            dict_combined_assertion_info[key].append(value)
                        elif key in ['observations', 'xrefs', 'attributes', 'citations_info', 'citations', 'comments']:
                            dict_combined_assertion_info[key].extend(value)
                        else:
                            print(dict_combined_assertion_info[key])
                            print(value)
                            print(list_of_dict_assertion_info)
                            sys.exit('different assertion information ' + key)
            if assertion in dict_edge_info["assertion"]:
                variant_id = dict_edge_info["assertion"][assertion]["variant_id"]
                trait_set_id = dict_edge_info["assertion"][assertion]["trait_set_id"]
                if (variant_id, trait_set_id) in dict_pair_combined_assertion_info:
                    dict_combined_assertion_info = dict_pair_combined_assertion_info[(variant_id, trait_set_id)]
                    for key, value in dict_combined_assertion_info.items():
                        if key in dict_edge_info["assertion"][assertion]:

                            if dict_edge_info["assertion"][assertion][key] != value:
                                dict_edge_info["assertion"][assertion][key] = to_json_and_replace(
                                    {'reference_ClinVar_assertion': dict_edge_info["assertion"][assertion][key],
                                     'ClinVar_assertion': value})

                        else:
                            dict_edge_info["assertion"][assertion][key] = value

        if node[0].text == 'current':
            for assertion in dict_edge_info["assertion"]:
                final_assertion = '_'.join(assertion.split(' '))
                general_type = dict_edge_info["assertion"][assertion]['general_type']
                trait_set_type = dict_edge_info["assertion"][assertion]['trait_set_type']
                trait_set_id = dict_edge_info["assertion"][assertion]['trait_set_id']
                variant_id = dict_edge_info["assertion"][assertion]['variant_id']
                if (general_type, trait_set_type, final_assertion) not in dict_edges:
                    dict_rela_type_pair_to_count[(general_type, trait_set_type, final_assertion)] = 0
                    dict_edges[(general_type, trait_set_type, final_assertion)] = set()
                    file_name = path_of_clinvar_data + 'data/edges/edges_' + general_type + '_' + trait_set_type + '_' + final_assertion + '.tsv'
                    file = open(file_name, 'w', encoding='utf-8')
                    # csv_writer = csv.DictWriter(file, fieldnames=edge_information, delimiter='\t', escapechar="\\",
                    #                             doublequote=False)
                    csv_writer = csv.DictWriter(file, fieldnames=edge_information, delimiter='\t', quotechar='"')
                    csv_writer.writeheader()
                    dict_edge_types_to_tsv[(general_type, trait_set_type, final_assertion)] = csv_writer
                new_dict_edge_info = dict_edge_info.copy()
                for key, value in dict_edge_info["assertion"][assertion].items():
                    if key in new_dict_edge_info and key != "assertion":
                        print('ohno', key, new_dict_edge_info[key])
                        print(value)
                        sys.exit(");")
                    new_dict_edge_info[key] = value
                # if (variant_id, trait_set_id) not in dict_edges[(general_type, trait_set_type)]:
                dict_rela_type_pair_to_count[(general_type, trait_set_type, final_assertion)] += 1
                perpare_dictionary_values_add_to_set(new_dict_edge_info,
                                                     set_edge_trait_set_variation_pair_to_list_of_list_properties,
                                                     variant_id)
                dict_edges[((general_type, trait_set_type, final_assertion))].add((variant_id, trait_set_id))
                dict_edge_info['variant_id'] = variant_id
                dict_edge_info['trait_set_id'] = trait_set_id
                dict_edge_types_to_tsv[(general_type, trait_set_type, final_assertion)].writerow(new_dict_edge_info)
        node.clear()
    print('number of not human edges:', counter_not_human)


query_edge_variation_trait_set = ''' Match (g:%s_ClinVar{identifier:line.%s}), (o:%s_ClinVar{identifier:line.%s}) Create (g)-[:%s{'''
'''
prepare query for edges between variation and trait sets
'''


def perpare_query_for_edges():
    for (general_type, trait_set_type, final_assertion) in dict_edges.keys():
        final_assertion = '_'.join(final_assertion.split(' '))
        query = query_edge_variation_trait_set % (general_type, 'variant_id', 'trait_set_' + trait_set_type,
                                                  'trait_set_id', final_assertion)
        end_query = ' Set '
        for head in edge_information:
            if head in set_edge_trait_set_variation_pair_to_list_of_list_properties or head == 'attributes':
                query += head + ':split(line.' + head + ',"|"), '
            elif head in ['variant_id', 'trait_set_id', 'general_type', 'trait_set_type']:
                continue
            elif head.startswith('variation'):
                label = head.split('_')[1]
                if head == 'variation_attributes':
                    end_query += 'g.' + label + '=split(line.' + head + ',"|"), '
                else:
                    end_query += 'g.' + label + '=line.' + head + ', '
            else:
                query += head + ':line.' + head + ', '
        query = query[:-2] + '}]->(o)'
        query += end_query[:-2]
        query = pharmebinetutils.get_query_import(path_of_clinvar_data,
                                                  f'data/edges/edges_{general_type}_{trait_set_type}_{final_assertion}.tsv',
                                                  query)
        cypher_file_edges.write(query)


'''
prepare information on variation, haplotype or gene type
'''


def preparation_on_variation_haplo_or_genotype(interpreted_record, variant_id, dict_node, variation_type):
    genotype = interpreted_record.find('Genotype')
    haplotype = interpreted_record.find('Haplotype')
    # question is if this has one time ore then on single allel?
    found_already, list_single, specific_type = get_all_single_allele_infos_and_add_to_list(interpreted_record,
                                                                                            variant_id)
    if found_already:
        return True

    if len(list_single) == 1:
        fusion_of_them(dict_node, list_single)

        perpare_dictionary_values(dict_node, specific_type, dict_type_to_list_property_list)

        dict_tsv_file_variation['Variant'][specific_type].writerow(dict_node)
        dict_variation_to_node_ids['Variant'][specific_type].add(variant_id)

    if genotype is not None:
        if 'Genotype' not in dict_variation_to_node_ids:
            dict_variation_to_node_ids['Genotype'] = {}
            dict_tsv_file_variation['Genotype'] = {}
        variation_type = genotype.find('VariationType').text

        if variation_type not in dict_variation_to_node_ids['Genotype']:
            dict_specific_to_general_type[variation_type] = 'Genotype'
            dict_variation_to_node_ids['Genotype'][variation_type] = set()
            file_name = path_of_clinvar_data + 'data/' + prepare_for_file_name_and_label(variation_type) + '.tsv'
            file_type = open(file_name, 'w', encoding='utf-8')
            # csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=header_variation, escapechar="\\",
            #                                  doublequote=False)
            csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=header_variation, quotechar='"')
            csv_writer_type.writeheader()
            dict_tsv_file_variation['Genotype'][variation_type] = csv_writer_type

        prepare_rela_between_variations(genotype, variant_id, 'genotyp_id', 'SimpleAllele', 'Genotype', 'Variant')
        prepare_rela_between_variations(genotype, variant_id, 'genotyp_id', 'Haplotype', 'Genotype', 'Haplotype')

        if variant_id in dict_variation_to_node_ids['Genotype'][variation_type]:
            return True
        prepare_synonyms(genotype, dict_node)

        hgvs_list = prepare_hgvs(genotype)
        build_low_dict_into_higher_dict(dict_node, hgvs_list, 'hgvs_json_list')

        list_functional_consequences = prepare_functional_consequence(genotype)
        add_list_to_dict_if_not_empty(list_functional_consequences, dict_node, 'functional_consequences')

        preparation_of_xrefs_variation(genotype, dict_node)
        comment_dict = for_multiple_tags_at_one(genotype, 'Comment')
        build_low_dict_into_higher_dict(dict_node, comment_dict, 'comments')
        citation_list = genotype.find('CitationList')
        if citation_list is not None:
            for_citation_extraction_to_list(citation_list, dict_node)

        list_attributes = preparation_attributions(genotype)
        build_low_dict_into_higher_dict_with_list(dict_node, list_attributes, 'attribute', 'attributes')

        perpare_dictionary_values(dict_node, variation_type, dict_type_to_list_property_list)

        dict_tsv_file_variation['Genotype'][variation_type].writerow(dict_node)
        dict_variation_to_node_ids['Genotype'][variation_type].add(variant_id)

    elif haplotype is not None:
        if 'Haplotype' not in dict_variation_to_node_ids:
            dict_variation_to_node_ids['Haplotype'] = {}
            dict_tsv_file_variation['Haplotype'] = {}

        if variation_type not in dict_variation_to_node_ids['Haplotype']:
            dict_specific_to_general_type[variation_type] = 'Haplotype'
            dict_variation_to_node_ids['Haplotype'][variation_type] = set()
            file_name = path_of_clinvar_data + 'data/' + prepare_for_file_name_and_label(variation_type) + '.tsv'
            file_type = open(file_name, 'w', encoding='utf-8')
            # csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=header_variation, escapechar="\\",
            #                                  doublequote=False)
            csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=header_variation, quotechar='"')
            csv_writer_type.writeheader()
            dict_tsv_file_variation['Haplotype'][variation_type] = csv_writer_type

        prepare_rela_between_variations(haplotype, variant_id, 'haplo_id', 'SimpleAllele', 'Haplotype', 'Variant')

        if variant_id in dict_variation_to_node_ids['Haplotype'][variation_type]:
            return True

        prepare_synonyms(haplotype, dict_node)

        hgvs_list = prepare_hgvs(haplotype)
        build_low_dict_into_higher_dict(dict_node, hgvs_list, 'hgvs_json_list')

        list_functional_consequences = prepare_functional_consequence(haplotype)
        add_list_to_dict_if_not_empty(list_functional_consequences, dict_node, 'functional_consequences')

        preparation_of_xrefs_variation(haplotype, dict_node)
        comment_dict = for_multiple_tags_at_one(haplotype, 'Comment')
        build_low_dict_into_higher_dict(dict_node, comment_dict, 'comments')
        number_of_copies = haplotype.get('NumberOfCopies')
        if number_of_copies is not None:
            dict_node['number_of_copies'] = number_of_copies
        number_of_chromosomes = haplotype.get('NumberOfChromosomes')
        if number_of_chromosomes is not None:
            dict_node['number_of_chromosomes'] = number_of_chromosomes

        perpare_dictionary_values(dict_node, variation_type, dict_type_to_list_property_list)
        dict_tsv_file_variation['Haplotype'][variation_type].writerow(dict_node)
        dict_variation_to_node_ids['Haplotype'][variation_type].add(variant_id)
    return False


# to get all not found variants

# dictiontionary variation with group variant, haplotype, genotype to all entries
dict_variation_to_node_ids = {}

# edge_dictionary
edge_between_variations = {}

# dictionary of edges for the different types to tsv
dict_tsv_edge_variations = {}

# dict_type_to_property_list_which is a list
dict_type_to_list_property_list = {}

# head variation
header_variation = ['identifier', 'accession', 'name', 'allele_id', 'frequencies', 'global_minor_allele_frequency',
                    'xrefs', 'attributes', 'comments', 'genes', 'specific_type', 'synonyms', 'cytogenetic_location',
                    'hgvs_json_list',
                    'sequence_location', 'functional_consequences', 'number_of_chromosomes', 'review_status',
                    'citations', 'rela', 'global_minor_allel_frequency', 'genes', 'citations_info',
                    'germline_classification', 'somatic_clinicalImpact', 'noClassification',
                    'oncogenicity_classification']
list_header_measures = ['identifier', 'accession', 'name', 'synonyms', 'symbols', 'comments', 'measures',
                        'citations', 'xrefs', 'number_of_chromosomes', 'specific_type', 'allele_id',
                        'attributes',
                        'cytogenetic_location', 'measure_relationships', 'sequence_location', 'frequencies',
                        'global_minor_allele_frequency', 'genes', 'citations_info']
# query for variation edges
query_edge_variation = ''' Match (g:%s_ClinVar{identifier:line.%s}), (o:%s_ClinVar{identifier:line.%s}) Create (g)-[:has]->(o)'''

# dictionary tsv file for variation
dict_tsv_file_variation = {}

print(datetime.datetime.now())

'''
get the node information for variations
'''


def extract_node_info_for_variations():
    print(datetime.datetime.now(), 'start download')
    filename = path_of_clinvar_data + 'ClinVarVCVRelease_00-latest.xml.gz'
    if not os.path.exists(filename):
        url = 'https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/ClinVarVCVRelease_00-latest.xml.gz'
        path_combi = path_of_clinvar_data
        filename = pharmebinetutils.download_file(url, out=path_combi)

    file = gzip.open(filename, 'rb')
    print('end download', datetime.datetime.now())
    # file = open('ClinVarVariationRelease_2020-0302.xml', 'rb')
    # file = open('big_head_variation.xml', 'rb')
    for event, node in etree.iterparse(file, events=('end',), tag='VariationArchive'):
        dict_node = {}
        variant_id = node.get('VariationID')
        variation_type = node.get('VariationType')

        name = node.get('VariationName')
        accession = node.get('Accession')
        species = node.find('Species').text.lower()
        record_status = node.find('RecordStatus').text
        if record_status != 'current' or species != 'homo sapiens':
            node.clear()
            continue
        dict_node['identifier'] = variant_id
        dict_node['accession'] = accession
        dict_node['name'] = name

        # for interpretation
        interpreted_record = node.find('ClassifiedRecord')
        if interpreted_record is not None:
            prepareClassificationInformation(interpreted_record, dict_node)
            general_citation = interpreted_record.find('GeneralCitations')
            if general_citation is not None:
                for_citation_extraction_to_list(general_citation, dict_node)

            found = preparation_on_variation_haplo_or_genotype(interpreted_record, variant_id, dict_node,
                                                               variation_type)
            if found:
                node.clear()
                continue
        else:
            interpreted_record = node.find('IncludedRecord')
            prepareClassificationInformation(interpreted_record, dict_node)
            general_citation = interpreted_record.find('GeneralCitations')
            if general_citation is not None:
                for_citation_extraction_to_list(general_citation, dict_node)

            found = preparation_on_variation_haplo_or_genotype(interpreted_record, variant_id, dict_node,
                                                               variation_type)
            if found:
                node.clear()
                continue
        node.clear()


'''
prepare the content of the cypher file
'''


def prepare_content_of_cypher_file(type_variation, dict_set_of_property_which_are_list, query, list_head, extra_name):
    for head in list_head:
        if head in dict_set_of_property_which_are_list:
            query += head + ':split(line.' + head + ",'|'), "
        else:
            query += head + ':line.' + head + ', '
    query = query + ' license:"CC0 1.0"})'
    type_variation = prepare_for_file_name_and_label(type_variation)
    if extra_name is None:
        file_name = type_variation
        this_query = query % (type_variation)
    else:
        file_name = extra_name + type_variation
        this_query = query % (extra_name + type_variation)
    this_query = pharmebinetutils.get_query_import(path_of_clinvar_data, f'data/{file_name}.tsv',
                                                   this_query)
    cypher_file_nodes.write(this_query)


'''
generate node cyphers
'''


def generate_node_cypher(dict_variation_to_node_ids, list_head, extra_name=None, is_Varient=False):
    query = ''' Create (n:%s_ClinVar '''
    for key, value in dict_variation_to_node_ids.items():
        if type(value) == dict:
            if is_Varient and not key == "Variant":
                query_add = query + ':Variant_ClinVar '
            else:
                query_add = query
            new_query = query_add + ':' + prepare_for_file_name_and_label(key) + '_ClinVar {'
            for lower_key in value.keys():
                if lower_key != key:
                    list_of_sets_properties = dict_type_to_list_property_list[lower_key]
                    prepare_content_of_cypher_file(lower_key, list_of_sets_properties, new_query, list_head, extra_name)

                else:
                    list_of_sets_properties = dict_type_to_list_property_list[key]
                    prepare_content_of_cypher_file(key, list_of_sets_properties, query_add + ' {', list_head,
                                                   extra_name)
        else:
            list_of_sets_properties = dict_type_to_list_property_list[key]
            prepare_content_of_cypher_file(key, list_of_sets_properties, query + '{', list_head, extra_name)
        if extra_name is None:
            query_constraint = pharmebinetutils.prepare_index_query(prepare_for_file_name_and_label(key) + '_ClinVar',
                                                                    'identifier')
        else:
            query_constraint = pharmebinetutils.prepare_index_query(
                extra_name + prepare_for_file_name_and_label(key) + '_ClinVar', 'identifier')
        cypher_file_nodes.write(query_constraint)


def main():
    print(datetime.datetime.now())
    global path_of_clinvar_data
    if len(sys.argv) > 1:

        path_of_clinvar_data = sys.argv[1] + 'clinvar/'
    else:
        sys.exit('need a path to clinvar data')

    print('extract information from ClinVarVariationRelease')
    extract_node_info_for_variations()
    print(datetime.datetime.now())
    print(dict_specific_to_general_type)
    print('extract information from Full release')
    get_information_from_full_release()

    # measure set nodes queries
    generate_node_cypher(dict_variation_to_node_ids, header_variation, is_Varient=True)

    generate_node_cypher(dict_trait_set_type_dictionary, list_head_trait, extra_name='trait_set_')
    generate_node_cypher(dict_trait_type_dictionary, list_head_trait, extra_name='trait_')

    # prepare the important edge queries
    perpare_query_for_edges()

    print(set_of_species)
    print(dict_rela_type_pair_to_count)
    print(datetime.datetime.now())

    print('#' * 100)

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
