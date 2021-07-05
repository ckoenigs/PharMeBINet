'''integrate the'''
from collections import defaultdict
import datetime
import sys, csv
from collections import defaultdict
import json

sys.path.append("../..")
import create_connection_to_databases

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    # authenticate("localhost:7474", "neo4j", "test")
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary of biological process key is the id and value the name
dict_bp_to_name = {}
# dictionary of cellular component key is the id and value the name
dict_cc_to_name = {}
# dictionary of molecular function key is the id and value the name
dict_mf_to_name = {}

# dictionary of biological process key is the alt id and value the id
dict_alt_bp_to_id = {}
# dictionary of cellular component key is the alt id and value the id
dict_alt_cc_to_id = {}
# dictionary of molecular function key is the alt id and value the id
dict_alt_mf_to_id = {}


# function integrate identifier and name into the right dictionary
def integrate_information_into_dict(entity_name, dict_go, dict_alt_go_to_go):
    query = '''MATCH (n:''' + entity_name + ''') RETURN n.identifier, n.name, n.alternative_ids'''
    results = g.run(query)

    counter_entities = 0
    for identifier, name, alt_go_ids, in results:
        dict_go[identifier] = name
        counter_entities += 1
        if alt_go_ids:
            for alt_go_id in alt_go_ids:
                dict_alt_go_to_go[alt_go_id] = identifier

    print('It exists ' + str(counter_entities) + ' ' + entity_name)
    print(len(dict_go))


# load all information of biological process, cellular component and molecular function and put this information into a dictionary
def load_bp_cc_mf_information():
    integrate_information_into_dict('BiologicalProcess', dict_bp_to_name, dict_alt_bp_to_id)
    integrate_information_into_dict('CellularComponent', dict_cc_to_name, dict_alt_cc_to_id)
    integrate_information_into_dict('MolecularFunction', dict_mf_to_name, dict_alt_mf_to_id)


# dictionary from uniprot to gene id from hetionet information
dict_uniprot_to_gene_id = {}

# dictionary gene id to gene symbol/name
dict_gene_to_name = {}

# dictionary gene_id to synonyms
dict_gene_id_to_synonyms ={}

# dictionary gene id to gene name
dict_gene_id_to_gene_name = {}

# dictionary gene name to genes without uniprot list
dict_gene_symbol_to_gene_without_uniprot = {}
dict_gene_symbol_to_gene_id = {}

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
    query = '''MATCH (n:Gene) RETURN n.identifier,  n.geneSymbol, n.name, n.synonyms'''
    results = g.run(query)
    counter_uniprot_to_multiple_genes = 0
    counter_all_genes = 0
    list_double_names = set([])
    for gene_id, genesymbols, name, synonyms, in results:
        counter_all_genes += 1
        dict_gene_id_to_gene_name[gene_id] = name.lower() if name is not None else ''

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
            dict_gene_id_to_synonyms[gene_id]=set()
            for synonym in synonyms:
                synonym=synonym.lower()
                dict_gene_id_to_synonyms[gene_id].add(synonym)
                dict_synonyms_to_gene_ids[synonym.lower()].append(gene_id)

    print('number of genes:' + str(counter_all_genes))
    print('number of multiple name:' + str(len(list_double_names)))


# files with rela from uniprot protei to gene
file_uniprots_gene_rela = open('uniprot_gene/db_uniprot_to_gene_rela.csv', 'w')
writer_rela = csv.writer(file_uniprots_gene_rela)
writer_rela.writerow(['uniprot_id', 'gene_id', 'alternative_ids', 'name_mapping', 'uniprot', 'resource'])

# list of all uniprot ids which where wrong mapped and already found in the program to avoid duplication in the file
list_already_included = []

# list of all already integrated pairs of gene uniprot id
list_already_integrated_pairs_gene_protein = []

# counter for not matching gene names
count_not_mapping_gene_name = 0


'''
this goes throu a list of mapping gens and check out if they really do not exists already
if not integrate them into the csv
'''


def check_and_add_rela_pair(identifier, uniprot_id, gene_ids, secondary_uniprot_ids, name_mapping,
                            uniprot_mapping, map_resource):
    for gene_id in gene_ids:
        if not (identifier, gene_id) in list_already_integrated_pairs_gene_protein:
            writer_rela.writerow(
                [identifier, gene_id, secondary_uniprot_ids, name_mapping, uniprot_mapping, map_resource])
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


def check_and_write_uniprot_ids(uniprot_id, name, identifier, secondary_uniprot_ids, gene_names, gene_ids, primary_gene_symbol):
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
            check_and_add_rela_pair(identifier, uniprot_id, gene_ids, secondary_uniprot_ids,
                                    '', 'yes', 'UniProt')
            return True, gene_ids
            # if name.lower() in dict_gene_name_to_id:
            #     list_gene_id_from_name = [str(x) for x in dict_gene_name_to_id[name.lower()]]
            #     intersection = set(gene_ids).intersection(list_gene_id_from_name)
            #     if len(intersection) > 0:
            #         check_and_add_rela_pair(identifier, uniprot_id, intersection, secondary_uniprot_ids,
            #                                 'yes', 'yes', 'UniProt')
            #         genes = list(intersection)
            #         return True, genes
            # else:
            #     print('only gene id mapping')
        elif primary_gene_symbol:
            primary_gene_symbol=primary_gene_symbol.lower()
            gene_ids_from_symbol = []
            if primary_gene_symbol in dict_gene_symbol_to_gene_id:
                gene_ids_from_name = dict_gene_symbol_to_gene_id[primary_gene_symbol]
                gene_ids_from_symbol.extend(gene_ids_from_name)
                # print('ok gene symbol works primary')
                text='direct'
            elif primary_gene_symbol in dict_synonyms_to_gene_ids:
                gene_ids_from_symbol.extend(dict_synonyms_to_gene_ids[primary_gene_symbol])
                # print('only name and id is not existing primary')
                text='synonyms'
            if len(gene_ids_from_symbol)>0:
                check_and_add_rela_pair(identifier, uniprot_id, gene_ids_from_symbol,
                                        secondary_uniprot_ids,
                                        'yes', '', 'PrimaryGeneSymbol '+text)
                return True, genes
        elif gene_names:
            gene_ids_from_symbol=[]
            for gene_name in gene_names:
                if gene_name in dict_gene_symbol_to_gene_id:
                    gene_ids_from_name = dict_gene_symbol_to_gene_id[gene_name]
                    gene_ids_from_symbol.extend(gene_ids_from_name)
                    print('ok gene symbol works', uniprot_id, gene_ids, gene_names)
                    text='direct'
                elif gene_name in dict_synonyms_to_gene_ids:
                    gene_ids_from_symbol.extend(dict_synonyms_to_gene_ids[gene_name])
                    print('only name and id is not existing', uniprot_id, gene_ids, gene_names)
                    text='synonyms'
            if len(gene_ids_from_symbol)>0:
                check_and_add_rela_pair(identifier, uniprot_id, gene_ids_from_symbol,
                                        secondary_uniprot_ids,
                                        'yes', '', 'GeneSymbol '+text)
                return True, genes




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
                                    secondary_uniprot_ids, 'yes', '', 'GeneSymbolMapping')

            # print(identifier)
            # print(list_of_possible_mapped_gene_ids)
            found_at_least_on = True
            # no mapping from the gene or protein and no gene symbol
        # the last possible mapping try is with  name mapping
        else:
            if name.lower() in dict_gene_name_to_id:
                check_and_add_rela_pair(identifier, uniprot_id, dict_gene_name_to_id[name.lower()],
                                        secondary_uniprot_ids,
                                        'yes', '', 'NameMapping')

                genes = dict_gene_name_to_id[name.lower()]
                return True, genes

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

    query_property = '''MATCH (p:Protein_Uniprot) WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''

    results = g.run(query_property)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/db_uniprot_ids.csv" As line MATCH (p:Protein_Uniprot{identifier:line.uniprot_id}) Create (p)<-[:equal_to_uniprot]-(:Protein{'''

    for property, in results:
        # the go classifiers are in the rela to bc, cc and mf and the gene information are in the rela to gene
        if property in ['go_classifiers', 'gene_name', 'gene_id']:
            continue
        # to have the prepared xrefs
        elif property == 'xrefs':
            query += property + ':split(line.' + property + ',"|"), '
        if property == 'accession':
            query += 'alternative_ids:p.' + property + ', '
        else:
            query += property + ':p.' + property + ', '
    query += 'uniprot:"yes", url:"https://www.uniprot.org/uniprot/"+p.identifier, source:"UniProt", resource:["UniProt"], license:"CC BY 4.0"});\n '
    file_cypher.write(query)
    query = 'Create Constraint On (node:Protein) Assert node.identifier Is Unique;\n'
    file_cypher.write(query)

    # query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_gene/db_gene_uniprot_delete.csv" As line Match (g:Gene{identifier:line.gene_id}) With g,[x IN g.uniProtIDs WHERE x <> line.uniprot_id]  as filterdList
    #              Set g.uniProtIDs=filterdList;\n '''
    # file_cypher.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_gene/db_uniprot_to_gene_rela.csv" As line MATCH (n:Protein{identifier:line.uniprot_id}), (g:Gene{identifier:line.gene_id}) Create (g)-[:PRODUCES_GpP{name_mapping:line.name_mapping, uniprot:line.uniprot,resource:split(line.resource,'|'),license:'CC BY 4.0', url:'https://www.uniprot.org/uniprot/'+line.uniprot_id}]->(n);\n'''
    file_cypher.write(query)

    # the queries to integrate rela to bc, cc and mf
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_go/db_uniprots_to_bc.csv" As line MATCH (g:Protein{identifier:line.uniprot_ids}),(b:BiologicalProcess{identifier:line.go}) Create (g)-[:PARTICIPATES_PpBP{resource:['UniProt'],source:'UniProt', uniprot:'yes', license:'CC BY 4.0', url:'https://www.uniprot.org/uniprot/'+line.uniprot_ids}]->(b);\n'''
    file_cypher.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_go/db_uniprots_to_cc.csv" As line MATCH (g:Protein{identifier:line.uniprot_ids}),(b:CellularComponent{identifier:line.go}) Create (g)-[:PARTICIPATES_PpCC{resource:['UniProt'],source:'UniProt', uniprot:'yes', license:'CC BY 4.0', url:'https://www.uniprot.org/uniprot/'+line.uniprot_ids}]->(b);\n'''
    file_cypher.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_go/db_uniprots_to_mf.csv" As line MATCH (g:Protein{identifier:line.uniprot_ids}),(b:MolecularFunction{identifier:line.go}) Create (g)-[:PARTICIPATES_PpMF{resource:['UniProt'],source:'UniProt', uniprot:'yes', license:'CC BY 4.0', url:'https://www.uniprot.org/uniprot/'+line.uniprot_ids}]->(b);\n'''
    file_cypher.write(query)


'''
Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
'''


def get_gather_protein_info_and_generate_relas():
    # file with every uniprot identifier
    file_uniprots_ids = open('db_uniprot_ids.csv', 'w')
    writer_uniprots_ids = csv.writer(file_uniprots_ids)
    writer_uniprots_ids.writerow(['uniprot_id', 'xrefs'])

    # generate a file with all uniprots which mapped to multiple genes
    file_uniprots_genes = open('uniprot_gene/db_uniprots_to_genes_multi_map.csv', 'w')
    writer_uniprots_genes_multi_mapps = csv.writer(file_uniprots_genes)
    writer_uniprots_genes_multi_mapps.writerow(['uniprot_ids', 'gene_id'])

    # generate a file with all uniprots to bc
    file_uniprots_bc = open('uniprot_go/db_uniprots_to_bc.csv', 'w')
    writer_uniprots_bc = csv.writer(file_uniprots_bc)
    writer_uniprots_bc.writerow(['uniprot_ids', 'go'])

    # generate a file with all uniprots to cc
    file_uniprots_cc = open('uniprot_go/db_uniprots_to_cc.csv', 'w')
    writer_uniprots_cc = csv.writer(file_uniprots_cc)
    writer_uniprots_cc.writerow(['uniprot_ids', 'go'])

    # generate a file with all uniprots to mf
    file_uniprots_mf = open('uniprot_go/db_uniprots_to_mf.csv', 'w')
    writer_uniprots_mf = csv.writer(file_uniprots_mf)
    writer_uniprots_mf.writerow(['uniprot_ids', 'go'])

    # query to get all Protein information {identifier:'P0DMV0'} {identifier:'Q05066'} {identifier:'P0DPK4'} {identifier:'E5RIL1'} {identifier:'P01009'}
    query = '''MATCH (n:Protein_Uniprot) RETURN n '''
    results = g.run(query)

    print(datetime.datetime.utcnow())
    # counter of combined gene protein interaction
    counter_existing_gene_protein_rela = 0
    # counter all proteins
    counter_all_proteins = 0

    # counter protein to gos
    counter_gos_bc = 0
    counter_gos_cc = 0
    counter_gos_mf = 0

    # go through all Proteins
    # find overlap between protein and genes
    # maybe check out the go information to generate further relationships to go
    for node, in results:
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
        if identifier == 'P0DI82':
            print('ok')

        # get the name of the node
        name = node['name']
        # get all xrefs of the node
        xrefs = node['xrefs'] if 'xrefs' in node else []

        # the gene symbol
        geneSymbols = node['gene_name'] if 'gene_name' in node else []
        primary_gene_symbol=''
        set_gene_symbol=set()
        for geneSymbol in geneSymbols:
            splitted_genesymbol=geneSymbol.split(':')
            set_gene_symbol.add(splitted_genesymbol[1])
            if splitted_genesymbol[0]=='primary':
                primary_gene_symbol=splitted_genesymbol[1]

        # the gene ids
        gene_ids = [x.replace('GeneID:', '') for x in node['gene_id']] if 'gene_id' in node else []

        # first check out the identifier
        # also check if it has multiple genes or not
        # print(identifier)
        in_list, genes = check_and_write_uniprot_ids(identifier, name, identifier, '', set_gene_symbol, gene_ids, primary_gene_symbol)
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

        # to find also relationships to biological processes, cellular component and moleculare functions
        if 'go_classifiers' in node:
            for go_id in node['go_classifiers']:
                source_id = go_id.split(':', 1)
                if source_id[0] == 'GO':
                    if source_id[1] in dict_bp_to_name:
                        counter_gos_bc += 1
                        writer_uniprots_bc.writerow([identifier, source_id[1]])
                    elif source_id[1] in dict_cc_to_name:
                        counter_gos_cc += 1
                        writer_uniprots_cc.writerow([identifier, source_id[1]])
                    elif source_id[1] in dict_mf_to_name:
                        counter_gos_mf += 1
                        writer_uniprots_mf.writerow([identifier, source_id[1]])
                    elif source_id[1] in dict_alt_bp_to_id:
                        counter_gos_bc += 1
                        writer_uniprots_bc.writerow([identifier, dict_alt_bp_to_id[source_id[1]]])
                    elif source_id[1] in dict_alt_cc_to_id:
                        counter_gos_cc += 1
                        writer_uniprots_bc.writerow([identifier, dict_alt_cc_to_id[source_id[1]]])
                    elif source_id[1] in dict_alt_mf_to_id:
                        counter_gos_mf += 1
                        writer_uniprots_bc.writerow([identifier, dict_alt_mf_to_id[source_id[1]]])

                    else:
                        print('GO not found:' + source_id[1])
        new_xrefs = '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'Protein'))
        writer_uniprots_ids.writerow([identifier, new_xrefs])

    print('number of existing gene protein rela:' + str(counter_existing_gene_protein_rela))
    print('number of all proteins:' + str(counter_all_proteins))
    print('rela to one of the bcs:' + str(counter_gos_bc))
    print('rela to one of the ccs:' + str(counter_gos_cc))
    print('rela to one of the mfs:' + str(counter_gos_mf))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        print(sys.argv)
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the hetionet genes')

    get_all_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the hetionet Bp,CC and MF')

    load_bp_cc_mf_information()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('write cypher queries into cypher file')

    write_cypher_file()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the proteins')

    get_gather_protein_info_and_generate_relas()

    print('number of not matching gene names between protein and gene:' + str(count_not_mapping_gene_name))

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
