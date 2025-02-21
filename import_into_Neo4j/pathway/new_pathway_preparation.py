'''
construct list of pathway form d. himmelstein, but for python 2.7
https://github.com/dhimmel/pathways
https://github.com/dhimmel/pathways/blob/master/merge-resources.ipynb
'''

import csv
import collections
import re, datetime
import html
import gzip, os

import pandas, sys

sys.path.append("../..")
import pharmebinetutils

'''
Get Gene information from Entrez-gene from latest version which is already integrated into Neo4j
'''

csv.field_size_limit(337261)

def use_of_entrez_gene():
    global human_coding_genes, human_genes, symbol_to_entrez, entrez_to_symbol

    human_genes = set()
    human_coding_genes = set()
    symbol_to_entrez = {}
    entrez_to_symbol = {}

    gene_file_name = '../ncbi_genes/output/genes.tsv'

    with open(gene_file_name, 'r', encoding='utf-8') as gene_file:
        csv_reader = csv.DictReader(gene_file, delimiter='\t')
        for line in csv_reader:
            identifier = line['GeneID']
            symbol = line['Symbol']
            type_of_gene = line['type_of_gene']
            human_genes.add(identifier)
            if type_of_gene == 'protein-coding':
                human_coding_genes.add(identifier)
            symbol_to_entrez[symbol] = identifier
            entrez_to_symbol[identifier] = symbol


# gmt function
def read_gmt(path):
    read_file = open(path, 'r', encoding='utf-8')
    reader = csv.reader(read_file, delimiter='\t')
    for row in reader:
        if not row or len(row) < 3:
            continue
        name = row[0]
        description = row[1]
        genes = set(row[2:])
        yield name, description, genes
    read_file.close()

def prepare_files():
    global set_of_gene_ids, csv_gene_writer, csv_pathway_gene_writer, cypher_edge_file, csv_participants_writer, set_of_participants_ids
    file= open('output/gene.tsv', 'w', encoding='utf-8')
    csv_gene_writer=csv.writer(file, delimiter='\t')
    csv_gene_writer.writerow(['entrez_id', 'id'])
    set_of_gene_ids=set()


    file_p= open('output/participants.tsv', 'w', encoding='utf-8')
    csv_participants_writer=csv.writer(file_p, delimiter='\t')
    csv_participants_writer.writerow(['id'])
    set_of_participants_ids=set()


    file_p_g= open('output/pathway_gene.tsv', 'w', encoding='utf-8')
    csv_pathway_gene_writer=csv.writer(file_p_g, delimiter='\t')
    csv_pathway_gene_writer.writerow(['pathway_id','gene_id','source'])

    cypher_edge_file=open('output/cypher_edge.cypher','w')
    query='Match (n:pathway_multi{identifier:line.pathway_id}), (m:gene_multi{entrez_id:line.gene_id}) Create (n)-[:associates{source:line.source}]->(m)'
    query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/pathway/output/pathway_gene.tsv', query)
    cypher_edge_file.write(query)


'''
Pathway Commons V12 download and information extraction
'''


def pathway_commons():
    # download Pathway Commons v12
    # url = 'https://www.pathwaycommons.org/archives/PC2/v12/PathwayCommons12.All.hgnc.gmt.gz'
    filename_without_gz='data/pc-hgnc.gmt'
    if not os.path.exists(filename_without_gz+'.gz'):
        url = 'https://download.baderlab.org/PathwayCommons/PC2/v14/pc-hgnc.gmt.gz'
        filename = pharmebinetutils.download_file(url, out='data/')
        filename_without_gz = filename.rsplit('.', 1)[0]
        print(filename_without_gz)

        file = open(filename_without_gz, 'wb')
        with gzip.open(filename, 'rb') as f:
            file.write(f.read())
        file.close()

    global i
    i = 0
    rows = list()
    PC_Row = collections.namedtuple('PC_Row', ['identifier', 'synonyms', 'source', 'genes', 'url', 'xrefs'])

    for url, description, genes in read_gmt(filename_without_gz):

        # Process description and only for human
        # print(url)
        # print(genes)
        # print(description)
        try:
            description = dict(item.split(': ', 1) for item in description.split('; '))
        except:
            key_before = ''
            description_saver = {}
            for item in description.split('; '):
                splitted_information = item.split(': ', 1)
                if len(splitted_information) > 1:
                    key_before = splitted_information[0]
                    description_saver[key_before] = splitted_information[1]
                else:
                    description_saver[key_before] = description_saver[key_before] + ': ' + splitted_information[0]
            description = description_saver

        if description['organism'] != '9606':
            continue

        # Process name
        name = description['name']
        name = re.sub(r'^9606: +', '', name)
        # name = HTMLParser.unescape(name)
        name = html.unescape(name)
        if name == 'Not pathway':
            continue

        # Convert genes to Entrez
        genes = {symbol_to_entrez.get(x) for x in genes}
        genes.discard(None)
        if not genes:
            continue
        for gene in genes:
            if gene not in set_of_gene_ids:
                csv_gene_writer.writerow([gene,entrez_to_symbol[gene] ])
                set_of_gene_ids.add(gene)
            csv_pathway_gene_writer.writerow(['PC14_{}'.format(i), gene])
        # Add pathway
        i += 1
        # PC12
        # row = PC_Row(
        #     identifier='PC12_{}'.format(i),
        #     synonyms=name,
        #     source=description['datasource'],
        #     genes=genes,
        #     url=url,
        #     xrefs=description['datasource'] + ':' + url.rsplit('/', 1)[1]
        # )
        row = PC_Row(
            identifier='PC14_{}'.format(i),
            synonyms=name,
            source=description['datasource'],
            genes=genes,
            url=url,
            xrefs=description['datasource'] + ':' + url.rsplit(':', 1)[1]
        )
        rows.append(row)

    global pc_df
    pc_df = pandas.DataFrame(rows)
    print(pc_df.head(2))
    print(pc_df['source'].unique())
    print(pc_df.source.value_counts())
    print(pc_df.synonyms.value_counts())

    # wikipathways: CC BY 3.0
    # reactome: CC BY 4.0
    # kegg: not open source
    # panther:GNU GPLv3
    # pid:not existing anymore?
    # netpath:CC BY 2.5
    # inoh:unknown
    # humancyc: not open source
    # biofactoid: CC0 1.0 Legal Code
    # pathbank: PathBank is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (PathBank) and the original publication.


    # filter only the open source sources
    # 'netpath', is currently not available
    keep = {'wikipathways', 'reactome', 'panther',  'pathbank','biofactoid'}
    pc_df = pc_df.query("source in @keep")

    # dictionary source to license
    source_to_license = {
        'wikipathways': 'CC BY 3.0',
        'reactome': 'CC BY 4.0',
        'kegg': 'not open source',
        'panther': 'GNU GPLv3',
        'pid': 'not existing anymore?',
        'netpath': 'CC BY 2.5',
        'inoh': 'unknown',
        'humancyc': 'acedemic',
        'biofactoid':'CC0 1.0 Universal',
        'pathbank': 'PathBank is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (PathBank) and the original publication. '
    }

    # add license to the different sources
    pc_df['license'] = pc_df['source'].map(source_to_license)

    file_name='data/pc-hgnc.txt.gz'
    if not os.path.exists(file_name):
        url = 'https://download.baderlab.org/PathwayCommons/PC2/v14/pc-hgnc.txt.gz'
        pharmebinetutils.download_file(url, out='data/')

    # association_df = pandas.read_csv(file_name, compression='gzip', header=0, delimiter='\t')
    # print(association_df)
    # print(association_df['INTERACTION_DATA_SOURCE'].drop_duplicates().sort_values())
    # print(association_df['INTERACTION_TYPE'].drop_duplicates().sort_values())
    dict_edge_type_to_csv_file={}
    with gzip.open(file_name, 'rt') as f:
        csv_reader=csv.reader(f,delimiter='\t')
        header=next(csv_reader)
        print(header)
        header.remove('INTERACTION_TYPE')
        for row in csv_reader:
            if len(row)==0:
                print('empty',row)
                continue
            # print(row)
            interactor_1= row[0]
            if not interactor_1 in set_of_participants_ids:
                set_of_participants_ids.add(interactor_1)
                csv_participants_writer.writerow([interactor_1])
            edge_types=row[1]
            interactor_2= row[2]

            del row[1]

            if not interactor_2 in set_of_participants_ids:
                set_of_participants_ids.add(interactor_2)
                csv_participants_writer.writerow([interactor_2])
            for edge_type in edge_types.split(';'):
                if not edge_type in dict_edge_type_to_csv_file:
                    print(edge_type)
                    file_name_edge=f'output/{edge_type}.tsv'
                    new_file=open(file_name_edge,'w',encoding='utf-8')
                    csv_writer=csv.writer(new_file,delimiter='\t')
                    csv_writer.writerow(header)
                    query = f'Match (n:participants_multi{{identifier:line.PARTICIPANT_A}}), (m:participants_multi{{identifier:line.PARTICIPANT_B}}) Create (n)-[:{edge_type.replace("-","_")}{{sources:split(line.INTERACTION_DATA_SOURCE,";"), pmids:split(line.INTERACTION_PUBMED_ID,";"), pathway_names:split(line.PATHWAY_NAMES,";"), mediator_ids:split(line.MEDIATOR_IDS,";")}}]->(m)'
                    query = pharmebinetutils.get_query_import(path_of_directory,
                                                              f'import_into_Neo4j/pathway/{file_name_edge}', query)
                    cypher_edge_file.write(query)
                    dict_edge_type_to_csv_file[edge_type]=csv_writer
                dict_edge_type_to_csv_file[edge_type].writerow(row)




'''
Download wikiPathways and extract the information from the gmt file
'''


def wikipathways():
    # Parse WikiPathways

    # download WikiPathways
    url = 'https://zenodo.org/records/14649898/files/wikipathways-20250110-gmt-Homo_sapiens.gmt?download=1'
    #url = 'https://data.wikipathways.org/20240410/gmt/wikipathways-20240410-gmt-Homo_sapiens.gmt'
    filename = pharmebinetutils.download_file(url, out='data/')

    gmt_generator = read_gmt(filename)

    global wikipath_df
    wikipath_df = pandas.DataFrame(gmt_generator, columns=['name', 'description', 'genes'])
    wikipath_df.name = wikipath_df.name.map(lambda x: x.split('%')[0])
    if len(wikipath_df) == 0:
        print('wikipathway ulr is not working anymore')
        sys.exit('wikipathway ulr is not working anymore')
    print(i)
    wikipath_df['identifier'] = ['PC14_{}'.format(j) for j in range(i + 1, i + 1 + len(wikipath_df))]
    print(len(wikipath_df))
    # print(j)

    # Remove genes absent from our entrez gene version
    for genes in wikipath_df.genes:
        genes &= human_genes
    print(genes)
    wikipath_df = wikipath_df[wikipath_df.genes.map(bool)]
    print(len(wikipath_df))

    print(wikipath_df.head(2))

    wikipath_df = pandas.DataFrame({
        'identifier': wikipath_df['identifier'],
        'xrefs': wikipath_df['description'].map(lambda x: 'wikipathways' + ':' + x.rsplit('/', 1)[1]),
        'synonyms': wikipath_df['name'],
        'url': wikipath_df['description'],
        'source': 'wikipathways',
        'license': 'CC BY 3.0',
        'genes': wikipath_df.genes
    })
    print(wikipath_df.head(2))


properties_which_are_list = ['genes', 'coding_genes', 'synonyms', 'xrefs']

'''
Combine the both data from the different source to one big one and generate a cypher file
'''


def combine_both_source():
    # Merge resources into a pathway dataframe
    pathway_df = pandas.concat([wikipath_df, pc_df], sort=True)
    pathway_df = pathway_df[['identifier', 'synonyms', 'url', 'source', 'license', 'genes', 'xrefs']]
    print(len(pathway_df))

    # Remove duplicate pathways
    pathway_df.genes = pathway_df.genes.map(frozenset)
    print(pathway_df['synonyms'])
    pathway_df_without_duplicated = pathway_df.drop_duplicates(['genes']).copy()
    print(len(pathway_df))

    pathway_df_without_duplicated['coding_genes'] = pathway_df_without_duplicated.genes.map(
        lambda x: x & human_coding_genes)

    pathway_df_without_duplicated.insert(3, 'n_genes', pathway_df_without_duplicated.genes.map(len))
    pathway_df_without_duplicated.insert(4, 'n_coding_genes', pathway_df_without_duplicated.coding_genes.map(len))

    pathway_df_without_duplicated = pathway_df_without_duplicated.sort_values('identifier')
    print(pathway_df_without_duplicated.head())

    print(pathway_df_without_duplicated.source.value_counts())

    # Create a dataframe for writing as a tsv. Multi-element fields are pipe delimited.
    write_df = pathway_df_without_duplicated.copy()
    join = lambda x: '|'.join(map(str, sorted(x)))
    for column in 'genes', 'coding_genes':
        write_df[column] = write_df[column].map(join)

    write_df.to_csv('output/pathways.tsv', index=False, sep='\t', encoding='utf-8')

    # generate cypher file
    query = ''' Create (c1:pathway_multi{'''
    for property in pathway_df_without_duplicated:
        if property not in properties_which_are_list:
            query += property + ':line.' + property + ', '
        else:
            query += property + ':split(line.' + property + ',"|"), '

    query = query[:-2] + '''}) '''
    query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/pathway/output/pathways.tsv', query)
    with open('output/cypher.cypher', 'w') as file:
        file.write(query)
        file.write(pharmebinetutils.prepare_index_query('pathway_multi', 'identifier'))

        # generate cypher file
        query = ' Create (c1:participants_multi{identifier:line.id})'
        query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/pathway/output/participants.tsv',
                                                  query)
        file.write(query)
        file.write(pharmebinetutils.prepare_index_query('participants_multi', 'identifier'))


        # generate cypher file
        query = ' Match (c1:participants_multi{identifier:line.id}) Set c1:gene_multi , c1.entrez_id=line.entrez_id'
        query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/pathway/output/gene.tsv',
                                                  query)
        file.write(query)
        query = ' Merge (c1:gene_multi{identifier:line.id}) On Create Set c1.only_one="yes", c1.entrez_id=line.entrez_id '
        query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/pathway/output/gene.tsv',
                                                  query)
        file.write(query)
        file.write(pharmebinetutils.prepare_index_query('gene_multi', 'entrez_id'))



# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('prepare_files')

    prepare_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load gene information')

    use_of_entrez_gene()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load pathway commons information')

    pathway_commons()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load pathway wikiPathways')

    wikipathways()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('combine both sources and generate tsv')

    combine_both_source()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
