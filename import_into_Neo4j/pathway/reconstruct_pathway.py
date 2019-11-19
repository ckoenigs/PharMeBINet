'''
construct list of pathway form d. himmelstein, but for python 2.7
https://github.com/dhimmel/pathways
https://github.com/dhimmel/pathways/blob/master/merge-resources.ipynb
'''


import csv
import collections
import re, datetime
import html
from html.parser import HTMLParser
# import HTMLParser
import json
import wget
import gzip


import requests
import pandas, sys

'''
Get Gene informaation from Entrez-gene
'''
def use_of_entrez_gene():
    # read entrez genes
    url = 'https://raw.githubusercontent.com/dhimmel/entrez-gene/a7362748a34211e5df6f2d185bb3246279760546/data/genes-human.tsv'
    entrez_df = pandas.read_csv(url,sep='\t', dtype={'GeneID': str})
    global human_coding_genes, human_genes
    human_genes = set(entrez_df.GeneID)
    human_coding_genes = set(entrez_df[entrez_df.type_of_gene == 'protein-coding'].GeneID)



    url = 'https://raw.githubusercontent.com/dhimmel/entrez-gene/a7362748a34211e5df6f2d185bb3246279760546/data/symbol-map.json'
    global symbol_to_entrez
    symbol_to_entrez = json.loads(requests.get(url).text)

    symbol_to_entrez = {k: str(v) for k, v in symbol_to_entrez.items()}

#gmt function
def read_gmt(path):
    read_file = open(path)
    reader = csv.reader(read_file, delimiter='\t')
    for row in reader:
        if not row or len(row)<3:
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

    # download Pathway Commons v11
    url = 'https://www.pathwaycommons.org/archives/PC2/v11/PathwayCommons11.All.hgnc.gmt.gz'
    filename = wget.download(url, out='data/')
    filename_without_gz =filename.rsplit('.',1)[0]
    file=open(filename_without_gz,'wb')
    with gzip.open(filename,'rb') as f:
        file.write(f.read())
    file.close()

    global i
    i = 0
    rows = list()
    PC_Row = collections.namedtuple('PC_Row', ['identifier', 'names', 'source', 'genes','url','idOwns' ])


    for url, description, genes in read_gmt(filename_without_gz):

        # Process description and only for human
        print(description)
        try:
            description = dict(item.split(': ',1) for item in description.split('; '))
        except:
            key_before=''
            description_saver={}
            for item in description.split('; '):
                splitted_information=item.split(': ',1)
                if len(splitted_information)>1:
                    key_before=splitted_information[0]
                    description_saver[key_before]=splitted_information[1]
                else:
                    description_saver[key_before]=description_saver[key_before]+': '+splitted_information[0]
            description=description_saver

        if description['organism'] != '9606':
            continue

        # Process name
        name= description['name']
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
            # identifier='PC7_{}'.format(i),
            identifier='PC11_{}'.format(i),
            names=name,
            source=description['datasource'],
            genes=genes,
            url=url,
            idOwns=url.rsplit('/',1)[1]
        )
        rows.append(row)


    global pc_df
    pc_df = pandas.DataFrame(rows)
    print(pc_df.head(2))

    print(pc_df.source.value_counts())

    # wikipathways: CC BY 3.0
    # reactome: CC BY 4.0
    # kegg: not open source
    # panther:GNU GPLv3
    # pid:not existing anymore?
    # netpath:CC BY 2.5
    # inoh:unknown
    # humancyc: not open source

    # filter only the open source sources
    keep = {'wikipathways', 'reactome', 'panther', 'netpath'}
    pc_df=pc_df.query("source in @keep")

    #dictionary source to license
    source_to_license={
        'wikipathways': 'CC BY 3.0',
        'reactome': 'CC BY 4.0',
        'kegg': 'not open source',
        'panther': 'GNU GPLv3',
        'pid': 'not existing anymore?',
        'netpath': 'CC BY 2.5',
        'inoh': 'unknown',
        'humancyc': 'not open source'
    }

    #add license to the different sources
    pc_df['license']=pc_df['source'].map(source_to_license)


'''
Download wikiPathways and extract the information from the gmt file
'''
def wikipathways():
    # Parse WikiPathways

    # download WikiPathways
    url = 'http://data.wikipathways.org/20191010/gmt/wikipathways-20191010-gmt-Homo_sapiens.gmt'
    filename= wget.download(url,out='data/')

    gmt_generator = read_gmt(filename)

    global wikipath_df
    wikipath_df = pandas.DataFrame(gmt_generator, columns = ['name', 'description', 'genes'])
    wikipath_df.name = wikipath_df.name.map(lambda x: x.split('%')[0])
    if len(wikipath_df)==0:
        print('wikipathway ulr is not working anymore')
        sys.exit('wikipathway ulr is not working anymore')
    print(i)
    wikipath_df['identifier']=['PC11_{}'.format(j) for j in range(i+1,i+1+len(wikipath_df))]
    print(len(wikipath_df))
    # print(j)

    # Remove genes absent from our entrez gene version
    for genes in wikipath_df.genes:
        genes &= human_genes
    wikipath_df = wikipath_df[wikipath_df.genes.map(bool)]
    print(len(wikipath_df))

    print(wikipath_df.head(2))



    wikipath_df = pandas.DataFrame({
        'identifier':wikipath_df['identifier'],
        'idOwns': wikipath_df['description'].map(lambda x: x.rsplit('/', 1)[1]),
        'names': wikipath_df['name'],
        'url': wikipath_df['description'],
        'source': 'wikipathways',
        'license': 'CC BY 3.0',
        'genes': wikipath_df.genes
    })
    print(wikipath_df.head(2))

properties_which_are_list=['genes','coding_genes','names','idOwns']

'''
Combine the both data from the different source to one big one and generate a cypher file
'''
def combine_both_source():
    # Merge resources into a pathway dataframe
    pathway_df = pandas.concat([wikipath_df, pc_df],sort=True)
    print(pathway_df)
    pathway_df = pathway_df[['identifier', 'names', 'url', 'source', 'license', 'genes','idOwns']]
    print(len(pathway_df))

    # Remove duplicate pathways
    pathway_df.genes = pathway_df.genes.map(frozenset)
    pathway_df = pathway_df.drop_duplicates(['genes'])
    print(len(pathway_df))

    pathway_df['coding_genes'] = pathway_df.genes.map(lambda x: x & human_coding_genes)

    pathway_df.insert(3, 'n_genes', pathway_df.genes.map(len))
    pathway_df.insert(4, 'n_coding_genes', pathway_df.coding_genes.map(len))

    pathway_df = pathway_df.sort_values('identifier')
    print(pathway_df.head())

    print(pathway_df.source.value_counts())

    # Create a dataframe for writing as a tsv. Multi-element fields are pipe delimited.
    write_df = pathway_df.copy()
    join = lambda x: '|'.join(map(str, sorted(x)))
    for column in 'genes', 'coding_genes':
        write_df[column] = write_df[column].map(join)

    write_df.to_csv('pathways.tsv', index=False, sep='\t',encoding='utf-8')


    #generate cypher file
    query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/import_into_Neo4j/pathway/pathways.tsv" As line fieldterminator '\\t' Create (c1:pathway_multi{'''
    for property in pathway_df:
        if property not in properties_which_are_list:
            query+= property+':line.'+property+', '
        else:
            query += property + ':split(line.' + property + ',"|"), '

    query= query[:-2]+'''});\n '''
    with open('cypher.cypher','w') as file:
        file.write(query)

 # path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('load gene information')


    use_of_entrez_gene()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load pathway commons information')

    pathway_commons()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('load pathway wikiPathways')

    wikipathways()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('combine both sources and generate tsv')

    combine_both_source()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()