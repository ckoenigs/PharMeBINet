import lxml.etree as etree
import csv, sys
import json
import datetime, re

# type to the dictionary of nodes od this type
type_to_dictionary_of_node = {}

# type to csv writer
type_to_csv_writer = {}

# dictionary of diseases
dict_diseases = {}

# dictionary of relationships
dict_edges = {}

dict_type_to_number_of_measure = {}

#  type to genotype
dict_type_to_genotype = {}

# type genotype to csv file
dict_genotype_type_to_csv = {}

# type genotype to edge geno id - measure set csv
dict_genotype_type_edge_to_measure_set_to_csv = {}

# dictionary type to set genotype -measure set, measure type
dict_type_edge_genotype_measure_set_and_type = {}

# trait set type to trait set node
dict_trait_set_type_dictionary = {}

# trait set type to ces
dict_trait_set_typ_to_csv = {}

edge_information = ['title', 'assertion', 'clinical_significance', 'observations']

edge_file = open('edge.tsv', 'w', encoding='utf-8')
csv_edge = csv.DictWriter(edge_file, delimiter='\t', fieldnames=edge_information)
csv_edge.writeheader()


# dictionary of edges from measure set which has multiple measures to measure
dict_type_dict_pair_measure_set_measure={}

# dictionary of edges from measure set which has multiple measures to measure for write into the file
dict_csv_type_measure_set_measure={}

'''
prepare the citation information
'''


def for_citation_extraction_to_list(node, dict_to_use=None):
    all_citation = []
    for citation in node.iterfind('Citation'):
        citation_info = {}
        for id in citation.iterfind('ID'):
            citation_info[id.get('Source')] = id.text
        check_for_information_and_add_to_dictionary_with_extra_name('URL', citation, citation_info, name='url')
        check_for_information_and_add_to_dictionary_with_extra_name('CitationText', citation, citation_info,
                                                                    name='citation_text')
        all_citation.append(citation_info)

    if not dict_to_use is None:
        if len(all_citation) > 0:
            dict_to_use['citations'] = all_citation
        return dict_to_use

    return all_citation


'''
preparation of xrefs
'''


def preparation_of_xrefs(node, dict_to_use):
    all = set()
    for xref in node.iterfind('XRef'):
        all.add(xref.get('DB') + ':' + xref.get('ID'))
    if not dict_to_use is None:
        if len(all) > 0:
            dict_to_use['xrefs'] = list(all)
        return dict_to_use

    return list(all)


'''
for mutliple information
'''


def for_multiple_tags_at_one(node, tag):
    list_of_this_tags_outputs = []
    for comment in node.iterfind(tag):
        list_of_this_tags_outputs.append(comment.text)
    return list_of_this_tags_outputs


'''
clinical significance
'''


def prepare_clinical_significance(node):
    clinical_significance = node.find('ClinicalSignificance')
    if not clinical_significance is None:
        date = clinical_significance.get('DateLastEvaluated')
        dict_significance = {'date': date}
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

        # print(dict_significance)

        # todo external id, but if have to check what it stands for !
        result = clinical_significance.find('ExternalID')
        if not result is None:
            external_id = result.get('DB') + ':' + result.get('ID') + '(' + result.get('Type') + ')'
            print(external_id)

        return True, dict_significance
    return False, {}


'''
prepare set_element
'''


def prepare_set_element(node, set_element_type):
    dict_all_elements = {}
    for element in node.iterfind(set_element_type):
        element_value = element.find('ElementValue')
        type = element_value.get('Type')
        value = element_value.text
        if not type in dict_all_elements:
            dict_all_elements[type] = set()
        dict_all_elements[type].add(value)

        # for_citation_extraction_to_list(element, dict_one_element)
        # preparation_of_xrefs(element, dict_one_element)
        #
        # comment_dict = perare_comments(element)
        # build_low_dict_into_higher_dict(dict_one_element, comment_dict, 'comments')
        #
    return dict_all_elements


'''
get information from node and put in dictionary
'''


def check_for_information_and_add_to_dictionary_with_extra_name(tag, node, dictionary, name=None, gets=None):
    result = node.find(tag)
    if result is not None:
        value = result.text

        if name is None and gets is not None:
            dictionary[result.get(gets)] = value
        elif name is not None and gets is None:
            dictionary[name] = value
        else:
            sys.exist('I have to think about this case')
    # return list_to_add


'''
higher into lower but with list of elements
'''


def build_low_dict_into_higher_dict_with_list(top_dict, lower_dict, name, names):
    if len(lower_dict) > 0:
        if names not in top_dict:
            top_dict[names] = []
        top_dict[names].append({name: lower_dict})


'''
add set to a set but transform into string before
'''


def build_low_dict_into_higher_dict(top_dict, lower_dict, name):
    if len(lower_dict) > 0:
        top_dict[name] = lower_dict


'''
Add name to and synonyms to dictionary
'''


def add_name_and_synonyms_to_dict(node, dictionary):
    dict_names = prepare_set_element(node, 'Name')
    synonyms = set()
    for type, set_names in dict_names.items():
        if type != 'Preferred':
            synonyms=synonyms.union(set_names)
    synonyms = set(synonyms)
    if 'Preferred' in dict_names:
        name_s = dict_names['Preferred']
        if 'name' in dictionary:
            name = name_s.pop()
            if name != dictionary['name']:
                print(name)
                print(dictionary['name'])
                sys.exit('in existing name is different name then from the other source')
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
        element_list.union(element)
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
            dictionary['sequence_location'] = dict_seq_location


'''
preparation of attributes
'''


def preparation_attributions(node):
    dict_attributes = {}
    for attribute in node.iterfind('AttributeSet'):
        # todo must be a list
        check_for_information_and_add_to_dictionary_with_extra_name('Attribute', attribute, dict_attributes,
                                                                    gets='Type')
    return dict_attributes


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
                    sys.exit('allele and variant id are not unique?')
                else:
                    dict_allele_id_to_variant_id[value] = node_dictionary['identifier']
            if key not in node_dictionary:
                node_dictionary[key] = value
            else:
                if value != node_dictionary[key] and key not in set_properties_with_different_values:
                    print(key)
                    print(value)
                    print(node_dictionary[key])
                    print(node_dictionary)
                    set_properties_with_different_values.add(key)
    del node_dictionary['measures']


# type with multiple measure
type_with_multiple_measure = set()

# dictionary allele id to variant id
dict_allele_id_to_variant_id = {}

# species set
set_of_species = set()

# all assertion
assertions_set = set()

print(datetime.datetime.utcnow())
file = open('ClinVarFullRelease_00-latest.xml', 'rb')
# file = open('big_head.xml', 'rb')
for event, node in etree.iterparse(file, events=('end',), tag='ClinVarSet'):
    # print(etree.tostring(node))
    # all edge information
    dict_edge_info = {}
    # dictionary variant information
    dict_variant_info = {}
    # dictionary disease
    dict_disease = {}

    disease_id = ''
    variant_id = ''
    dict_edge_info['title'] = node.find('Title').text
    reference_assertion = node.find('ReferenceClinVarAssertion')

    # everything from reference
    if reference_assertion is not None:
        assertion = reference_assertion.find('Assertion').get('Type')
        if assertion not in assertions_set:
            assertions_set.add(assertion)
            print(assertion)
            print(datetime.datetime.utcnow())
        dict_edge_info['assertion'] = assertion
        found_clinical, dict_significance = prepare_clinical_significance(reference_assertion)
        if found_clinical:
            dict_edge_info['clinical_significance'] = json.dumps(dict_significance)

        # check if this relationship appears at least in human
        found_human = False
        observation_list = []
        for observation in reference_assertion.iterfind('ObservedIn'):
            observation_dict_one = {}
            sample = observation.find('Sample')
            sample_information = {}
            species = sample.find('Species')
            if species is not None:
                if species.text == 'human':
                    found_human = True
                else:
                    if  species.text not in set_of_species:
                        print('other than human')
                        print(node.get('ID'))
                        print(species.text)
                        set_of_species.add(species.text)
                    # sys.exit('other the human')

            check_for_information_and_add_to_dictionary_with_extra_name('Origin', sample, sample_information,
                                                                        name='origin')

            for age in sample.iterfind('Age'):
                sample_information['Age ' + age.get('Type')] = age.text + ' ' + age.get('age_unit')

            check_for_information_and_add_to_dictionary_with_extra_name('NumberTested', sample, sample_information,
                                                                        name='number_tested')
            check_for_information_and_add_to_dictionary_with_extra_name('NumberMales', sample, sample_information,
                                                                        name='number_tested_males')
            check_for_information_and_add_to_dictionary_with_extra_name('NumberFemales', sample, sample_information,
                                                                        name='number_tested_females')
            check_for_information_and_add_to_dictionary_with_extra_name('NumberChrTested', sample, sample_information,
                                                                        name='number_tested_children')
            check_for_information_and_add_to_dictionary_with_extra_name('GeographicOrigin', sample, sample_information,
                                                                        name='geographic_origin')

            check_for_information_and_add_to_dictionary_with_extra_name('Ethnicity', sample, sample_information,
                                                                        name='ethnicity')

            for_citation_extraction_to_list(sample, sample_information)
            preparation_of_xrefs(sample, sample_information)

            comment_dict = for_multiple_tags_at_one(sample, 'Comment')
            build_low_dict_into_higher_dict(sample_information, comment_dict, 'comments')
            build_low_dict_into_higher_dict(observation_dict_one, sample_information, 'sample')

            method_list = {}
            for method in observation.iterfind('Method'):
                method_info = {}
                check_for_information_and_add_to_dictionary_with_extra_name('MethodType', method, method_info,
                                                                            name='method_type')
                preparation_of_xrefs(method, method_info)
                build_low_dict_into_higher_dict_with_list(observation_dict_one, method_info, 'method', 'methods')

            observed_data_set = {}
            for observed_data in observation.iterfind('ObservedData'):
                one_observation = {}
                attribute = observed_data.find('Attribute')
                one_observation[attribute.get('Type')] = attribute.text
                for_citation_extraction_to_list(observed_data, one_observation)
                preparation_of_xrefs(observed_data, one_observation)
                comment_dict = for_multiple_tags_at_one(observation, 'Comment')
                build_low_dict_into_higher_dict(one_observation, comment_dict, 'comments')

                build_low_dict_into_higher_dict_with_list(observation_dict_one, one_observation, 'observation_data',
                                                          'observation_data_multiple')
            # build_low_dict_into_higher_dict(observation_dict_one, observed_data_set, 'observation_data_multiple')

            co_occurrences_set = {}
            for co_occurrence in observation.iterfind('Co-occurrenceSet'):
                print('co-occurences')

                one_co_occurrence = {}
                check_for_information_and_add_to_dictionary_with_extra_name('Zygosity', co_occurrence,
                                                                            one_co_occurrence,
                                                                            name='zygosity')
                check_for_information_and_add_to_dictionary_with_extra_name('Count', co_occurrence, one_co_occurrence,
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
                    found_clinical, dict_significance = prepare_clinical_significance((allele))
                    if found_clinical:
                        build_low_dict_into_higher_dict(one_allel_set, dict_significance, 'clinical_singnificant')

                    build_low_dict_into_higher_dict_with_list(one_co_occurrence, one_allel_set, 'allel', 'allels')
                # build_low_dict_into_higher_dict(one_co_occurrence, allels, 'allels')

                build_low_dict_into_higher_dict_with_list(observation_dict_one, one_co_occurrence, 'co-occurrence',
                                                          'co-occurrences')
            # build_low_dict_into_higher_dict(observation_dict_one,co_occurrences_set,'co-occurrences')

        # build_low_dict_into_higher_dict_with_list(observation_list, observation_dict_one, 'observation')
        add_dictionary_to_a_list_as_dict_with_a_name(observation_list, observation_dict_one, 'observation')
        dict_edge_info['observations'] = json.dumps(observation_list)

        # measureSet or genotype
        measure_set = reference_assertion.find('MeasureSet')
        genotype = reference_assertion.find('GenotypeSet')
        list_header_measures = ['identifier', 'accession', 'name', 'synonyms', 'symbols', 'comments', 'measures',
                                'citations', 'xrefs', 'number_of_chromosomes', 'specific_type', 'allele_id',
                                'attributes',
                                'cytogenetic_location', 'measure_relationships', 'sequence_location', 'frequencies',
                                'global_minor_allel_frequence']
        if measure_set is not None:
            node_dictionary = {}
            type = measure_set.get('Type')
            if type not in type_to_dictionary_of_node:
                type_to_dictionary_of_node[type] = set()
                file_type = open('data/' + type + '.tsv', 'w', encoding='utf-8')
                csv_writer_type = csv.DictWriter(file_type, delimiter='\t', fieldnames=list_header_measures)
                csv_writer_type.writeheader()
                type_to_csv_writer[type] = csv_writer_type
            identifier = measure_set.get('ID')
            variant_id = identifier
            accession = measure_set.get('Acc')
            if identifier == '431733':
                print('ok')
            if identifier not in type_to_dictionary_of_node[type]:
                node_dictionary['identifier'] = identifier
                node_dictionary['accession'] = accession

                if accession == 'VCV000599766':
                    print('blub')

                number_of_chr = measure_set.get('NumberOfChromosomes')
                if number_of_chr is not None:
                    node_dictionary['number_of_chromosomes'] = number_of_chr
                dict_measures = []
                for measure in measure_set.iterfind('Measure'):
                    # todo if no case exists where a measure set has more than one measure
                    dict_measure = {}
                    dict_measure['specific_type'] = measure.get('Type')
                    dict_measure['allele_id'] = measure.get('ID')
                    add_name_and_synonyms_to_dict(measure, dict_measure)
                    prepare_symbol(measure, dict_measure, 'symbols')
                    dict_attributes = preparation_attributions(measure)
                    build_low_dict_into_higher_dict(dict_measure, dict_attributes, 'attributes')

                    allele_frequencies = measure.find('AlleleFrequencyList')
                    list_of_frequencies = []
                    if not allele_frequencies is None:
                        for allel_frequence in allele_frequencies.iterfind('AlleleFrequency'):
                            list_of_frequencies.append(
                                {'frequence': allel_frequence.get('Value'), 'source': allel_frequence.get('Source')})
                        add_list_to_dict_if_not_empty(list_of_frequencies, dict_measure, 'frequencies')

                    global_minor_allel_frequence = measure.find('GlobalMinorAlleleFrequency')
                    if not global_minor_allel_frequence is None:
                        dict_global_allel_frequence = {}
                        add_element_to_dictionary_with_get(dict_global_allel_frequence, global_minor_allel_frequence,
                                                           'frequence', 'Value')
                        add_element_to_dictionary_with_get(dict_global_allel_frequence, global_minor_allel_frequence,
                                                           'source', 'Source')
                        add_element_to_dictionary_with_get(dict_global_allel_frequence, global_minor_allel_frequence,
                                                           'minor_allel', 'MinorAllele')
                        dict_measure['global_minor_allel_frequence'] = dict_global_allel_frequence

                    check_for_information_and_add_to_dictionary_with_extra_name('CytogeneticLocation', measure,
                                                                                dict_measure,
                                                                                name='cytogenetic_location')

                    add_current_sequence_location_to_dictionary(dict_measure, measure)

                    relationship_information = []
                    for measure_rela in measure.iterfind('MeasureRelationship'):
                        dict_rela = {}
                        add_name_and_synonyms_to_dict(measure_rela, dict_rela)
                        prepare_symbol(measure_rela, dict_rela, 'symbols')
                        preparation_of_xrefs(measure_rela, dict_rela)
                        relationship_information.append(dict_rela)
                    add_list_to_dict_if_not_empty(relationship_information, dict_measure, 'measure_relationships')

                    for_citation_extraction_to_list(measure, dict_measure)
                    preparation_of_xrefs(measure, dict_measure)
                    comment_dict = for_multiple_tags_at_one(measure, 'Comment')
                    build_low_dict_into_higher_dict(dict_measure, comment_dict, 'comments')

                    dict_measures.append(dict_measure)
                    build_low_dict_into_higher_dict_with_list(node_dictionary, dict_measure, 'measure', 'measures')

                if type not in dict_type_to_number_of_measure:
                    dict_type_to_number_of_measure[type] = set()
                dict_type_to_number_of_measure[type].add(len(dict_measures))
                if len(dict_measures)>1:

                    if type not in dict_type_dict_pair_measure_set_measure:
                        dict_type_dict_pair_measure_set_measure[type]=set()
                        writer=open('data/edge_measure_set_measure_'+type+'.csv','w',encoding='utf-8')
                        csv_writer=csv.writer(writer,delimiter='\t')
                        csv_writer.writerow(['measure_set_id','measure_id'])
                        dict_csv_type_measure_set_measure[type]=csv_writer
                    for dictionary_measure in dict_measures:
                        if (identifier, dictionary_measure['allele_id']) not in dict_type_dict_pair_measure_set_measure[type]:
                            dict_type_dict_pair_measure_set_measure[type].add((identifier, dictionary_measure['allele_id']) )
                if len(dict_measures) > 1 and type not in type_with_multiple_measure:
                    print('more then one measure')
                    print(type)
                    type_with_multiple_measure.add(type)
                    # print(node_dictionary)
                    # sys.exit('more then one measure')
                build_low_dict_into_higher_dict(node_dictionary, dict_measures, 'measures')

                add_name_and_synonyms_to_dict(measure_set, node_dictionary)
                prepare_symbol(measure_set, node_dictionary, 'symbols')

                for_citation_extraction_to_list(measure_set, node_dictionary)
                preparation_of_xrefs(measure_set, node_dictionary)

                comment_dict = for_multiple_tags_at_one(measure_set, 'Comment')
                build_low_dict_into_higher_dict(node_dictionary, comment_dict, 'comments')

                if len(dict_measures) == 1:
                    fusion_of_them(node_dictionary, dict_measures)

                type_to_dictionary_of_node[type].add(identifier)
                type_to_csv_writer[type].writerow(node_dictionary)

        elif genotype is not None:
            list_header_genotype = ['identifier', 'accession', 'name', 'synonyms', 'symbols', 'comments',
                                    'citations', 'xrefs', 'attributes']
            list_header_edge_genotype_measure_set = ['genotype_id', 'measure_set_id']
            identifier = genotype.get('ID')
            type = genotype.get('Type')
            accession = genotype.get('Acc')

            variant_id = identifier

            if type not in dict_type_to_genotype:
                dict_type_to_genotype[type] = set()
                dict_type_edge_genotype_measure_set_and_type[type] = {}
                writer = open('data/genotype_' + type + '.csv', 'w', encoding='utf-8')
                csv_writer = csv.DictWriter(writer, delimiter='\t', fieldnames=list_header_genotype)
                csv_writer.writeheader()
                dict_genotype_type_to_csv[type] = csv_writer

            for measure_set in genotype.iterfind('MeasureSet'):
                measure_set_type = measure_set.get('Type')
                identifier_measure_set = measure_set.get('ID')

                if (type, measure_set_type) not in dict_type_edge_genotype_measure_set_and_type:
                    writer = open('data/edge_genotype_' + type + '_' + measure_set_type + '.csv', 'w',
                                  encoding='utf-8')
                    csv_writer = csv.writer(writer, delimiter='\t')
                    csv_writer.writerow(list_header_edge_genotype_measure_set)
                    dict_genotype_type_edge_to_measure_set_to_csv[(type,measure_set_type)] = csv_writer
                    dict_type_edge_genotype_measure_set_and_type[(type,measure_set_type)]=set()

                if not (identifier, identifier_measure_set) in \
                       dict_type_edge_genotype_measure_set_and_type[type]:


                    dict_type_edge_genotype_measure_set_and_type[(type,measure_set_type)].add(( identifier, identifier_measure_set))


                    dict_genotype_type_edge_to_measure_set_to_csv[(type,measure_set_type)].writerow(
                        [identifier, identifier_measure_set, measure_set_type])

            if identifier not in dict_type_to_genotype[type]:
                dict_genotyp = {}

                dict_genotyp['identifier'] = identifier
                dict_genotyp['accession'] = accession

                dict_attributes = preparation_attributions(genotype)
                build_low_dict_into_higher_dict(dict_genotyp, dict_attributes, 'attributes')

                add_name_and_synonyms_to_dict(genotype, dict_genotyp)
                prepare_symbol(genotype, dict_genotyp, 'symbols')
                for_citation_extraction_to_list(genotype, dict_genotyp)
                preparation_of_xrefs(genotype, dict_genotyp)
                comment_dict = for_multiple_tags_at_one(genotype, 'Comment')
                build_low_dict_into_higher_dict(dict_genotyp, comment_dict, 'comments')

                dict_type_to_genotype[type].add(identifier)

                dict_genotype_type_to_csv[type].writerow(dict_genotyp)

        # trait Set
        trait_set = reference_assertion.find('TraitSet')

        list_head_trait = ['identifier', 'accession', 'name', 'synonyms', 'symbols', 'comments',
                           'citations', 'xrefs', 'attributes', 'traits']
        identifier = trait_set.get('ID')
        trait_set_type = trait_set.get('Type')

        if not trait_set_type in dict_trait_set_type_dictionary:
            dict_trait_set_type_dictionary[trait_set_type] = set()

            writer = open('data/trait_set_' + trait_set_type + '.tsv', 'w', encoding='utf-8')
            csv_writer = csv.DictWriter(writer, delimiter='\t', fieldnames=list_head_trait)
            csv_writer.writeheader()
            dict_trait_set_typ_to_csv[trait_set_type] = csv_writer

        if not identifier in dict_trait_set_type_dictionary[trait_set_type]:
            dict_trait_set = {}

            list_traits = []
            for trait in trait_set.iterfind('Trait'):
                dict_trait = {}

                trait_type = trait.get('Type')
                trait_identifier = trait.get('ID')

                dict_trait['type'] = trait_type
                dict_trait['identifier'] = trait_identifier

                add_name_and_synonyms_to_dict(trait, dict_trait)
                prepare_symbol(trait, dict_trait, 'symbols')

                dict_attributes = preparation_attributions(trait)
                build_low_dict_into_higher_dict(dict_trait, dict_attributes, 'attributes')

                list_trait_rela = []
                for trait_rela in trait.iterfind('TraitRelationship'):
                    list_trait_rela.append((trait_rela.get('Type'), trait_rela.get('Id')))
                if len(list_trait_rela) > 0:
                    dict_trait['trait_rela'] = list_trait_rela

                for_citation_extraction_to_list(trait, dict_trait)
                preparation_of_xrefs(trait, dict_trait)
                comment_dict = for_multiple_tags_at_one(trait, 'Comment')
                build_low_dict_into_higher_dict(dict_trait, comment_dict, 'comments')
                list_traits.append(dict_trait)
                build_low_dict_into_higher_dict_with_list(dict_trait_set, dict_trait, 'trait', 'traits')

            dict_attributes = preparation_attributions(trait_set)
            build_low_dict_into_higher_dict(dict_trait_set, dict_attributes, 'attributes')

            add_name_and_synonyms_to_dict(trait_set, dict_trait_set)
            prepare_symbol(trait_set, dict_trait_set, 'symbols')
            for_citation_extraction_to_list(trait_set, dict_trait_set)
            preparation_of_xrefs(trait_set, dict_trait_set)
            comment_dict = for_multiple_tags_at_one(trait_set, 'Comment')
            build_low_dict_into_higher_dict(dict_trait_set, comment_dict, 'comments')

            # if len(list_traits) > 1 and not trait_set_type == 'Finding':
            #     print(identifier)
            #     print(trait_set_type)
            #     print('more then one trait')
            # sys.exit('more then one trait')

            dict_trait_set_type_dictionary[trait_set_type].add(identifier)
            dict_trait_set_typ_to_csv[trait_set_type].writerow(dict_trait_set)

    if node[0].text == 'current':
        csv_edge.writerow(dict_edge_info)
        # if (variant_id,disease_id) not in dict_edges:
        #     dict_edges[(variant_id,disease_id)]=dict_edge_info
        #     csv_edge.writerow(dict_edge_info)
        # else:
        #     print(disease_id)
        #     print(variant_id)
        #     print(dict_edges[(variant_id,disease_id)])
        #     print(dict_edge_info)
        # sys.exit('same pair, but do they have different information?')
    # break
    node.clear()

for type, set_measure_set_measure in dict_type_dict_pair_measure_set_measure.items():
    for (measure_set_id, allele_id) in set_measure_set_measure:
        if allele_id in dict_allele_id_to_variant_id:
            dict_csv_type_measure_set_measure[type].writerow([measure_set_id,dict_allele_id_to_variant_id[allele_id]])
        else:
            print(allele_id)
            print(measure_set_id)
            sys.exit('allele id do not exist somwhere ;(')


print(type_to_dictionary_of_node.keys())
print(dict_type_to_number_of_measure)
print(set_of_species)
print(datetime.datetime.utcnow())
