'''
construct list of pathway form d. himmelstein, but for python 2.7
https://github.com/dhimmel/pathways
https://github.com/dhimmel/pathways/blob/master/merge-resources.ipynb
'''

import csv
import collections
import re, datetime
import html
import gzip

import pandas, sys

sys.path.append("../..")
import pharmebinetutils

'''
Get Gene informaation from Entrez-gene from latest version which is already integrated into Neo4j
'''


def use_of_entrez_gene():
    global human_coding_genes, human_genes, symbol_to_entrez

    human_genes = set()
    human_coding_genes = set()
    symbol_to_entrez = {}

    gene_file_name = '../ncbi_genes/output_data/genes.tsv'

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


# def read_gmt_v11(read_file):
#     reader = csv.reader(read_file, delimiter='\t')
#     for row in reader:
#         if not row:
#             continue
#         url = row[0]
#         description = row[1]
#         genes = set(row[2:])
#         yield url, description, genes
#     read_file.close()

'''
Pathway Commons V11 download and information extraction
'''


def pathway_commons():
    # download Pathway Commons v12
    url = 'https://www.pathwaycommons.org/archives/PC2/v12/PathwayCommons12.All.hgnc.gmt.gz'
    filename = pharmebinetutils.download_file(url, out='data/')
    filename_without_gz = filename.rsplit('.', 1)[0]
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
        # Add pathway
        i += 1
        row = PC_Row(
            identifier='PC13_{}'.format(i),
            synonyms=name,
            source=description['datasource'],
            genes=genes,
            url=url,
            xrefs=description['datasource'] + ':' + url.rsplit('/', 1)[1]
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

    # filter only the open source sources
    keep = {'wikipathways', 'reactome', 'panther', 'netpath', 'pathbank'}
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
        'pathbank': 'PathBank is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (PathBank) and the original publication. '
    }

    # add license to the different sources
    pc_df['license'] = pc_df['source'].map(source_to_license)


'''
Download wikiPathways and extract the information from the gmt file
'''


def wikipathways():
    # Parse WikiPathways

    # download WikiPathways
    url = 'http://data.wikipathways.org/20230410/gmt/wikipathways-20230410-gmt-Homo_sapiens.gmt'
    filename = pharmebinetutils.download_file(url, out='data/')

    gmt_generator = read_gmt(filename)

    global wikipath_df
    wikipath_df = pandas.DataFrame(gmt_generator, columns=['name', 'description', 'genes'])
    wikipath_df.name = wikipath_df.name.map(lambda x: x.split('%')[0])
    if len(wikipath_df) == 0:
        print('wikipathway ulr is not working anymore')
        sys.exit('wikipathway ulr is not working anymore')
    print(i)
    wikipath_df['identifier'] = ['PC13_{}'.format(j) for j in range(i + 1, i + 1 + len(wikipath_df))]
    print(len(wikipath_df))
    # print(j)

    # Remove genes absent from our entrez gene version
    for genes in wikipath_df.genes:
        genes &= human_genes
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
