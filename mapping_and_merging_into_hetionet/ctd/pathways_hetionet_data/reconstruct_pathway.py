'''
construct list of pathway form d. himmelstein, but for python 2.7
https://github.com/dhimmel/pathways
'''


import csv
import collections
import re
# import html.parser
import HTMLParser
import json


import requests
import pandas


# read entrez genes
url = 'https://raw.githubusercontent.com/dhimmel/entrez-gene/a7362748a34211e5df6f2d185bb3246279760546/data/genes-human.tsv'
entrez_df = pandas.read_table(url, dtype={'GeneID': str})
human_genes = set(entrez_df.GeneID)
human_coding_genes = set(entrez_df[entrez_df.type_of_gene == 'protein-coding'].GeneID)



url = 'https://raw.githubusercontent.com/dhimmel/entrez-gene/a7362748a34211e5df6f2d185bb3246279760546/data/symbol-map.json'
symbol_to_entrez = json.loads(requests.get(url).text)
symbol_to_entrez = {k: str(v) for k, v in symbol_to_entrez.items()}

def read_gmt(path):
    read_file = open(path)
    reader = csv.reader(read_file, delimiter='\t')
    for row in reader:
        if not row:
            continue
        name = row[0]
        description = row[1]
        genes = set(row[2:])
        yield name, description, genes
    read_file.close()

def read_gmt_v9(path):
    read_file = open(path)
    reader = csv.reader(read_file, delimiter='\t')
    for row in reader:
        if not row:
            continue
        url = row[0]
        description = row[1]
        genes = set(row[2:])
        yield url, description, genes
    read_file.close()



i = 0
rows = list()
PC_Row = collections.namedtuple('PC_Row', ['identifier', 'name', 'source', 'genes','url','idOwn' ])
# path = "pathways_hetionet_data/Pathway Commons.7.All.GSEA.hgnc.gmt"
path = "PathwayCommons9.All.hgnc_change.gmt"
# version for pc7
# for name, description, genes in read_gmt(path):
#
#     # Process name
#     name = re.sub(r'^9606: +', '', name)
#     name = HTMLParser.HTMLParser().unescape(name)
#     if name == 'Not pathway':
#         continue
#
#     # Process description
#     description = dict(item.split(': ') for item in description.split('; '))
#     if description['organism'] != '9606':
#         continue
#
#     # Convert genes to Entrez
#     genes = {symbol_to_entrez.get(x) for x in genes}
#     genes.discard(None)
#     if not genes:
#         continue
#
#     # Add pathway
#     i += 1
#     row = PC_Row(
#         # identifier='PC7_{}'.format(i),
#         identifier='PC9_{}'.format(i),
#         name=name,
#         source=description['datasource'],
#         genes=genes,
#     )
#     rows.append(row)

for url, description, genes in read_gmt(path):

    # Process description
    description = dict(item.split(': ',1) for item in description.split('; '))
    if description['organism'] != '9606':
        continue

    # Process name
    name= description['name']
    name = re.sub(r'^9606: +', '', name)
    name = HTMLParser.HTMLParser().unescape(name)
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
        identifier='PC9_{}'.format(i),
        name=name,
        source=description['datasource'],
        genes=genes,
        url=url,
        idOwn=url.rsplit('/',1)[1]
    )
    rows.append(row)

pc_df = pandas.DataFrame(rows)
print(pc_df.head(2))

print(pc_df.source.value_counts())

gmt_generator = read_gmt('wikipathways.gmt')
wikipath_df = pandas.DataFrame(gmt_generator, columns = ['name', 'description', 'genes'])
wikipath_df.name = wikipath_df.name.map(lambda x: x.split('%')[0])
print(len(wikipath_df))

print(wikipath_df.head(2))



wikipath_df = pandas.DataFrame({
    'identifier': wikipath_df['description'].map(lambda x: x.rsplit('/', 1)[1]),
    'name': wikipath_df['name'],
    'url': wikipath_df['description'],
    'source': 'wikipathways',
    'license': 'CC BY 3.0',
    'genes': wikipath_df.genes
})
print(wikipath_df.head(2))

pathway_df = pandas.concat([wikipath_df, pc_df])
print(pathway_df)
pathway_df = pathway_df[['identifier', 'name', 'url', 'source', 'license', 'genes','idOwn']]
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

write_df.to_csv('pathways_v9.tsv', index=False, sep='\t',encoding='utf-8')