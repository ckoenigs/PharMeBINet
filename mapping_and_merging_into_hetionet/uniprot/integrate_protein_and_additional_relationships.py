'''integrate the'''
from collections import defaultdict
import datetime
import sys, csv
from collections import defaultdict
import json

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# dictionary from uniprot to gene id from pharmebinet information
dict_uniprot_to_gene_id = {}

# dictionary gene id to gene symbol/name
dict_gene_to_name = {}

# dictionary gene_id to synonyms
dict_gene_id_to_synonyms = {}

# dictionary gene id to gene name
dict_gene_id_to_resource = {}

# dictionary gene name to genes without uniprot list
dict_gene_symbol_to_gene_without_uniprot = {}
dict_gene_symbol_to_gene_id = {}

# dictionary hgnc id to gene identifiers
dict_hgnc_id_to_gene_id = {}

# list of all gene symbols which appears in multiple genes
list_double_gene_symbol_for_genes_without_uniprot_id = set([])

# dictionary gene name to gene id
dict_gene_name_to_id = defaultdict(list)

# dictionary from synonyms to gene id
dict_synonyms_to_gene_ids = defaultdict(list)

# dictionary of the uniprot ids which mapped wrong to the correct ncbi gene id
# Q96NJ1 (Uncharacterized protein FLJ30774) mapped to 158055 (c9orf163) and with tblastn I found out that the protein is
# part of the orf
dict_wrong_uniprot_to_correct_gene_id = {
    'Q8N8H1': '399669',
    'A2RUG3': '353515',
    'E5RIL1': '107983993',
    'P0DI82': '10597',
    'P0DMW3': '100129361',
    'H3BUK9': '100287399',
    'Q5XG87': '64282',
    'Q8NDF8': '11044',
    'A0A024RBG1': '440672',
    'P0DMR1': '101060301',
    'P30042': '102724023',
    'P0DPD8': '110599583',
    'P0DP73': '100133267',
    'P0DMV2': '102723680',
    'P0DMV1': '102723737',
    'A0A1B0GUU1': '110806298'
}

'''
Find mapping between genes and proteins
{identifier:100996717}
{identifier:107983993}
'''


def get_all_genes():
    query = '''MATCH (n:Gene) RETURN n.identifier,  n.gene_symbols, n.xrefs, n.name, n.synonyms, n.resource'''
    results = g.run(query)
    counter_uniprot_to_multiple_genes = 0
    counter_all_genes = 0
    list_double_names = set([])
    for record in results:
        [gene_id, genesymbols, xrefs, name, synonyms, resource] = record.values()
        counter_all_genes += 1
        dict_gene_id_to_resource[gene_id] = set(resource)

        if xrefs:
            for xref in xrefs:
                if xref.startswith('HGNC'):
                    hgnc_id = xref.split(':', 1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_hgnc_id_to_gene_id, hgnc_id, gene_id)

        if gene_id == '28299':
            print('ok')

        # prepare dictionary from gensymbol to gene ids and remember which gene symbols appears in multiple genes
        if genesymbols:

            genesymbols = [x.lower() for x in genesymbols]
            dict_gene_to_name[gene_id] = genesymbols
            for genesymbol in genesymbols:
                if not genesymbol in dict_gene_symbol_to_gene_id:
                    dict_gene_symbol_to_gene_id[genesymbol] = [gene_id]
                else:
                    list_double_gene_symbol_for_genes_without_uniprot_id.add(genesymbol)

                    dict_gene_symbol_to_gene_id[genesymbol].append(gene_id)
        else:
            dict_gene_to_name[gene_id] = [name.lower()]

        # fill the gene name to gene id dictionary
        if name:
            if name.lower() in dict_gene_name_to_id:
                list_double_names.add(name.lower())
                dict_gene_name_to_id[name.lower()].append(gene_id)
            else:
                dict_gene_name_to_id[name.lower()].append(gene_id)
        if synonyms:
            dict_gene_id_to_synonyms[gene_id] = set()
            for synonym in synonyms:
                synonym = synonym.lower()
                dict_gene_id_to_synonyms[gene_id].add(synonym)
                dict_synonyms_to_gene_ids[synonym.lower()].append(gene_id)

    print('number of genes:' + str(counter_all_genes))
    print('number of multiple name:' + str(len(list_double_names)))


# files with rela from uniprot protei to gene
file_uniprots_gene_rela = open('uniprot_gene/db_uniprot_to_gene_rela.tsv', 'w')
writer_rela = csv.writer(file_uniprots_gene_rela, delimiter='\t')
writer_rela.writerow(
    ['uniprot_id', 'gene_id', 'alternative_ids', 'name_mapping', 'resource_node', 'how_mapped'])

# list of all uniprot ids which where wrong mapped and already found in the program to avoid duplication in the file
list_already_included = []

# list of all already integrated pairs of gene uniprot id
list_already_integrated_pairs_gene_protein = []

# counter for not matching gene names
count_not_mapping_gene_name = 0

'''
this goes throu a list of mapping gens and check out if they really do not exists already
if not integrate them into the tsv
'''


def check_and_add_rela_pair(identifier, uniprot_id, gene_ids, secondary_uniprot_ids, name_mapping, how_mapped):
    for gene_id in gene_ids:
        if gene_id not in dict_gene_id_to_resource:
            print('gene problem', gene_id)
            continue
        if not (identifier, gene_id) in list_already_integrated_pairs_gene_protein:
            writer_rela.writerow(
                [identifier, gene_id, secondary_uniprot_ids, name_mapping,
                 add_resource(dict_gene_id_to_resource[gene_id]), how_mapped])
            list_already_integrated_pairs_gene_protein.append(
                (identifier, gene_id))
            list_already_included.append(uniprot_id)


''' 
check if the uniprot id is in dictionary uniprot to gene and write into right file
all inputs are from the uniprot nodes
uniprot_id can be identifier or an alternative uniprot id 

gene_names are the genesymbol of UniProt
gene_ids are the gene ids which from uniprot
'''


def check_and_write_uniprot_ids(uniprot_id, name, identifier, secondary_uniprot_ids, gene_names, gene_ids,
                                primary_gene_symbols, hgnc_ids):
    global count_not_mapping_gene_name
    found_at_least_on = False

    gene_names = [x.lower() for x in gene_names]
    gene_names = list(set(gene_names))
    genes = []
    same_gene_name = False

    name = name.split(' {E')[0].lower()

    # if no gene is found in the multiple or single dictionary, search with name for on mapping or with the gene_ids from uniprot
    if identifier not in list_already_included:
        if identifier == 'P0DI82':
            print('blub')
        # check out if the mapping gene ids are good by checking the name
        # but it seems that even if the name are not the same they map correct
        if gene_ids:
            # check_and_add_rela_pair(identifier, uniprot_id, gene_ids, secondary_uniprot_ids, '')
            # return True, gene_ids
            lower_primary_gene_symbols = {x.lower() for x in primary_gene_symbols}
            symbol_interaction = lower_primary_gene_symbols.intersection(dict_gene_symbol_to_gene_id.keys())
            if len(symbol_interaction) > 0:
                list_gene_id_from_name = set()
                for symbol in symbol_interaction:
                    list_gene_id_from_name = list_gene_id_from_name.union(dict_gene_symbol_to_gene_id[symbol])
                intersection = set(gene_ids).intersection(list_gene_id_from_name)
                if len(intersection) > 0:
                    check_and_add_rela_pair(identifier, uniprot_id, intersection, secondary_uniprot_ids, 'yes',
                                            'ncbi_id_and_gene_symbol')
                    return True, genes
                else:
                    symbol_synonym_interaction = lower_primary_gene_symbols.intersection(
                        dict_synonyms_to_gene_ids.keys())
                    list_gene_id_from_synonyms = set()
                    for symbol in symbol_synonym_interaction:
                        list_gene_id_from_synonyms = list_gene_id_from_synonyms.union(dict_synonyms_to_gene_ids[symbol])
                    intersection = set(gene_ids).intersection(list_gene_id_from_synonyms)
                    if len(intersection) > 0:
                        check_and_add_rela_pair(identifier, uniprot_id, intersection, secondary_uniprot_ids, 'yes',
                                                'ncbi_id_and_gene_symbol_synonym')
                        return True, genes
                    else:
                        print('use only the symbol gene ids')
                        check_and_add_rela_pair(identifier, uniprot_id, list_gene_id_from_name, secondary_uniprot_ids,
                                                'yes',
                                                'ncbi_id_but_only_gene_symbol')
                        return True, genes
            else:
                print('only gene id mapping')
                check_and_add_rela_pair(identifier, uniprot_id, gene_ids, secondary_uniprot_ids, '', 'ncbi_id')
                return True, gene_ids

        if len(hgnc_ids) > 0:
            gene_ids_from_hgnc = set()
            for hgnc_id in hgnc_ids:
                if hgnc_id in dict_hgnc_id_to_gene_id:
                    gene_ids_from_hgnc = gene_ids_from_hgnc.union(dict_hgnc_id_to_gene_id[hgnc_id])
            if len(gene_ids_from_hgnc) > 0:
                check_and_add_rela_pair(identifier, uniprot_id, gene_ids_from_hgnc,
                                        secondary_uniprot_ids, 'yes', 'hgnc_mapping')
                return True, gene_ids_from_hgnc
        if primary_gene_symbols:
            lower_primary_gene_symbols = {x.lower() for x in primary_gene_symbols}
            gene_ids_from_symbol = set()
            symbol_interaction = lower_primary_gene_symbols.intersection(dict_gene_symbol_to_gene_id.keys())
            symbol_synonym_interaction = lower_primary_gene_symbols.intersection(dict_synonyms_to_gene_ids.keys())

            if len(symbol_interaction) > 0:
                for symbol in symbol_interaction:
                    gene_ids_from_name = dict_gene_symbol_to_gene_id[symbol]
                    gene_ids_from_symbol = gene_ids_from_symbol.union(gene_ids_from_name)
                    # print('ok gene symbol works primary')
                    text = 'direct'
            elif len(symbol_synonym_interaction) > 0:
                for symbol in symbol_synonym_interaction:
                    gene_ids_from_symbol = gene_ids_from_symbol.union(dict_synonyms_to_gene_ids[symbol])
                    # print('only name and id is not existing primary')
                    text = 'synonyms'
            if len(gene_ids_from_symbol) > 0:
                check_and_add_rela_pair(identifier, uniprot_id, gene_ids_from_symbol,
                                        secondary_uniprot_ids, 'yes', text + '_primary_gene_symbol')
                return True, gene_ids_from_symbol

        if gene_names:
            gene_ids_from_symbol = set()
            for gene_name in gene_names:
                if gene_name in dict_gene_symbol_to_gene_id:
                    gene_ids_from_name = dict_gene_symbol_to_gene_id[gene_name]
                    gene_ids_from_symbol = gene_ids_from_symbol.union(gene_ids_from_name)
                    print('ok gene symbol works', uniprot_id, gene_ids, gene_names)
                    text = 'direct'
                elif gene_name in dict_synonyms_to_gene_ids:
                    gene_ids_from_symbol = gene_ids_from_symbol.union(dict_synonyms_to_gene_ids[gene_name])
                    print('only name and id is not existing', uniprot_id, gene_ids, gene_names)
                    text = 'synonyms'
            if len(gene_ids_from_symbol) > 0:
                check_and_add_rela_pair(identifier, uniprot_id, gene_ids_from_symbol,
                                        secondary_uniprot_ids, 'yes', text + '_gene_names')
                return True, gene_ids_from_symbol

        # check if mapping is possible with gene symbol
        ## I have to check this out more but it seems like it works
        list_of_possible_mapped_gene_ids = set([])
        for gene_name in gene_names:
            if gene_name in dict_gene_symbol_to_gene_id and not gene_name in list_double_gene_symbol_for_genes_without_uniprot_id:
                gene_ids_from_name = dict_gene_symbol_to_gene_id[gene_name]
                list_of_possible_mapped_gene_ids = list_of_possible_mapped_gene_ids.union(gene_ids_from_name)
                list_already_included.append(uniprot_id)
            elif gene_name in list_double_gene_symbol_for_genes_without_uniprot_id:
                print(gene_name)
                print(identifier)
                print(dict_gene_symbol_to_gene_id[gene_name])
                print('multiple name name mapping')

        # the multiple mapping with gene symbol are not the best only 4 of 14 this make sense but for the other it would be manual mapping
        if len(list_of_possible_mapped_gene_ids) == 1:
            check_and_add_rela_pair(identifier, uniprot_id, list_of_possible_mapped_gene_ids,
                                    secondary_uniprot_ids, 'yes', 'multiple_name_mapping')

            # print(identifier)
            # print(list_of_possible_mapped_gene_ids)
            found_at_least_on = True
            # no mapping from the gene or protein and no gene symbol

    return found_at_least_on, genes


def split_string_to_get_one_value(try_to_get_value, symbol, which):
    """
    check if the list has at least legth 2
    :param try_to_get_value: list
    :param symbol: one character
    :param which: string
    :return: string
    """
    return_value = ''
    if len(try_to_get_value) > 1:
        return_value = try_to_get_value[1].split(symbol, 1)[0]
    else:
        if not try_to_get_value[0].startswith('Note'):
            print('no ' + which)
            print(try_to_get_value)
    return return_value


def write_cypher_file():
    """
    generate the different cpyher queries and write into cypher file
    :return:
    """

    # cypher file for nodes and relas
    file_cypher = open('output/cypher.cypher', 'w')
    file_cypher_edge = open('output/cypher_gene.cypher', 'w')

    query_property = '''MATCH (p:Protein_Uniprot) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields as l;'''

    results = g.run(query_property)

    query = '''MATCH (p:Protein_Uniprot{identifier:line.uniprot_id}) Create (p)<-[:equal_to_uniprot]-(:Protein{'''

    for property in results:
        property = property.data()['l']
        # the go classifiers are in the rela to bc, cc and mf and the gene information are in the rela to gene
        if property in ['go_classifiers', 'gene_name', 'gene_id']:
            continue
        # to have the prepared xrefs
        elif property == 'xrefs':
            query += property + ':split(line.' + property + ',"|"), '
        elif property == 'accessions':
            query += 'alternative_ids:p.' + property + ', '
        elif property == 'as_sequence':
            query += property + 's:[p.' + property + '], '
        else:
            query += property + ':p.' + property + ', '
    query += 'uniprot:"yes", url:"https://www.uniprot.org/uniprot/"+p.identifier, source:"UniProt", resource:["UniProt"], license:"CC BY 4.0"}) '
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/uniprot/output/db_uniprot_ids.tsv',
                                              query)
    file_cypher.write(query)
    file_cypher.write(pharmebinetutils.prepare_index_query('Protein', 'identifier'))

    # query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/uniprot/uniprot_gene/db_gene_uniprot_delete.tsv" As line FIELDTERMINATOR "\\t" Match (g:Gene{identifier:line.gene_id}) With g,[x IN g.uniProtIDs WHERE x <> line.uniprot_id]  as filterdList
    #              Set g.uniProtIDs=filterdList '''
    # file_cypher.write(query)

    query = ''' MATCH (n:Protein{identifier:line.uniprot_id}), (g:Gene{identifier:line.gene_id}) Set g.resource=split(line.resource_node,'|'), g.uniprot='yes' Create (g)-[:PRODUCES_GpP{name_mapping:line.name_mapping, uniprot:"yes" ,resource:['UniProt'],license:'CC BY 4.0', url:'https://www.uniprot.org/uniprot/'+line.uniprot_id, source:"UniProt", how_mapped:line.how_mapped}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/uniprot/uniprot_gene/db_uniprot_to_gene_rela.tsv',
                                              query)
    file_cypher_edge.write(query)


def add_resource(set_resource):
    """
    Add source to resource and prepare to string
    :param set_resource:
    :return:
    """
    set_resource.add('UniProt')
    return '|'.join(set_resource)


# dictionary from go label to set of pairs
dict_go_label_to_pairs = {
    'bp': set(),
    'cc': set(),
    'mf': set()
}

'''
Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
'''


def get_gather_protein_info_and_generate_relas():
    # file with every uniprot identifier
    file_uniprots_ids = open('output/db_uniprot_ids.tsv', 'w')
    writer_uniprots_ids = csv.writer(file_uniprots_ids, delimiter='\t')
    writer_uniprots_ids.writerow(['uniprot_id', 'xrefs'])

    # generate a file with all uniprots which mapped to multiple genes
    file_uniprots_genes = open('uniprot_gene/db_uniprots_to_genes_multi_map.tsv', 'w')
    writer_uniprots_genes_multi_mapps = csv.writer(file_uniprots_genes, delimiter='\t')
    writer_uniprots_genes_multi_mapps.writerow(['uniprot_ids', 'gene_id'])

    # query to get all Protein information {identifier:'P0DMV0'} {identifier:'Q05066'} {identifier:'P0DPK4'} {identifier:'E5RIL1'} {identifier:'P01009'}
    query = '''MATCH (n:Protein_Uniprot) RETURN n '''
    results = g.run(query)

    print(datetime.datetime.now())
    # counter of combined gene protein interaction
    counter_existing_gene_protein_rela = 0
    # counter all proteins
    counter_all_proteins = 0

    # go through all Proteins
    # find overlap between protein and genes
    # maybe check out the go information to generate further relationships to go
    for record in results:
        node = record.data()['n']
        counter_all_proteins += 1
        # get true if on of the uniprot of this nodes are in the dictionary uniprot to gene
        found_at_least_on = False

        # gather all uniprot ids which mapped to at least one gene
        overlap_uniprot_ids = set([])
        # gather all genes which mapped to all uniprots of this node
        set_list_mapped_genes = set([])

        # get the Uniprot id
        identifier = node['identifier']
        # print(identifier)

        # get the name of the node
        name = node['name']
        # get all xrefs of the node
        xrefs = node['xrefs'] if 'xrefs' in node else []

        # the gene symbol
        geneSymbols = node['gene_name'] if 'gene_name' in node else []
        primary_gene_symbols = set()
        set_gene_symbol = set()
        for geneSymbol in geneSymbols:
            splitted_genesymbol = geneSymbol.split(':')
            set_gene_symbol.add(splitted_genesymbol[1])
            if splitted_genesymbol[0] == 'primary':
                primary_gene_symbols.add(splitted_genesymbol[1])

        hgnc_ids = set()
        for xref in xrefs:
            if xref.startswith('HGNC'):
                hgnc_ids.add(xref.split(':', 1)[1])

        # the gene ids
        gene_ids = [x.replace('GeneID:', '') for x in node['gene_id']] if 'gene_id' in node else []

        # first check out the identifier
        # also check if it has multiple genes or not
        # print(identifier)
        in_list, genes = check_and_write_uniprot_ids(identifier, name, identifier, '', set_gene_symbol, gene_ids,
                                                     primary_gene_symbols, hgnc_ids)
        if in_list:
            found_at_least_on = True
            overlap_uniprot_ids.add(identifier)
            set_list_mapped_genes = set_list_mapped_genes.union(genes)

        # if one mapped gene is found then count this and also if multiple genes mappes to multiple uniprots ids write this in a new file to check the manual
        if found_at_least_on:
            counter_existing_gene_protein_rela += 1
            if len(set_list_mapped_genes) > 1 and len(overlap_uniprot_ids) > 1:
                overlap_uniprot_ids = ';'.join(overlap_uniprot_ids)
                set_list_mapped_genes = [str(x) for x in list(set_list_mapped_genes)]
                set_list_mapped_genes = ';'.join(set_list_mapped_genes)
                writer_uniprots_genes_multi_mapps.writerow([overlap_uniprot_ids, set_list_mapped_genes])

        new_xrefs = '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'Protein'))
        writer_uniprots_ids.writerow([identifier, new_xrefs])

    print('number of existing gene protein rela:' + str(counter_existing_gene_protein_rela))
    print('number of all proteins:' + str(counter_all_proteins))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gather all information of the pharmebinet genes')

    get_all_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('write cypher queries into cypher file')

    write_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('gather all information of the proteins')

    get_gather_protein_info_and_generate_relas()

    driver.close()

    print('number of not matching gene names between protein and gene:' + str(count_not_mapping_gene_name))

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
