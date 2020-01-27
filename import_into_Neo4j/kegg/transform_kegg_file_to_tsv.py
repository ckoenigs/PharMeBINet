
import datetime
import sys, csv, wget
import gzip, io, requests
import io
import os.path
from typing import List, Dict, Set

url_data_dgroup='ftp://ftp.genome.jp/pub/kegg/medicus/dgroup/dgroup'
url_data_disease='ftp://ftp.genome.jp/pub/kegg/medicus/disease/disease'
url_data_drug='ftp://ftp.genome.jp/pub/kegg/medicus/drug/drug'
url_data_network='ftp://ftp.genome.jp/pub/kegg/medicus/network/network'
url_data_variant='ftp://ftp.genome.jp/pub/kegg/medicus/network/variant'

# list of found genes
found_gene_ids=[]

'''
prepare external identifier in a format db:id
'''
def prepare_external_links(db_links):
    resolved_xrefs = set()
    for xref in db_links:
        db_key, ids = xref.split(':')
        resolved_xrefs.update(['%s:%s' % (db_key, _id) for _id in ids.split(' ') if len(_id) > 0])
    return sorted(resolved_xrefs)

'''
extract the information from flat file  into a dictionary
'''
def parse_kegg_file(file_path: str) -> List[Dict[str, List[str] or str]]:
    result = []
    with io.open(file_path, 'r', encoding='utf-8') as f:
        current_entry = {}
        last_keyword = None
        for line in f:
            line = line.rstrip()
            if line.startswith('///'):
                result.append(current_entry)
                current_entry = {}
                last_keyword = None
            else:
                keyword = line[0:12].rstrip()
                if len(keyword) > 0:
                    last_keyword = keyword
                else:
                    keyword = last_keyword
                value = line[12:].rstrip()
                if keyword == 'ENTRY':
                    parts = [x for x in value.split(' ') if len(x) > 0]
                    current_entry['id'] = parts[0]
                    current_entry['tags'] = parts[1:]
                else:
                    if keyword not in current_entry:
                        current_entry[keyword] = []
                    current_entry[keyword].append(value)
    for row in result:
        if 'NAME' in row:
            row['names'] = row['NAME']
            del row['NAME']
        else:
            row['names'] = []
    return result
'''
download the file and put it into directory data
'''
def download_file(url_data):
    counter_tries = 0
    got_file = False
    while not got_file and counter_tries < 11:
        try:
            # download ncbi human genes
            filename = wget.download(url_data, out='data/')
            got_file = True
        except:
            counter_tries += 1
            print(counter_tries)
    if counter_tries >= 11:
        sys.exit('did not get any connection to url in ncbi integration\n\n huhuhu\n')
    return filename

# dictionary mixure ingredient


'''
prepare drug files and relationships dictionary
'''
def prepare_drug_files():
    drugs: Dict[str, Dict[str, List[str] or str]] = {}
    file_name=download_file(url_data_drug)
    header=['id','tags','FORMULA','EXACT_MASS','MOL_WEIGHT','SEQUENCE','SOURCE','alternative_ids','therapeutic_category','xrefs','atc_codes','chemical_structure_group','COMMENT']
    #file with csv information
    writer=open('output/drugs.csv','w',encoding='utf-8')
    csv_writer=csv.writer(writer, delimiter='\t')
    for row in parse_kegg_file(os.path.join(os.path.dirname(__file__), file_name)):
        if row['id']=='D00088':
            print('ok')
        if 'REMARK' in row:
            for value in row['REMARK']:
                if value.startswith('ATC code'):
                    new_atc_codes = sorted({x for x in value.split(':')[1].split(' ') if len(x) > 0})
                    atc_codes = row['atc_codes'] if 'atc_codes' in row else []
                    new_atc_codes.extend(atc_codes)
                    row['atc_codes'] = sorted(set(new_atc_codes))
                elif value.startswith('Same as'):
                    new_alternative_ids = sorted({x for x in value.split(':')[1].split(' ') if len(x) > 0})
                    row['alternative_ids']=new_alternative_ids
                elif value.startswith('Therapeutic category'):
                    new_alternative_ids = sorted({x for x in value.split(':')[1].split(' ') if len(x) > 0})
                    row['therapeutic_category']=new_alternative_ids

                elif value.startswith('Chemical structure group'):
                    new_alternative_ids = sorted({x for x in value.split(':')[1].split(' ') if len(x) > 0})
                    row['chemical_structure_group'] = new_alternative_ids
                elif value.startswith('Product (mixture)'):
            del row['REMARK']
        if 'ATOM' in row:
            del row['ATOM']
        if 'BOND' in row:
            del row['BOND']
        if 'BRACKET' in row:
            del row['BRACKET']

        drugs[row['id']] = row

#
# drug_children_id_map: Dict[str, Set[str]] = {}
# drug_groups: Dict[str, Dict[str, List[str] or str]] = {}
# for row in parse_kegg_file(os.path.join(os.path.dirname(__file__), '../../data/KEGG/dgroup')):
#     if 'REMARK' in row:
#         for i in range(len(row['REMARK']) - 1, -1, -1):
#             if row['REMARK'][i].startswith('ATC code'):
#                 new_atc_codes = sorted({x for x in row['REMARK'][i].split(':')[1].split(' ') if len(x) > 0})
#                 atc_codes = row['atc_codes'] if 'atc_codes' in row else []
#                 new_atc_codes.extend(atc_codes)
#                 row['atc_codes'] = sorted(set(new_atc_codes))
#                 del row['REMARK'][i]
#         if len(row['REMARK']) == 0:
#             del row['REMARK']
#     if 'MEMBER' in row:
#         depth_stack = [row['id']]
#         last_depth = -1
#         for member in row['MEMBER']:
#             depth = len(member) - len(member.lstrip())
#             member = member.strip()
#             _id = member[0:member.index(' ')]
#             if depth > last_depth:
#                 depth_stack.append(_id)
#             elif depth < last_depth:
#                 while len(depth_stack) - 2 > depth:
#                 while len(depth_stack) - 2 > depth:
#                     depth_stack.pop()
#             last_depth = depth
#             depth_stack[-1] = _id
#             if depth_stack[-2] not in drug_children_id_map:
#                 drug_children_id_map[depth_stack[-2]] = set()
#             drug_children_id_map[depth_stack[-2]].add(depth_stack[-1])
#         del row['MEMBER']
#     if '  STEM' in row:
#         row['name_stems'] = row['  STEM']
#         del row['  STEM']
#     if 'COMMENT' in row:
#         row['comments'] = row['COMMENT']
#         del row['COMMENT']
#     if 'CLASS' in row:
#         del row['CLASS']
#     drug_groups[row['id']] = row
#
#
#
# diseases: Dict[str, Dict[str, List[str] or str]] = {}
# for row in parse_kegg_file(os.path.join(os.path.dirname(__file__), '../../data/KEGG/disease')):
#     for key in ['  AUTHORS', 'DESCRIPTION', '  JOURNAL', 'GENE', 'REFERENCE', '  TITLE', 'PATHOGEN', 'COMMENT',
#                 'NETWORK', 'CATEGORY', '  SUBGROUP', '  SUPERGRP', '  ELEMENT']:
#         if key in row:
#             del row[key]
#     if 'DBLINKS' in row:
#         resolved_xrefs = set()
#         for xref in row['DBLINKS']:
#             db_key, ids = xref.split(':')
#             resolved_xrefs.update(['%s:%s' % (db_key, _id) for _id in ids.split(' ') if len(_id) > 0])
#         row['xrefs'] = sorted(resolved_xrefs)
#         del row['DBLINKS']
#     #
#     diseases[row['id']] = row

'''
load ncbi tsv file in and write only the important lines into a new csv file for integration into Neo4j
'''
def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():
    counter_tries=0
    got_file=False
    while not got_file and counter_tries<11:
        try:
            # download ncbi human genes
            filename = wget.download(url_data, out='data/')
            got_file=True
        except:
            counter_tries+=1
            print(counter_tries)
    if counter_tries>=11:
        sys.exit('did not get any connection to url in ncbi integration\n\n huhuhu\n')

    filename_without_gz = filename.rsplit('.', 1)[0]
    # file = open(filename_without_gz, 'wb')
    with io.TextIOWrapper(gzip.open(filename, 'rb')) as f:
        csv_reader=csv.DictReader(f,delimiter='\t')

        # create cypher file
        cypher_file = open('cypher_node.cypher', 'w')
        query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/import_into_Neo4j/ncbi_genes/output_data/genes.csv" As line Fieldterminator '\\t' Create (n:Gene_Ncbi {'''



        dict_header={}
        # add properties to query and fill dictionary
        for header_property in csv_reader.fieldnames:
            #fill dictionary
            if header_property=='#tax_id':
                dict_header[header_property]='tax_id'
            else:
                dict_header[header_property]=header_property
            # add property depending if list or not or int into query

            if header_property in ['Synonyms', 'dbXrefs', 'map_location', 'Feature_type', 'Other_designations']:
                query += header_property + ':split(line.' + header_property + ",'|') ,"
            elif header_property in ['#tax_id', 'GeneID']:
                if header_property == 'GeneID':
                    query += 'identifier:line.' + header_property + ' ,'
                else:
                    query += 'tax_id:line.tax_id ,'
            else:
                query += header_property + ':line.' + header_property + ' ,'

        query = query[:-2] + '});\n'
        cypher_file.write(query)
        query = 'Create Constraint On (node:Gene_Ncbi) Assert node.identifier Is Unique;\n'
        cypher_file.write(query)

        # file for integration into hetionet
        file = open('output_data/genes.csv', 'w')
        writer = csv.DictWriter(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL, fieldnames=csv_reader.fieldnames)
        # writer.writeheader()
        writer.writerow(dict_header)

        # file with all gene from hetionet which are not human
        file_nH = open('output_data/genes_not_human.csv', 'w')
        writer_not_human = csv.DictWriter(file_nH, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                fieldnames=csv_reader.fieldnames)
        writer_not_human.writeheader()


        #count all row in the file
        counter_all=0
        #count all row which will be integrated
        counter_included=0
        #counter all gene which are human and in hetionet
        counter_gene_in_hetionet_and_human=0


        counter_not_same_name_and_description=0

        # generate human gene csv
        for row in csv_reader:

            counter_all+=1
            gene_id =row['GeneID']
            name=row['Full_name_from_nomenclature_authority']
            description=row['description']

            if name!=description and name != '-':
                counter_not_same_name_and_description+=1
                if tax_id == '9606':
                    print(name)
                    print(description)
                    print(gene_id)

            # if gene_id=='100422997':
            #     print('ok')
            #tax id 9606 is human
            tax_id=row['#tax_id']
            if tax_id!='9606':
                writer_not_human.writerow(row)
                found_gene_ids.append(int(gene_id))
            else:
                counter_gene_in_hetionet_and_human+=1
                counter_included+=1
                writer.writerow(row)
                found_gene_ids.append(int(gene_id))

    print(len(found_gene_ids))
    print('all rows in ncbi gene_info file:'+str(counter_all))
    print('all included ncbi gene_info rows in new file:'+str(counter_included))
    print('all genes which are in hetionet and human:'+str(counter_gene_in_hetionet_and_human))
    print('number of name and description not equal:'+str(counter_not_same_name_and_description))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('generate a tsv file with only the human genes')

    prepare_drug_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()