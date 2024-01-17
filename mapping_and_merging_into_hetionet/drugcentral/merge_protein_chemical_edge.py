import datetime
import csv
from collections import defaultdict
import sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


# dictionary rela type to csv_mapped, new
dict_rela_type_to_csv_files = {}


def load_edge_into_dictionary(rela_type):
    """Load existing interaction pairs between chemical-protein nodes with a given relationship type from Pharmebinet
    and prepare the tsv and cypher queries.
    """

    rela_full = f'{rela_type}_CH{"".join([x[0].lower() for x in rela_type.split("_")])}P'

    query = f'''MATCH (n:Chemical)-[r:{rela_full}]->(m:Protein) RETURN n.identifier,m.identifier, r.resource, r.pubMed_ids, r.ref_links,r.ref_textbooks, r.actions, r.activities  '''
    results = g.run(query)

    csv_writer, csv_writer_new = prepare_tsv_and_cypher(rela_full)
    dict_rela_type_to_csv_files[rela_type] = [csv_writer, csv_writer_new]

    dict_pair_to_resource_pmids_ref_links_books = {}
    for record in results:
        [node_1_id, node_2_id, resource, pubmed_ids, ref_links, ref_textbooks, rela_action_type,
         rela_activities] = record.values()

        pair = (node_1_id, node_2_id)
        pubmed_ids = set(pubmed_ids) if pubmed_ids is not None else set()
        ref_links = set(ref_links) if ref_links else set()
        ref_textbooks = set(ref_textbooks) if ref_textbooks else set()
        rela_action_type = set(rela_action_type) if rela_action_type else set()
        rela_activities = set(rela_activities) if rela_activities else set()
        dict_pair_to_resource_pmids_ref_links_books[pair] = [resource, pubmed_ids, ref_links, ref_textbooks,
                                                             rela_action_type, rela_activities]
    return dict_pair_to_resource_pmids_ref_links_books


# generate cypher file
cypher_file = open('output/cypher_edge.cypher', 'a', encoding='utf-8')


def prepare_tsv_and_cypher(rela_type):
    """
    prepare tsv file and add cypher query to cypher file
    :return:
    """
    file_name = f'edge/chemical_protein_{rela_type}_merged.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(
        ['id1', 'id2', 'resource', 'pmids', 'links', 'books', 'dois', 'act_comment', 'act_source', 'act_source_url',
         'moa_source', 'moa_source_url',  'act_type', 'actions'])
    file_name_new = f'edge/chemical_protein_{rela_type}_new.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_writer_new = csv.writer(file_new, delimiter='\t')
    csv_writer_new.writerow(
        ['id1', 'id2', 'pmids', 'links', 'books', 'dois', 'dc_id', 'act_comment', 'act_source', 'act_source_url',
         'moa_source', 'moa_source_url',  'act_type', 'actions'])

    query = pharmebinetutils.get_all_properties_of_on_label % ('DC_Bioactivity')
    results = g.run(query)
    list_merged_properties = []
    list_new_properties = []
    for result in results:
        [prop] = result.values()
        if prop in ['act_comment', 'act_source', 'act_source_url', 'moa_source', 'moa_source_url', 'relation']:
            list_merged_properties.append(f'm.{prop}s=split(line.{prop},"|")')
            list_new_properties.append(f'{prop}s:split(line.{prop},"|")')
        elif prop == 'act_type':
            list_merged_properties.append(f'm.activities=split(line.{prop},"|")')
            list_new_properties.append(f'activities:split(line.{prop},"|")')

    query = f'''Match (n:Chemical{{identifier:line.id1}})-[m:{rela_type}]->(o:Protein{{identifier:line.id2}}) Set m.resource=split(line.resource,"|"), m.drugcentral='yes', m.pubMed_ids=split(line.pmids,"|"), m.ref_links=split(line.links,"|"), m.ref_dois=split(line.dois,"|"), m.ref_textbooks=split(line.books,"|"), {", ".join(list_merged_properties)}'''
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     'mapping_and_merging_into_hetionet/drugcentral/' + file_name,
                                                     query)
    cypher_file.write(query_create)
    query = f'''Match (n:Chemical{{identifier:line.id1}}), (o:Protein{{identifier:line.id2}}) Create (n)-[m:{rela_type}{{resource:['DrugCentral'], source:'DrugCentral', url:"https://drugcentral.org/drugcard/"+line.dc_id, ref_dois:split(line.dois,"|"),actions:split(line.actions,"|"), license:"Creative Commons Attribution-ShareAlike 4.0 International Public License", drugcentral:'yes', pubMed_ids:split(line.pmids,"|"), ref_links:split(line.links,"|"), ref_textbooks:split(line.books,"|"), {", ".join(list_new_properties)} }}]->(o)'''
    query_create = pharmebinetutils.get_query_import(path_of_directory,
                                                     'mapping_and_merging_into_hetionet/drugcentral/' + file_name_new,
                                                     query)
    cypher_file.write(query_create)

    return csv_writer, csv_writer_new


# dictionary bioactivity to description and type
dict_bioactivity_to_description_and_type = {}


def load_bioactivity_actiontype():
    """ Load all action type for the different bioactivity nodes and write information into dictionary
    """
    query = 'MATCH (n:DC_Bioactivity)--(m:DC_ActionType) Return ID(n), m.description, m.type '
    results = g.run(query)
    for result in results:
        [id_bioativity, description, edge_type] = result.values()
        if id_bioativity in dict_bioactivity_to_description_and_type:
            print('reallllllllyyyyyy bad')
        dict_bioactivity_to_description_and_type[id_bioativity] = [description, edge_type]


# dictionary bioactivity to reference
dict_bioactivity_to_reference = {}


def load_bioactivity_reference():
    """ Load all action type for the different bioactivity nodes and write information into dictionary
    """
    query = 'MATCH (n:DC_Bioactivity)--(m:DC_Reference) Return ID(n), m.pmid, m.isbn10, m.url, m.document_id, m.doi,m.title, m.type '
    results = g.run(query)
    for result in results:
        [id_bioativity, pmid, isbn10, url, document_id, doi, title, ref_type] = result.values()
        if id_bioativity in dict_bioactivity_to_reference and ref_type in dict_bioactivity_to_reference[id_bioativity]:
            if pmid:
                dict_bioactivity_to_reference[id_bioativity][ref_type][0].add(str(pmid))
            if isbn10:
                dict_bioactivity_to_reference[id_bioativity][ref_type][1].append(isbn10)
            if url:
                dict_bioactivity_to_reference[id_bioativity][ref_type][2].append(url)
            if document_id:
                dict_bioactivity_to_reference[id_bioativity][ref_type][3].append(document_id)
            if doi:
                dict_bioactivity_to_reference[id_bioativity][ref_type][4].append(doi)
            if title:
                dict_bioactivity_to_reference[id_bioativity][ref_type][5].append(title)
        elif id_bioativity in dict_bioactivity_to_reference:
            pmid = set([str(pmid)]) if pmid else set()
            isbn10 = [isbn10] if isbn10 else []
            url = [url] if url else []
            document_id = [document_id] if document_id else []
            doi = [doi] if doi else []
            title = [title] if title else []
            dict_bioactivity_to_reference[id_bioativity][ref_type] = [pmid, isbn10, url, document_id, doi, title]
        else:
            dict_bioactivity_to_reference[id_bioativity] = {}
            pmid = set([str(pmid)]) if pmid else set()
            isbn10 = [isbn10] if isbn10 else []
            url = [url] if url else []
            document_id = [document_id] if document_id else []
            doi = [doi] if doi else []
            title = [title] if title else []
            dict_bioactivity_to_reference[id_bioativity][ref_type] = [pmid, isbn10, url, document_id, doi, title]


def prepare_ref_information_tor_the_different_sources(rela_ids, pubmed_ids, ref_links, ref_textbooks, all_dois):
    """
    get bioactive information and add the information depending on the type to the different set
    :param rela_ids:
    :param pubmed_ids:
    :param ref_links:
    :param ref_textbooks:
    :param all_dois:
    :return:
    """
    for rela_id in rela_ids:
        if rela_id in dict_bioactivity_to_reference:
            for ref_type, [pmids, isbn10s, urls, document_ids, dois, titles] in dict_bioactivity_to_reference[
                rela_id].items():
                if ref_type == 'JOURNAL ARTICLE':
                    if len(pmids) > 0:
                        pubmed_ids = pubmed_ids.union(pmids)
                    elif len(dois):
                        all_dois = dois
                    else:
                        print('journal with different information, what to do')
                elif ref_type == 'DRUG LABEL':
                    counter = 0
                    for url in urls:
                        ref_links.add(document_ids[counter] + '::::' + url)
                        counter += 1
                elif ref_type in ['ONLINE RESOURCE', 'CLINICAL TRIAL']:
                    counter = 0
                    for url in urls:
                        ref_links.add(document_ids[counter] + f'::{titles[counter]}::' + url)
                        counter += 1
                elif ref_type == 'BOOK':
                    counter = 0
                    for title in titles:
                        ref_textbooks.add(f'::{isbn10s[counter]}::' + title)
                        counter += 1
                elif ref_type == 'PATENT':
                    counter = 0
                    for document_id in document_ids:
                        ref_links.add(document_id + f'::{titles[counter]}::')
                        counter += 1
    return pubmed_ids, ref_links, ref_textbooks, all_dois


def prepare_relationships_information_from_bioactivity(rela_infos):
    # define the different information sets
    act_comments = set()
    act_source = set()
    act_source_url = set()
    moa_source = set()
    moa_source_url = set()
    act_type = set()

    for rela_info in rela_infos:
        if 'act_comment' in rela_info:
            act_comments.add(rela_info['act_comment'])
        if 'act_source' in rela_info:
            act_source.add(rela_info['act_source'])
        if 'act_source_url' in rela_info:
            act_source_url.add(rela_info['act_source_url'])
        if 'moa_source' in rela_info:
            moa_source.add(rela_info['moa_source'])
        if 'moa_source_url' in rela_info:
            moa_source_url.add(rela_info['moa_source_url'])
        if 'act_type' in rela_info:
            # print(rela_info['relation'], rela_info['act_value'])
            if 'act_value' in rela_info:
                relation_string = rela_info['relation'] if 'relation' in rela_info else '='
                act_type.add(rela_info['act_type'] + relation_string + rela_info['act_value'])
            else:
                act_type.add(rela_info['act_type'])
    return act_comments, act_source, act_source_url, moa_source, moa_source_url, act_type


dict_rela_type_to_existing_rela_pairs_to_information = {}


def load_and_map_DC_chemical_protein_edges():
    query = f'''MATCH (n:Chemical)--(a:DC_Structure)-[]->(b:DC_Bioactivity)--(m:Protein) Where b.act_source<>'UNKNOWN' RETURN n.identifier,m.identifier, b, ID(b), a.id '''
    results = g.run(query)

    dictionary_pair_rela_type_to_bioactivity_ids = {}

    for record in results:
        [node_1_id, node_2_id, rela, rela_id, structure_id] = record.values()
        rela_type = 'ASSOCIATES'
        rela_type_dc = None
        if rela_id in dict_bioactivity_to_description_and_type:
            rela_type_dc = dict_bioactivity_to_description_and_type[rela_id][1]
            if rela_type_dc in ['SUBSTRATE', 'RELEASING AGENT', 'OTHER', 'SEQUESTERING AGENT', 'CHELATING AGENT']:
                rela_type = 'ASSOCIATES'
            elif rela_type_dc in ['OXIDATIVE ENZYME', 'PROTEOLYTIC ENZYME', 'PHARMACOLOGICAL CHAPERONE',
                                  'HYDROLYTIC ENZYME']:
                rela_type = 'IS_ACTIVE_ON_POLYPEPTIDE_LEVEL'
            elif rela_type_dc in ['OPENER', 'MEMBRANE PERMEABILIZER']:
                rela_type = 'IS_ACTIVE_ON_CELLULAR_LEVEL'
            elif rela_type_dc in ['GATING INHIBITOR', 'INHIBITOR', 'MINIMUM INHIBITORY CONCENTRATION',
                                  'ANTISENSE INHIBITOR']:
                rela_type = 'INHIBITS'
            elif rela_type_dc in ['BLOCKER', 'ANTAGONIST']:
                rela_type = 'DOWNREGULATES'
            elif rela_type_dc in ['ACTIVATOR']:
                rela_type = 'UPREGULATES'
            elif rela_type_dc in ['BINDING AGENT']:
                rela_type = 'BINDS'
            elif rela_type_dc in ['ANTIBODY BINDING']:
                rela_type = 'IS_ACTIVE_AS_ANTIBODY'
            elif rela_type_dc in ['DNA STRAND BREAK']:
                rela_type = 'IS_ACTIVE_ON_DNA_OR_RNA_LEVEL'
            elif rela_type_dc in ['ALKYLATING AGENT', 'CROSS-LINKING AGENT']:
                rela_type = 'IS_ACTIVE_IN_METABOLISM'
            elif rela_type_dc in ['NEGATIVE MODULATOR', 'POSITIVE MODULATOR', 'POSITIVE ALLOSTERIC MODULATOR',
                                  'PARTIAL AGONIST', 'ALLOSTERIC MODULATOR', 'NEGATIVE ALLOSTERIC MODULATOR',
                                  'MODULATOR', 'INVERSE AGONIST', 'AGONIST', 'ALLOSTERIC ANTAGONIST']:
                rela_type = 'REGULATES'
            else:
                sys.exit('no type definition')

        if rela_type not in dict_rela_type_to_existing_rela_pairs_to_information:
            dict_existing_pairs_to_resource_pmids_links_books = load_edge_into_dictionary(rela_type)
            dict_rela_type_to_existing_rela_pairs_to_information[
                rela_type] = dict_existing_pairs_to_resource_pmids_links_books

        if (node_1_id, node_2_id, rela_type) not in dictionary_pair_rela_type_to_bioactivity_ids:
            dictionary_pair_rela_type_to_bioactivity_ids[(node_1_id, node_2_id, rela_type)] = [set(), structure_id, [],
                                                                                               set()]
        dictionary_pair_rela_type_to_bioactivity_ids[(node_1_id, node_2_id, rela_type)][0].add(rela_id)
        dictionary_pair_rela_type_to_bioactivity_ids[(node_1_id, node_2_id, rela_type)][2].append(rela)
        if rela_type_dc:
            dictionary_pair_rela_type_to_bioactivity_ids[(node_1_id, node_2_id, rela_type)][3].add(rela_type_dc.lower())

        # if rela_id not in dict_bioactivity_to_reference:
        #     print('no edge reference', node_1_id, node_2_id)

    for (node_1_id, node_2_id, rela_type), [rela_ids, structure_id,
                                            rela_infos,
                                            rela_types] in dictionary_pair_rela_type_to_bioactivity_ids.items():

        # print(node_1_id,node_2_id)
        if (node_1_id, node_2_id) in dict_rela_type_to_existing_rela_pairs_to_information[rela_type]:
            [resource, pubmed_ids, ref_links, ref_textbooks, rela_action_type, rela_activities] = \
                dict_rela_type_to_existing_rela_pairs_to_information[rela_type][(node_1_id, node_2_id)]
            all_dois = []
            pubmed_ids, ref_links, ref_textbooks, all_dois = prepare_ref_information_tor_the_different_sources(rela_ids,
                                                                                                               pubmed_ids,
                                                                                                               ref_links,
                                                                                                               ref_textbooks,
                                                                                                               all_dois)

            # print(node_1_id, node_2_id, rela_id,pubmed_ids,all_dois)
            rela_action_type = rela_action_type.union(rela_types)

            act_comments, act_source, act_source_url, moa_source, moa_source_url, act_type = prepare_relationships_information_from_bioactivity(
                rela_infos)

            rela_activities = rela_activities.union(act_type)

            # 'act_comment', 'act_source', 'act_source_url',
            #          'moa_source', 'moa_source_url', 'relation', 'act_type','actions'
            dict_rela_type_to_csv_files[rela_type][0].writerow(
                [node_1_id, node_2_id, pharmebinetutils.resource_add_and_prepare(resource, 'DrugCentral'),
                 '|'.join(pubmed_ids), '|'.join(ref_links), '|'.join(ref_textbooks), '|'.join(all_dois),
                 '|'.join(act_comments), '|'.join(act_source), '|'.join(act_source_url), '|'.join(moa_source),
                 '|'.join(moa_source_url),  '|'.join(rela_activities), '|'.join(rela_action_type)])
        else:
            pubmed_ids = set()
            ref_links = set()
            ref_textbooks = set()
            all_dois = set()
            pubmed_ids, ref_links, ref_textbooks, all_dois = prepare_ref_information_tor_the_different_sources(rela_ids,
                                                                                                               pubmed_ids,
                                                                                                               ref_links,
                                                                                                               ref_textbooks,
                                                                                                               all_dois)
            act_comments, act_source, act_source_url, moa_source, moa_source_url,  act_type = prepare_relationships_information_from_bioactivity(
                rela_infos)
            # 'act_comment', 'act_source', 'act_source_url',
            #          'moa_source', 'moa_source_url', 'relation', 'act_type','actions'
            dict_rela_type_to_csv_files[rela_type][1].writerow(
                [node_1_id, node_2_id, '|'.join(pubmed_ids), '|'.join(ref_links), '|'.join(ref_textbooks),
                 '|'.join(all_dois), structure_id, '|'.join(act_comments), '|'.join(act_source),
                 '|'.join(act_source_url), '|'.join(moa_source),
                 '|'.join(moa_source_url), '|'.join(act_type), '|'.join(rela_types)])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path drugcentral atc edge')

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')
    create_connection_with_neo4j()

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('load edge type')

    load_bioactivity_actiontype()

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('load edge references')

    load_bioactivity_reference()

    print(pharmebinetutils.print_hline())
    print(datetime.datetime.now())
    print('map')

    load_and_map_DC_chemical_protein_edges()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
