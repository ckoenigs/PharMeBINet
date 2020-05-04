
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
        one_sequence=False
        for line in f:
            line = line.rstrip()
            if line.startswith('///'):
                one_sequence = False
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
                elif keyword=='SEQUENCE':
                    if value.startswith('('):
                        one_sequence=False
                    else:
                        one_sequence=True
                    if one_sequence and keyword  in current_entry:
                        current_entry[keyword][-1]+value
                    else:
                        if keyword not in current_entry:
                            current_entry[keyword] = []
                        current_entry[keyword].append(value)


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
dict_mixture_to_ingredient={}

# dictionary alternative identifier to normal drug id
dict_alternative_id_to_drugbank_id={}

# dictionary drug target (gene symbol) with extra information about the gene form (protein, mrna,..) and network information
dict_drug_target={}

# dictionary target gene symbol to has and ko identifier
dict_target_to_has_and_ko={}

# dictionary drug_indicate_disease
dict_drug_indicate_disease={}

#dictionary metabolite drug-enzyme
dict_metabolite_drug_enzyme={}

#dictioanry metabolite drug-transporter
dict_metabolite_drug_transporter={}

#dictionary of all kind of metabolite types to there dictionary
dict_metabolites_rela={
    'Enzyme':dict_metabolite_drug_enzyme,
    'Transporter':dict_metabolite_drug_transporter
}

#

'''
fill relationship list between mixture and ingredient(drug)
sometimes the ingredient has no id in kegg and is only a string, then the string is used as identifier

general get a dictionary which and an element which contains a name (and a id). The id if existing is extracted and add 
to dictionary as pair with identifier. Else the name is used as identifier.
The name and id is returned.
'''
def fill_mixture_and_ingredient_rela_dict(element, identifier, dict_of_relationship):
    if '[' in element :
        name_id=element.rsplit('[',1)
        id_part = name_id[1]
        id = id_part.split(':')[1].split(']')[0]
        if identifier in dict_of_relationship:
            dict_of_relationship[identifier].add(id)
        else:
            dict_of_relationship[identifier] = set([id])
        return name_id[0].rstrip(), id
    else:
        element = element.rstrip(' ')
        if identifier in dict_of_relationship:
            dict_of_relationship[identifier].add(element)
        else:
            dict_of_relationship[identifier] = set([element])
        return element, element


'''
prepare drug files and relationships dictionary
'''
def prepare_drug_files():
    drugs: Dict[str, Dict[str, List[str] or str]] = {}

    # file_name=download_file(url_data_drug)
    file_name='data/drug'
    header=['id','tags','names','FORMULA','EXACT_MASS','MOL_WEIGHT','SEQUENCE','SOURCE','alternative_ids','therapeutic_category','xrefs','atc_codes','chemical_structure_group','COMMENT','COMPONENT','EFFICACY']
    #file with csv information
    writer=open('output/drugs.csv','w',encoding='utf-8')
    csv_writer=csv.DictWriter(writer, delimiter='\t',fieldnames=header)
    csv_writer.writeheader()
    for row in parse_kegg_file(os.path.join(os.path.dirname(__file__), file_name)):
        identifier=row['id']
        # print(identifier)
        if identifier=='D00015':
            print('ok')

        #sorte the different information from remakr in the different properties
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
                    for alternative_id in new_alternative_ids:
                        if alternative_id in dict_alternative_id_to_drugbank_id:
                            dict_alternative_id_to_drugbank_id[alternative_id].add(identifier)
                        else:
                            dict_alternative_id_to_drugbank_id[alternative_id]=set(identifier)
                elif value.startswith('Therapeutic category'):
                    new_alternative_ids = sorted({x for x in value.split(':')[1].split(' ') if len(x) > 0})
                    row['therapeutic_category']=new_alternative_ids



                elif value.startswith('Chemical structure group'):
                    new_alternative_ids = sorted({x for x in value.split(':')[1].split(' ') if len(x) > 0})
                    row['chemical_structure_group'] = new_alternative_ids
                elif value.startswith('Product (mixture)'):
                    for x in value.split(':')[1].split(' '):
                        if len(x)>0:
                            mixture_id=x.split('<')[0]
                            if mixture_id in dict_mixture_to_ingredient:
                                dict_mixture_to_ingredient[mixture_id].add(identifier)
                            else:
                                dict_mixture_to_ingredient[mixture_id]=set([identifier])
                elif value.startswith('Product'):
                    continue
                else:
                    print(value)

            del row['REMARK']

        # generate rela later to check out the alternative ids !
        #component will be still in the drug because, sometimes the the combination is definded as logic with or's.
        if 'COMPONENT' in row:
            counter=0
            for components in  row['COMPONENT']:
                for element in components.split(', '):
                    if len(element)>0:
                        if element[0]=='(' and element[-1]==')':
                            new_element=element[1:-1]
                            for seperate_element in new_element.split('| '):
                                if len(seperate_element)>0:
                                    fill_mixture_and_ingredient_rela_dict(seperate_element,identifier, dict_mixture_to_ingredient)
                        else:
                            fill_mixture_and_ingredient_rela_dict(element, identifier, dict_mixture_to_ingredient)
                    else:
                        row['COMPONENT'][counter]=row['COMPONENT'][counter].replace(', ,',', ')
                counter+=1

        # update the sequence with what kind of sequence it is
        if 'SEQUENCE' in row:
            if '  TYPE' in row:
                if  len(row['  TYPE'])>1:
                    print(row['SEQUENCE'])
                    print(row['  TYPE'])
                    sys.exit('ohje')
                row['SEQUENCE']=[row['  TYPE'][0]+':'+x for x in row['SEQUENCE']]
                del row['  TYPE']
        if '  TYPE' in row:
            print(row['  TYPE'])

        # fill relationship durg-disease dictionary
        if '  DISEASE' in row:
            for disease in row['  DISEASE']:
                fill_mixture_and_ingredient_rela_dict(disease, identifier, dict_drug_indicate_disease)
            del row['  DISEASE']

        # fill rela to metabolite
        # need own dictionary for enzyme and transporter to integrate this information
        if 'METABOLISM' in row:
            for type_metabolism in row['METABOLISM']:
                # print(type_metabolism)
                type_metabolism=type_metabolism.split(':',1)
                type=type_metabolism[0]
                for meta_protein in type_metabolism[1].split(', '):
                    if type in dict_metabolites_rela:
                        if ':' not in meta_protein:
                            print(meta_protein)
                            id=meta_protein.split('[')[1].replace(']','')
                            if identifier in dict_metabolites_rela[type]:
                                dict_metabolites_rela[type][identifier].add(id)
                            else:
                                dict_metabolites_rela[type][identifier]=set(id)
                        else:
                            name, identifier=fill_mixture_and_ingredient_rela_dict(meta_protein,identifier,dict_metabolites_rela[type])
                    else:
                        sys.exit(type)
            del row['METABOLISM']


        # fill relationship drug-target and build dictionary for different  target
        if 'TARGET' in row:
            network_info = ''
            if '  NETWORK' in row:
                if len(row['  NETWORK']) > 1:
                    print(row['TARGET'])
                    print(row['  NETWORK'])
                    sys.exit('network to long')
                network_info = row['  NETWORK'][0]
                del row['  NETWORK']
            for target in row['TARGET']:


                parts=target.split('[')
                # print(parts)
                if len(parts)>1:
                    if ':' not in parts[1]:
                        gene_symbol=parts[0]+'['+ parts[1]
                    else:
                        gene_symbol = parts[0]
                    gene_symbol=gene_symbol.rstrip()
                    extra_information_of_form_of_protein=''
                    if '(' in parts[-1]:
                        extra_information_of_form_of_protein=parts[-1].split('(')[1].replace(')','')
                    if identifier in dict_drug_target:
                        dict_drug_target[identifier].add((gene_symbol,extra_information_of_form_of_protein,network_info))
                    else:
                        dict_drug_target[identifier]=set((gene_symbol,extra_information_of_form_of_protein, network_info))

                    if not gene_symbol in dict_target_to_has_and_ko:
                        external_identifiers_hsa_ko=[]
                        counter=0
                        # print(parts)
                        for external_ids in parts[1:]:
                            counter+=1
                            if ':' not in external_ids:
                                if counter>1:
                                    sys.exit('multi name with [')
                                continue
                            external_identifiers_hsa_ko.append(external_ids.split(']')[0])
                        # print(external_identifiers_hsa_ko)
                        dict_target_to_has_and_ko[gene_symbol]=prepare_external_links(external_identifiers_hsa_ko)
                else:
                    gene_symbol = parts[0]
                    if identifier in dict_drug_target:
                        dict_drug_target[identifier].add((gene_symbol,'',network_info))
                    else:
                        dict_drug_target[identifier]=set((gene_symbol,'',network_info))
                    dict_target_to_has_and_ko[gene_symbol]=[]
            del row['TARGET']

        # gather and prepare xrefs
        if 'DBLINKS' in row:
            xrefs=prepare_external_links(row['DBLINKS'])
            row['xrefs']=xrefs

            del row['DBLINKS']

        # will yous the class from dgroup file
        if 'CLASS' in row:
            del row['CLASS']
        # THESE HAS NO INFORMATION WHICH ARE NICE TO SEE
        if 'ATOM' in row:
            del row['ATOM']
        if 'BOND' in row:
            del row['BOND']
        if 'BRACKET' in row:
            del row['BRACKET']
        if '  REPEAT' in row:
            del row['  REPEAT']
        if '  ORIGINAL' in row:
            del row['  ORIGINAL']
        if 'INTERACTION' in row:
            del row['INTERACTION']
        csv_writer.writerow(row)

        drugs[identifier] = row

    # os.remove(file_name)

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