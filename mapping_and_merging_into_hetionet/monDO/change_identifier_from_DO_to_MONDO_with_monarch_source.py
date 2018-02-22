# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 13:31:43 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import sys
import datetime
from types import *

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append('../drugbank/')
from add_information_from_a_not_existing_node_to_existing_node import merge_information_from_one_node_to_another


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary monarch DO to information: name
dict_monDO_info = {}

# dictionary external ids to monDO id
dict_external_ids_monDO = {}

# dict of xrefs from monDO which has multiple monDO IDs with counter
dict_source_mapped_to_multiple_monDOs = {}

'''
Load MonDO disease in dictionary
'''


def load_in_all_monDO_in_dictionary():
    query = ''' MATCH (n:disease)  RETURN n'''
    results = g.run(query)
    for disease, in results:
        monDo_id = disease['http://www.geneontology.org/formats/oboInOwl#id']
        # if monDo_id == 'MONDO:0007108':
        #     print('blub')
        dict_monDO_info[monDo_id] = dict(disease)
        xrefs = disease[
            'http://www.geneontology.org/formats/oboInOwl#hasDbXref'] if 'http://www.geneontology.org/formats/oboInOwl#hasDbXref' in disease else []
        # the DOID:7 mapped better to MONDO:0021199
        if monDo_id=='MONDO:0000001':
            xrefs.remove('DOID:7')
            dict_monDO_info[monDo_id]['http://www.geneontology.org/formats/oboInOwl#hasDbXref']= xrefs
        if type(xrefs) == list:
            for external_id in xrefs:
                if external_id in dict_external_ids_monDO:
                    if external_id.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                        dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] = 1

                    else:
                        dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] += 1

                    # print(external_id)
                    dict_external_ids_monDO[external_id].append(monDo_id)
                    # print(dict_external_ids_monDO[external_id])
                else:
                    dict_external_ids_monDO[external_id] = [monDo_id]
        else:
            if xrefs in dict_external_ids_monDO:
                if xrefs.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                    dict_source_mapped_to_multiple_monDOs[xrefs.split(':')[0]] = 1

                else:
                    dict_source_mapped_to_multiple_monDOs[xrefs.split(':')[0]] += 1

                # print(external_id)
                dict_external_ids_monDO[xrefs].append(monDo_id)
                # print(dict_external_ids_monDO[external_id])
            else:
                dict_external_ids_monDO[xrefs] = [monDo_id]

        possible_xref = disease[
            'http://www.geneontology.org/formats/oboInOwl#hasAlternativeId'] if 'http://www.geneontology.org/formats/oboInOwl#hasAlternativeId' in disease else []
        if type(possible_xref) == list:
            for external_id in possible_xref:
                if external_id in dict_external_ids_monDO:
                    if external_id.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                        dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] = 1
                    else:
                        dict_source_mapped_to_multiple_monDOs[external_id.split(':')[0]] += 1
                    # print(external_id)
                    dict_external_ids_monDO[external_id].append(monDo_id)
                    # print(dict_external_ids_monDO[external_id])
                else:
                    dict_external_ids_monDO[external_id] = [monDo_id]
        else:
            if possible_xref in dict_external_ids_monDO:
                if possible_xref.split(':')[0] not in dict_source_mapped_to_multiple_monDOs:
                    dict_source_mapped_to_multiple_monDOs[possible_xref.split(':')[0]] = 1
                else:
                    dict_source_mapped_to_multiple_monDOs[possible_xref.split(':')[0]] += 1
                # print(external_id)
                dict_external_ids_monDO[possible_xref].append(monDo_id)
                # print(dict_external_ids_monDO[external_id])
            else:
                dict_external_ids_monDO[possible_xref] = [monDo_id]

    print(dict_source_mapped_to_multiple_monDOs)


# dictionary disease ontology to external ids
dict_DO_to_xref = {}

# dictionary do to information: name
dict_DO_to_info = {}

# dictionary do to alternative doid
dict_do_to_alternative_do = {}

'''
Load in all disease ontology ids with external identifier and alternative id
'''


def load_in_all_DO_in_dictionary():
    query = ''' MATCH (n:Disease) RETURN n'''
    results = g.run(query)
    for disease, in results:
        Do_id = disease['identifier']
        # if Do_id == 'DOID:4606':
        #     print('ok')
        dict_DO_to_info[Do_id] = dict(disease)
        alternative_id = disease['alternateIds'] if 'alternateIds' in disease else []
        dict_do_to_alternative_do[Do_id] = alternative_id
        xrefs = disease['xrefs'] if 'xrefs' in disease else []
        xrefs = xrefs[0].split(',')
        dict_DO_to_xref[Do_id] = xrefs

    print('Number of DOIDs:' + str(len(dict_DO_to_xref)))


# dictionary monDO to DOIDs
dict_monDo_to_DO = {}

# dictionary monDO to DOIDs with only doid mapping
dict_monDo_to_DO_only_doid = {}

# dictionary Do to monDos
dict_DO_to_monDOs = {}

# dictionary Do to monDos
dict_DO_to_monDOs_only_DO = {}

# list of not mapped doids
list_of_not_mapped_doids = []

'''
Go through all DOIDs and check if the DOID or the external IDs are in the xrefs-monDO dictionary and generate mapping
'''


def map_DO_to_monDO_with_DO_and_xrefs():
    not_direct_name_matching_file = open('not_direct_name_matching_file.tsv', 'w')
    not_direct_name_matching_file.write('monDO \t DOID \t name monDO \t name DOID \n')
    counter_name_not_matching = 0
    for doid, xrefs in dict_DO_to_xref.items():
        # if doid == 'DOID:4606':
        #     print('ok')
        if doid in dict_external_ids_monDO:

            for monDO in dict_external_ids_monDO[doid]:
                monDOname = dict_monDO_info[monDO]['label'].lower()
                do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '')
                if monDOname != do_name:
                    counter_name_not_matching += 1
                    not_direct_name_matching_file.write(
                        monDO + '\t' + doid + '\t' + dict_monDO_info[monDO]['label'] + '\t' + dict_DO_to_info[doid][
                            'name'] + '\n')
                    # print(monDO)
                    # print(doid)
                    # print(dict_monDO_info[monDO][0])
                    # print(dict_DO_to_info[doid][0])
                if monDO in dict_monDo_to_DO:
                    dict_monDo_to_DO[monDO].add(doid)
                    if monDO in dict_monDo_to_DO_only_doid:
                        dict_monDo_to_DO_only_doid[monDO].add(doid)
                    else:
                        dict_monDo_to_DO_only_doid[monDO] = set([doid])
                else:
                    dict_monDo_to_DO[monDO] = set([doid])
                    dict_monDo_to_DO_only_doid[monDO] = set([doid])

                if doid in dict_DO_to_monDOs:
                    dict_DO_to_monDOs[doid].add(monDO)
                    dict_DO_to_monDOs_only_DO[doid].add(monDO)
                else:
                    dict_DO_to_monDOs[doid] = set([monDO])
                    dict_DO_to_monDOs_only_DO[doid] = set([monDO])
        else:
            found_with_alternative = False
            for alternativ_doid in dict_do_to_alternative_do[doid]:
                if alternativ_doid in dict_external_ids_monDO:
                    found_with_alternative = True

                    for monDO in dict_external_ids_monDO[alternativ_doid]:
                        monDOname = dict_monDO_info[monDO]['label'].lower()
                        do_name = dict_DO_to_info[doid]['name'].lower().replace("'", '')
                        if monDOname != do_name:
                            counter_name_not_matching += 1
                            not_direct_name_matching_file.write(
                                monDO + '\t' + doid + '\t' + dict_monDO_info[monDO]['label'] + '\t' +
                                dict_DO_to_info[doid][
                                    'name'] + '\n')
                            # print(monDO)
                            # print(doid)
                            # print(dict_monDO_info[monDO][0])
                            # print(dict_DO_to_info[doid][0])
                        if monDO in dict_monDo_to_DO:
                            dict_monDo_to_DO[monDO].add(doid)
                            if monDO in dict_monDo_to_DO_only_doid:
                                dict_monDo_to_DO_only_doid[monDO].add(doid)
                            else:
                                dict_monDo_to_DO_only_doid[monDO] = set([doid])
                        else:
                            dict_monDo_to_DO[monDO] = set([doid])
                            dict_monDo_to_DO_only_doid[monDO] = set([doid])

                        if doid in dict_DO_to_monDOs:
                            dict_DO_to_monDOs[doid].add(monDO)
                            dict_DO_to_monDOs_only_DO[doid].add(monDO)
                        else:
                            dict_DO_to_monDOs[doid] = set([monDO])
                            dict_DO_to_monDOs_only_DO[doid] = set([monDO])
            if not found_with_alternative:
                list_of_not_mapped_doids.append(doid)
        for xref in xrefs:
            xref = xref.replace("'", "")
            if xref in dict_external_ids_monDO:
                for monDO in dict_external_ids_monDO[xref]:
                    if monDO in dict_monDo_to_DO:
                        dict_monDo_to_DO[monDO].add(doid)
                    else:
                        dict_monDo_to_DO[monDO] = set([doid])
                    if doid in dict_DO_to_monDOs:
                        # if monDO not in dict_DO_to_monDOs[doid]:
                        # print(xref)
                        dict_DO_to_monDOs[doid].add(monDO)
                    else:
                        dict_DO_to_monDOs[doid] = set([monDO])

    print('number of not name matching mappes:' + str(counter_name_not_matching))
    print('number of mapped doids with only doids:' + str(len(dict_DO_to_monDOs_only_DO)))
    print('number of mapped doids:' + str(len(dict_DO_to_monDOs_only_DO)))

    print('number of mapped monDO with only doids:' + str(len(dict_monDo_to_DO_only_doid)))
    print('number of mapped monDO:' + str(len(dict_monDo_to_DO)))

    counter_more_than_one_monDO_ID = 0

    for doid, mondos in dict_DO_to_monDOs.items():
        if len(mondos) > 1:
            counter_more_than_one_monDO_ID += 1

    print('number of multiple monDO IDs:' + str(counter_more_than_one_monDO_ID))

    print(list_of_not_mapped_doids)

    # generate file with not mapped doids
    file_not_mapped_doids = open('not_mapped_DOIDs.txt', 'w')
    file_not_mapped_doids.write('doid \t name \n')
    for doid in list_of_not_mapped_doids:
        file_not_mapped_doids.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')

    file_not_mapped_doids.close()

    # file for multiple mapped monDO IDs
    file_mondo_to_multiple_doids = open('multiple_doids_for_monDO.tsv', 'w')
    file_mondo_to_multiple_doids.write('monDO\t monDO name\t doids \t doid names\n')
    for monDO, doids in dict_monDo_to_DO_only_doid.items():
        if len(doids) > 1:
            text = monDO + '\t' + dict_monDO_info[monDO]['label'] + '\t' + '|'.join(doids) + '\t'
            for doid in doids:
                text = text + dict_DO_to_info[doid]['name'] + '|'
            file_mondo_to_multiple_doids.write(text[0:-1] + '\n')
            # print(monDO)
            # print(doids)

    # print(dict_DO_to_monDOs)
    print('###################################################################################')
    # print(dict_DO_to_monDOs_only_DO)

    print('###################################################################################')
    # print(dict_monDo_to_DO)


'''
Generate mapping files
'''


def mapping_files():
    multi_mondo_for_do = open('mapping/multi_mondo_for_a_doid.txt', 'w')
    multi_mondo_for_do.write('doid\t name\t mondos\t mondo_names\n')
    for doid, mondos in dict_DO_to_monDOs_only_DO.items():
        f = open('mapping/Do_to_monDO/' + doid + '.txt', 'w')
        f.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')
        f.write('monDO ID \t name \n')
        if len(mondos) > 1:
            string_mondos = ",".join(mondos)
            line = doid + '\t' + dict_DO_to_info[doid]['name'] + '\t' + string_mondos + '\t'
            liste_names = []
            for mondo in mondos:
                liste_names.append(dict_monDO_info[mondo]['label'])
            list_name_string = ",".join(liste_names)
            multi_mondo_for_do.write(line + list_name_string + '\n')
        for mondo in mondos:
            f.write(mondo + '\t' + dict_monDO_info[mondo]['label'] + '\n')
        f.close()

    for monDo, doids in dict_monDo_to_DO.items():
        g = open('mapping/monDO_to_DO/with_xref/' + monDo + '.txt', 'w')
        g.write(monDo + '\t' + dict_monDO_info[monDo]['label'] + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')
        g.close()

    for monDo, doids in dict_monDo_to_DO_only_doid.items():
        g = open('mapping/monDO_to_DO/without_xref/' + monDo + '.txt', 'w')
        g.write(monDo + '\t' + dict_monDO_info[monDo]['label'] + '\n')
        g.write('DOID \t name \n')
        for doid in doids:
            g.write(doid + '\t' + dict_DO_to_info[doid]['name'] + '\n')
        g.close()


# dictionary of the doids which are merged  into one, key is the merged id and value are the nodes which are integrated
# into the merged node
dict_merged_nodes = {
    'MONDO:0001504':['DOID:1233'] # DOID:1233 (transvestism) is sub class of  fetishism and contains relationships -> merged together
}

# dictionary of self decision which doid is the merged node
dict_self_decision_mondo_multiple_doid = {
    'MONDO:0004398': 'DOID:7922',
    'MONDO:0001561': 'DOID:12639',
    'MONDO:0010626': 'DOID:6620',
    'MONDO:0003061': 'DOID:461',
    'MONDO:0016021': 'DOID:0050709',
    'MONDO:0003345': 'DOID:4927',
    'MONDO:0006639': 'DOID:660'
}

# dictionary of mondo to doid where mondo has no doid as ref but an external identifier mapped manual
dict_mondo_xref_doid_mapping = {
    'MONDO:0009700': 'DOID:0080194',
    'MONDO:0009567': 'DOID:0080195',
    'MONDO:0010771': 'DOID:0080198',
    'MONDO:0003050': 'DOID:4556',
    'MONDO:0001071': 'DOID:1059',
    'MONDO:0021199': 'DOID:7' # disease affecting anatomical system (mondo) is more  similar to disease of anatomical entity (DOID:7) than disease (DOID:4) also same subclasses like DOID:7
}

# list of doids which are not part of mondo and are removed
list_removed_doids = ['DOID:7267', 'DOID:0060017', 'DOID:946', 'DOID:6823', 'DOID:0050332', 'DOID:8150', 'DOID:5469',
                      'DOID:0080125', 'DOID:7571', 'DOID:0060517', 'DOID:9341', 'DOID:0080193', 'DOID:0080197',
                      'DOID:0080196', 'DOID:0050875','DOID:0050987', 'DOID:2468', 'DOID:854' ]

'''
integrate mondo into hetionet and change identifier
'''


def integrate_mondo_change_identifier():
    counter_new_nodes = 0
    counter_switched_nodes = 0
    counter_merge_nodes = 0

    for monDo, info in dict_monDO_info.items():
        # if monDo == 'MONDO:0003059':
        #     print('ohje')
        if (monDo in dict_monDo_to_DO_only_doid and len(dict_monDo_to_DO_only_doid[monDo]) == 1) or monDo in dict_mondo_xref_doid_mapping:
            counter_switched_nodes += 1

            # get the different information from monDO which will be combined
            if not monDo in dict_mondo_xref_doid_mapping:
                doid = list(dict_monDo_to_DO_only_doid[monDo])[0]
            else:
                doid=dict_mondo_xref_doid_mapping[monDo]
            monDO_synonyms = dict_monDO_info[monDo]['synonym'] if 'synonym' in dict_monDO_info else []
            monDo_def = dict_monDO_info[monDo]['definition'] if 'definition' in dict_monDO_info else ''
            monDO_xref = dict_monDO_info[monDo][
                'http://www.geneontology.org/formats/oboInOwl#hasDbXref'] if 'http://www.geneontology.org/formats/oboInOwl#hasDbXref' in dict_monDO_info else []

            umls_cuis_monDO = []
            other_xrefs_monDO = []
            for ref in monDO_xref:
                if ref[0:4] == 'UMLS':
                    umls_cuis_monDO.append(ref)
                else:
                    other_xrefs_monDO.append(ref)

            monDO_subset = []

            # combined information from monDO and DO
            monDO_synonyms.extend(dict_DO_to_info[doid]['synonyms'])
            dict_monDO_info[monDo]['synonym'] = monDO_synonyms

            dict_monDO_info[monDo]['definition'] = dict_DO_to_info[doid]['definition'] + '[FROM DOID]. ' + monDo_def

            dict_DO_to_info[doid]['alternateIds'].append(doid)
            # the alternative id get at least a ''  if their exist no alternative id, that's why they had to be
            # removed from the list
            if dict_DO_to_info[doid]['alternateIds'][0] == '':
                dict_DO_to_info[doid]['alternateIds'].remove('')
            dict_monDO_info[monDo]['doids'] = dict_DO_to_info[doid]['alternateIds']

            other_xrefs_monDO.extend(dict_DO_to_info[doid]['xrefs'])
            dict_monDO_info[monDo]['http://www.geneontology.org/formats/oboInOwl#hasDbXref'] = other_xrefs_monDO

            umls_cuis_monDO.extend(dict_DO_to_info[doid]['umls_cuis'])
            dict_monDO_info[monDo]['umls_cuis'] = umls_cuis_monDO

            monDO_subset.extend(dict_DO_to_info[doid]['subset'])
            dict_monDO_info[monDo]['subset'] = monDO_subset

            dict_DO_to_info[doid]['resource'].append('MonDO')
            string_resources = '","'.join(dict_DO_to_info[doid]['resource'])

            query = ''' Match (n:Disease{identifier:"%s"}), (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})
            Create (n)-[:equal_to_monDO]->(a)
            Set n.identifier="%s",'''
            query = query % (doid, monDo, monDo)

            for key, property in dict_monDO_info[monDo].items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#hasDbXref':
                        key = 'xrefs'
                    key = '`' + key + '`' if key[0:5] == 'http:' else key
                    if len(property) > 0 and type(property[0]) == int:
                        add_query = ''' n.%s=%s,''' % (key, property)
                    else:
                        property_string = '","'.join(property)
                        add_query = ''' n.%s=["%s"],''' % (key, property_string.replace('"', "'"))
                    query = query + add_query
                else:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#id':
                        continue
                    elif key == 'label':
                        continue
                    key = '`' + key + '`' if key[0:5] == 'http:' else key
                    # query = query + ''' n.%s="%s",'''
                    # query = query % (key, property)
                    if type(property) == int:
                        add_query = ''' n.%s=%s,''' % (key, property)
                    else:
                        add_query = ''' n.%s="%s",''' % (key, property.replace('"', "'"))
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            add_query = ''' n.url="%s" , n.resource=["%s"]; \n ''' % (url, string_resources)
            query = query + add_query
        # if has more than one doid than they have to be merge into one node
        elif monDo in dict_monDo_to_DO_only_doid:
            counter_switched_nodes += 1
            counter_merge_nodes += 1

            dict_merged_nodes[monDo] = []

            doid_with_same_name = ''
            # get the different information from monDO which will be combined
            doids = list(dict_monDo_to_DO_only_doid[monDo])
            for doid in doids:
                dict_merged_nodes[monDo].append(doid)
                if dict_DO_to_info[doid]['name'] == dict_monDO_info[monDo]['label']:
                    doid_with_same_name = doid
                elif monDo in dict_self_decision_mondo_multiple_doid:
                    doid_with_same_name = dict_self_decision_mondo_multiple_doid[monDo]
            if doid_with_same_name == '':
                print(monDo)
                print(dict_monDO_info[monDo]['label'])
                print(doids)
                continue

            monDO_synonyms = dict_monDO_info[monDo]['synonym'] if 'synonym' in dict_monDO_info else []
            monDo_def = dict_monDO_info[monDo]['definition'] if 'definition' in dict_monDO_info else ''
            monDO_xref = dict_monDO_info[monDo][
                'http://www.geneontology.org/formats/oboInOwl#hasDbXref'] if 'http://www.geneontology.org/formats/oboInOwl#hasDbXref' in dict_monDO_info else []

            umls_cuis_monDO = []
            other_xrefs_monDO = []
            for ref in monDO_xref:
                if ref[0:4] == 'UMLS':
                    umls_cuis_monDO.append(ref)
                else:
                    other_xrefs_monDO.append(ref)

            monDO_subset = []

            # combined information from monDO and DO
            monDO_synonyms.extend(dict_DO_to_info[doid_with_same_name]['synonyms'])
            dict_monDO_info[monDo]['synonym'] = monDO_synonyms

            dict_monDO_info[monDo]['definition'] = dict_DO_to_info[doid_with_same_name][
                                                       'definition'] + '[FROM DOID]. ' + monDo_def

            dict_DO_to_info[doid]['alternateIds'].append(doid_with_same_name)
            # the alternative id get at least a ''  if their exist no alternative id, that's why they had to be
            # removed from the list
            if dict_DO_to_info[doid_with_same_name]['alternateIds'][0] == '':
                dict_DO_to_info[doid_with_same_name]['alternateIds'].remove('')
            dict_monDO_info[monDo]['doids'] = dict_DO_to_info[doid_with_same_name]['alternateIds']

            other_xrefs_monDO.extend(dict_DO_to_info[doid_with_same_name]['xrefs'])
            dict_monDO_info[monDo]['http://www.geneontology.org/formats/oboInOwl#hasDbXref'] = other_xrefs_monDO

            umls_cuis_monDO.extend(dict_DO_to_info[doid_with_same_name]['umls_cuis'])
            dict_monDO_info[monDo]['umls_cuis'] = umls_cuis_monDO

            monDO_subset.extend(dict_DO_to_info[doid_with_same_name]['subset'])
            dict_monDO_info[monDo]['subset'] = monDO_subset

            dict_DO_to_info[doid_with_same_name]['resource'].append('MonDO')
            string_resources = '","'.join(dict_DO_to_info[doid_with_same_name]['resource'])

            query = ''' Match (n:Disease{identifier:"%s"}), (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})
                        Create (n)-[:equal_to_monDO]->(a)
                        Set n.identifier="%s",'''
            query = query % (doid, monDo, monDo)

            for key, property in dict_monDO_info[monDo].items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#hasDbXref':
                        key = 'xrefs'
                    key = '`' + key + '`' if key[0:5] == 'http:' else key
                    if len(property) > 0 and type(property[0]) == int:
                        add_query = ''' n.%s=%s,''' % (key, property)
                    else:
                        property_string = '","'.join(property)
                        add_query = ''' n.%s=["%s"],''' % (key, property_string.replace('"', "'"))
                    query = query + add_query
                else:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#id':
                        continue
                    elif key == 'label':
                        continue
                    key = '`' + key + '`' if key[0:5] == 'http:' else key
                    # query = query + ''' n.%s="%s",'''
                    # query = query % (key, property)
                    if type(property) == int:
                        add_query = ''' n.%s=%s,''' % (key, property)
                    else:
                        add_query = ''' n.%s="%s",''' % (key, property.replace('"', "'"))
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            add_query = ''' n.url="%s" , n.resource=["%s"]; \n ''' % (url, string_resources)
            query = query + add_query
        else:
            counter_new_nodes += 1
            query = ''' Match  (a:disease{`http://www.geneontology.org/formats/oboInOwl#id`:"%s"})
                        Create (n:Disease{identifier:"%s", '''
            query = query % (monDo, monDo)
            for key, property in dict_monDO_info[monDo].items():
                # if key in list_properties_which_should_be_an_array:
                if type(property) == list:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#hasDbXref':
                        key = 'xrefs'
                    key = '`' + key + '`' if key[0:5] == 'http:' else key
                    if len(property) > 0 and type(property[0]) == int:
                        add_query = ''' %s:%s,''' % (key, property)
                    else:
                        property_string = '","'.join(property)
                        add_query = ''' %s:["%s"],''' % (key, property_string.replace('"', "'"))
                    query = query + add_query
                else:
                    if key == 'http://www.geneontology.org/formats/oboInOwl#id':
                        continue
                    key = '`' + key + '`' if key[0:5] == 'http:' else key
                    if type(property) == int:
                        add_query = ''' %s:%s,''' % (key, property)
                    else:
                        add_query = ''' %s:"%s",''' % (key, property.replace('"', "'"))
                    query = query + add_query

            url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + monDo
            add_query = '''ctd:"no", ndf_rt:"no", resource:['MonDO'], diseaseOntology:"no", hetionet:"no", source:"Monarch Disease Ontology", url:"%s"})
                        Create (n)-[:equal_to_monDO]->(a); \n''' % (url)
            query = query + add_query

        # print(query)
        # sys.exit()
        g.run(query)


    print('number of new nodes:'+str(counter_new_nodes))
    print('number of switched nodes:'+str(counter_switched_nodes))
    print(datetime.datetime.utcnow())

    print(dict_merged_nodes)
    print(len(dict_merged_nodes))
    for merge_id, list_delete_nodes in dict_merged_nodes.items():

        for delete_node in list_delete_nodes:
            # one mapping is not ok from disease to disease of anatomical entity (DOID:7)
            if merge_id == 'MONDO:0000001' and delete_node=='DOID:7':
                continue

            merge_information_from_one_node_to_another(delete_node, merge_id, 'Disease')

    print('delete doid nodes without mapping to mondo')
    print(datetime.datetime.utcnow())
    count_removed_nodes = 0
    for doid in list_removed_doids:
        count_removed_nodes += 1
        query = '''Match (r:Disease{identifier:"%s"}) Detach Delete r''' % (doid)
        print(query)
        g.run(query)

    print('number of removed nodes with doid:' + str(count_removed_nodes))

'''
generate cypher file for subClassOf relationship
'''
def generate_cypher_file_for_relationship():
    # file counter
    file_counter = 1
    # maximal number of queries for a commit block
    constrain_number = 20000
    # maximal number of queries in a file
    creation_max_in_file = 1000000

    h = open('integrate_and_transformed_disease' + str(file_counter) + '.cypher', 'w')
    file_counter += 1
    h.write('begin \n')
    # count the number of queries
    counter_connection = 0


    query = ''' Match (a)-[r:subClassOf]->(b) Return a.`http://www.geneontology.org/formats/oboInOwl#id`, b.`http://www.geneontology.org/formats/oboInOwl#id`, r'''
    results = g.run(query)
    for child_id, parent_id, rela, in results:
        url = 'http://bioportal.bioontology.org/ontologies/MONDO/' + child_id
        dict_rela = dict(rela)
        query = ''' Match (a:Disease{identifier:"%s"}), (b:Disease{identifier:"%s"})
        Create (a)-[:SUBCLASS_OF_DsoD{license:"CC BY 4.0",unbiased:"false", source:"Monarch Disease Ontology", resource:['MonDO'] , mondo:'yes', mondo_source:"%s",'''
        query = query % (child_id, parent_id, url)
        for key, property in dict_rela.items():
            if key[0:4]=='http':
                key='`'+key+'`'
            if type(property) == list:
                property= '","'.join(property)
                add_query = '''%s:["%s"],''' % (key, property)
            else:
                add_query = '''%s:"%s",''' % (key, property)
            query += add_query

        query = query[0:-1]+''' }]->(b);\n'''

        h.write(query)
        counter_connection += 1
        if counter_connection % constrain_number == 0:
            h.write('commit \n')
            if counter_connection % creation_max_in_file == 0:
                h.close()
                h = open('integrate_and_transformed_disease' + str(file_counter) + '.cypher', 'w')
                h.write('begin \n')
                file_counter += 1
            else:
                h.write('begin \n')

    h.write('commit \n')
    h.close()
    print('number of relationships:' + str(counter_connection))


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in MonDO diseases ')

    load_in_all_monDO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in DO diseases ')

    load_in_all_DO_in_dictionary()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Map DO to monDO ')

    map_DO_to_monDO_with_DO_and_xrefs()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate the mapping files ')

    mapping_files()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('integrate and switch the nodes but ignore the multiple mapped monDO ids ')

    integrate_mondo_change_identifier()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('generate cypher file for subclassof relationship  ')

    generate_cypher_file_for_relationship()

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
