import lxml.etree as etree
import csv,sys
import json

#type to the dictionary of nodes od this type
type_to_dictionary_of_node={}

#dictionary of diseases
dict_diseases={}

#dictionary of relationships
dict_edges={}

edge_information=['title','assertion','clinical_significance','observations']

edge_file=open('edge.tsv','w',encoding='utf-8')
csv_edge=csv.DictWriter(edge_file,delimiter='\t',fieldnames=edge_information)
csv_edge.writeheader()

'''
prepare the citation information
'''
def for_citation_extraction_to_list(node,dict_to_use=None):
    all_citation={}
    for citation in node.iter('Citation'):
        citation_info = {}
        for id in citation.iter('ID'):
            citation_info[id.get('Source')]=  id.text
        check_for_information_and_add_to_list_with_extra_name('URL', citation, citation_info, name='url')
        check_for_information_and_add_to_list_with_extra_name('CitationText', citation, citation_info,
                                                              name='citation_text')
        build_low_dict_into_higher_dict(all_citation,citation_info,'citation')

        if not dict_to_use is None:
            build_low_dict_into_higher_dict(dict_to_use, all_citation, 'citations')
            return dict_to_use


    return all_citation

'''
preparation of xrefs
'''
def preparation_of_xrefs(node,dict_to_use):
    all = {}
    for xref in node.iter('XRef'):
        all[xref.get('DB')]=xref.get('ID')
    if not dict_to_use is None:
        build_low_dict_into_higher_dict(dict_to_use, all, 'xrefs')
        return dict_to_use

    return  all

'''
prepare comments
'''
def perare_comments(node):
    dict_comments={}
    for comment in node.iter('Comment'):
        check_for_information_and_add_to_list_with_extra_name('Comment', comment, dict_comments,
                                                              name='comment')
    return dict_comments

'''
clinical significance
'''
def prepare_clinical_significance(node):
    clinical_significance = node.find('ClinicalSignificance')
    if not clinical_significance is None:
        date = clinical_significance.get('DateLastEvaluated')
        dict_significance = {'date': date}
        check_for_information_and_add_to_list_with_extra_name('ReviewStatus', clinical_significance, dict_significance,
                                                              name='review_status')

        check_for_information_and_add_to_list_with_extra_name('Description', clinical_significance, dict_significance,
                                                              name='description')

        check_for_information_and_add_to_list_with_extra_name('Explanation', clinical_significance, dict_significance,
                                                              name='explanation')

        preparation_of_xrefs(clinical_significance, dict_significance)

        for_citation_extraction_to_list(clinical_significance, dict_significance)

        comment_dict = perare_comments(clinical_significance)
        build_low_dict_into_higher_dict(dict_significance, comment_dict, 'comments')

        # print(dict_significance)


        #todo external id, but if have to check what it stands for !
        result = clinical_significance.find('ExternalID')
        if not result is None:
            external_id=result.get('DB')+':'+result.get('ID')+'('+result.get('Type')+')'
            print(external_id)

        return True, dict_significance
    return False, {}

'''
prepare set_element
'''
def prepare_set_element(node, set_element_type):
    dict_all_elements={}
    for element in node.iter(set_element_type):
        element_value=element.find('ElementValue')
        type=element_value.get('Type')
        value=element.text
        if not type in dict_all_elements:
            dict_all_elements[type]=set()
        dict_all_elements[type].add(value)


        # for_citation_extraction_to_list(element, dict_one_element)
        # preparation_of_xrefs(element, dict_one_element)
        #
        # comment_dict = perare_comments(element)
        # build_low_dict_into_higher_dict(dict_one_element, comment_dict, 'comments')
        #
    return dict_all_elements

'''
get information from node and put in list
'''
def check_for_information_and_add_to_list_with_extra_name(tag, node,dictionary,name=None,gets=None):
    result=node.find(tag)
    if not result  is None:
        value=result.text

        if name is None and not gets is None:
            dictionary[result.get(gets) ]=value
        elif not name is None and gets is None:
            dictionary[name]=value
        else:
            sys.exist('I have to think about this case')
    # return list_to_add

'''
add set to a set but transform into string before
'''
def build_low_dict_into_higher_dict(top_dict,lower_dict,name):
    if len(lower_dict)>0:
        top_dict[name]=lower_dict

'''
Add name to and synonyms to dictionary
'''
def add_name_and_synonyms_to_dict(node, dictionary):
    dict_names = prepare_set_element(node, 'Name')
    synonyms={}
    synonyms = {synonyms.union(x) for type, x in dict_names if type != 'Preferred'}
    if 'Preferred' in dict_names:
        name_s = dict_names['Preferred']
        if len(name_s) == 1:
            dictionary['name'] = name_s[0]
        else:
            sys.exit('multiple_names preferred')
    elif len(synonyms) > 0:
        dictionary['name'] = synonyms[0]
        synonyms.remove(synonyms[0])

    if len(synonyms) > 0:
        dictionary['synonyms'] = list(synonyms)

'''
prepare symbol
'''
def prepare_symbol(node, dictionary,dictionary_name):
    dict_elements=prepare_set_element(node,'Symbol')
    element_list={}
    element_list= {element_list.union(x) for type, x in dict_elements}
    dictionary[dictionary_name]=list(element_list)


#all assertion
assertions_set=set()

file = open('head_part.xml', 'rb')
for event, node in etree.iterparse(file, events=('end',), tag='ClinVarSet'):
    # print(etree.tostring(node))
    #all edge information
    dict_edge_info={}
    #dictionary variant information
    dict_variant_info={}
    #dictionary disease
    dict_disease={}

    disease_id=''
    variant_id=''
    dict_edge_info['title']=node.find('Title').text
    reference_assertion= node.find('ReferenceClinVarAssertion')

    #everything from reference
    if not reference_assertion is None:
        assertion=reference_assertion.find('Assertion').get('Type')
        if assertion not in assertions_set:
            assertions_set.add(assertion)
            print(assertion)
        dict_edge_info['assertion']=assertion
        found_clinical, dict_significance= prepare_clinical_significance(reference_assertion)
        if found_clinical:
            dict_edge_info['clinical_significance']=json.dumps(dict_significance)

        #check if this relationship appears at least in human
        found_human=False
        observation_list={}
        for observation in reference_assertion.iter('ObservedIn'):
            observation_dict_one={}
            sample=observation.find('Sample')
            sample_information={}
            species=sample.find('Species')
            if not species is None:
                if species.text=='human':
                    found_human=True
                else:
                    print(node.get('ID'))
                    print(species.text)
                    sys.exit('other the human')

            check_for_information_and_add_to_list_with_extra_name('Origin',sample,sample_information,name='origin')

            for age in sample.iter('Age'):
                sample_information['Age '+age.get('Type')]=age.text+' '+age.get('age_unit')


            check_for_information_and_add_to_list_with_extra_name('NumberTested',sample,sample_information,name='number_tested')
            check_for_information_and_add_to_list_with_extra_name('NumberMales',sample,sample_information,name='number_tested_males')
            check_for_information_and_add_to_list_with_extra_name('NumberFemales',sample,sample_information,name='number_tested_females')
            check_for_information_and_add_to_list_with_extra_name('NumberChrTested',sample,sample_information,name='number_tested_children')
            check_for_information_and_add_to_list_with_extra_name('GeographicOrigin',sample,sample_information,name='geographic_origin')

            check_for_information_and_add_to_list_with_extra_name('Ethnicity',sample,sample_information,name='ethnicity')

            for_citation_extraction_to_list(sample, sample_information)
            preparation_of_xrefs(sample, sample_information)

            comment_dict = perare_comments(sample)
            build_low_dict_into_higher_dict(sample_information, comment_dict, 'comments')
            build_low_dict_into_higher_dict(observation_dict_one,sample_information,'sample')

            method_list={}
            for method in observation.iter('Method'):
                method_info={}
                check_for_information_and_add_to_list_with_extra_name('MethodType',method,method_info,name='method_type')
                preparation_of_xrefs(method,method_info)
                build_low_dict_into_higher_dict(method_list,method_info,'method')
            build_low_dict_into_higher_dict(observation_dict_one, method_list, 'methods')

            observed_data_set={}
            for observed_data in observation.iter('ObservedData'):
                one_observation={}
                attribute=observed_data.find('Attribute')
                one_observation[attribute.get('Type')]=attribute.text
                for_citation_extraction_to_list(observed_data, observed_data_set)
                preparation_of_xrefs(observed_data, observed_data_set)
                comment_dict=perare_comments(observation)
                build_low_dict_into_higher_dict(one_observation, comment_dict, 'comments')

                build_low_dict_into_higher_dict(observed_data_set,one_observation,'observation_data')
            build_low_dict_into_higher_dict(observation_dict_one, observed_data_set, 'observation_data_multiple')

            co_occurrences_set={}
            for co_occurrence in observation.iter('Co-occurrenceSet'):
                one_co_occurrence={}
                check_for_information_and_add_to_list_with_extra_name('Zygosity',co_occurrence,one_co_occurrence,name='zygosity')
                check_for_information_and_add_to_list_with_extra_name('Count',co_occurrence,one_co_occurrence,name='count')
                allels={}
                for allele in co_occurrence.iter('AlleleDescSet'):
                    one_allel_set={}
                    check_for_information_and_add_to_list_with_extra_name('RelativeOrientation',allele,one_allel_set,name='relative_orientation')
                    check_for_information_and_add_to_list_with_extra_name('Zygosity',allele,one_allel_set,name='zygosity')
                    check_for_information_and_add_to_list_with_extra_name('Name', allele, one_allel_set,
                                                                          name='name')
                    found_clinical, dict_significance= prepare_clinical_significance((allele))
                    if found_clinical:
                        build_low_dict_into_higher_dict(one_allel_set,dict_significance,'clinical_singnificant')

                    build_low_dict_into_higher_dict(allels, one_allel_set, 'allel')
                build_low_dict_into_higher_dict(one_co_occurrence, allels, 'allels')

                build_low_dict_into_higher_dict(co_occurrences_set, one_co_occurrence, 'co-occurrence')
            build_low_dict_into_higher_dict(observation_dict_one,co_occurrences_set,'co-occurrences')
        build_low_dict_into_higher_dict(observation_list, observation_dict_one, 'observation')
        dict_edge_info['observations']=json.dumps(observation_list)

        # measureSet or genotype
        measure_set = reference_assertion.find('MeasureSet')
        genotype = reference_assertion.find('GenotypeSet')
        list_header_measures=['identifier','accession']
        if not measure_set is None:
            node_dictionary={}
            type=measure_set.get('Type')
            if type not in type_to_dictionary_of_node:
                type_to_dictionary_of_node[type]={}
            identifier=measure_set.get('ID')
            variant_id=identifier
            accession=measure_set.get('Accession')
            if not identifier in type_to_dictionary_of_node[type]:
                node_dictionary['identifier']=identifier
                node_dictionary['accession']=accession
                dict_measure={}
                for measure in measure_set.iter(''):
                    print()
                build_low_dict_into_higher_dict(node_dictionary,dict_measure,'measures')
                    
                add_name_and_synonyms_to_dict(measure_set,node_dictionary)
                prepare_symbol(measure_set,node_dictionary,'Symbol')

                for_citation_extraction_to_list(measure_set, node_dictionary)
                preparation_of_xrefs(measure_set, node_dictionary)

                comment_dict=perare_comments(observation)
                build_low_dict_into_higher_dict(node_dictionary, comment_dict, 'comments')





                type_to_dictionary_of_node[type][identifier]=node_dictionary






    if node[0].text =='current':
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