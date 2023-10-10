import csv
import os
import sys
import datetime

# Import pharmebinet utils without proper module structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import pharmebinetutils

cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
cypher_file_edge = open('output/cypher_edge.cypher', 'w', encoding='utf-8')


def replace_special_symbols(x):
    return x.replace('/', '_').replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').replace('[',
                                                                                                             '').replace(
        ']', '').replace('95%_CI_TEXT', 'CI_TEXT_95')


def prepare_node_cypher_query(file_name, label, properties, list_properties):
    """
    Prepare the cypher query fo a node.
    :param file_name: string
    :param label: string
    :param properties: list
    :param list_properties: list
    :return:
    """
    query = ''' Create (n:GWAS_%s{ '''

    query = query % (label.capitalize())

    for prop in properties:
        prop = replace_special_symbols(prop)
        if prop in list_properties:
            query += prop + ':split(line.' + prop + ',"|"), '
        else:
            query += prop + ':line.' + prop + ', '
    query = query[:-2] + '})'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/gwas/{file_name}', query)
    cypher_file.write(query)
    query = pharmebinetutils.prepare_index_query('GWAS_' + label.capitalize(), properties[0])
    cypher_file.write(query)


def prepare_edge_cypher_query(file_name, label_from, label, rela_name, properties, list_properties):
    """
    Prepare the cypher query fo a node.
    :param file_name: string
    :param label: string
    :param properties: list
    :param list_properties: list
    :return:
    """
    query = ''' Match (n:GWAS_%s{%s:line.%s}), (b:GWAS_%s{%s:line.%s}) Create (n)-[:%s'''

    query = query + '{' if len(properties) > 2 else query
    query = query % (
        label_from.capitalize(), properties[0], properties[0], label.capitalize(), properties[1], properties[1],
        rela_name)
    for prop in properties[2:]:
        prop = replace_special_symbols(prop)
        if prop in list_properties:
            query += prop + ':split(line.' + prop + ',"|"), '
        else:
            query += prop + ':line.' + prop + ', '
    query = query[:-2] + '}]->(b)' if len(properties) > 2 else query + ']->(b)'
    query = pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/gwas/{file_name}', query)
    cypher_file_edge.write(query)


def prepare_disease_nodes(line, disease_id, csv_disease_writer, dict_disease_trait_to_id):
    """
    extract from line disease information and add entry to csv file if not and return the disease id counter and the real
    disease id for this disease
    :param line:
    :param disease_id:
    :param csv_disease_writer:
    :param dict_disease_trait_to_id:
    :return:
    """
    disease = line['DISEASE/TRAIT']
    trait = line['MAPPED_TRAIT']
    if not (disease, trait) in dict_disease_trait_to_id:
        csv_disease_writer.writerow(
            [disease_id, disease, trait, '|'.join(line['MAPPED_TRAIT_URI'].split(', '))])
        dict_disease_trait_to_id[(disease, trait)] = disease_id
        disease_id += 1
        return disease_id, disease_id - 1
    else:
        return disease_id, dict_disease_trait_to_id[(disease, trait)]


def prepare_snp_information(line, dict_snp_id_to_infos, dict_id_with_merge_info, list_snp, list_snp_list_properties,
                            csv_snp_writer):
    """
    first get a snp id. This is either the snp-current-id or the snps. Also, check if this might be merged by check if
    the snp and the current are the same (with rs). Next check if snp is already added or not to tsv file. If not then
    only if not merged the information are prepared and written into the TSV file. If merged information are remember
    in a dictionary  which will removed if one entry is not merged. The existing snps are check if information are
    different.
    :param line:
    :param dict_snp_id_to_infos:
    :param dict_id_with_merge_info:
    :param list_snp:
    :param list_snp_list_properties:
    :param csv_snp_writer:
    :return:
    """
    snp_current = line['SNP_ID_CURRENT']
    # a lot are a list but have the same id 2 times included with set it is removed
    if ', ' in line['SNPS']:
        snps = set(line['SNPS'].split(', '))
    else:
        snps = set(line['SNPS'].split('; '))
    if (snp_current is None or snp_current == '') and len(snps) > 1:
        print('no current', snps)

    own_merge_check = False

    # set the snp id if no current exist use the snps and if current exists check the snps is not equal to current or
    # not
    if snp_current is None or snp_current == '':
        snp_id = '|'.join(snps)
    else:
        snp_id = snp_current
        if len(snps) == 1:
            snp = snps.pop()
            if not snp_id in snp:
                own_merge_check = True

    # check if snp id is not existing already
    if snp_id not in dict_snp_id_to_infos:
        # First check if this is not merged. If merged remember the information in dictionary. If not merge and it was
        # in dictionary of merged then remove and prepare information for TSV file.
        row = [snp_id]
        if line['MERGED'] == '1' or own_merge_check:
            dict_id_with_merge_info[snp_id] = line

        else:
            if snp_id in dict_id_with_merge_info:
                del dict_id_with_merge_info[snp_id]
            for prop in list_snp:
                if prop not in list_snp_list_properties:
                    row.append(line[prop])
                else:
                    if ', ' in line[prop]:
                        row.append('|'.join(line[prop].split(', ')))
                    else:
                        row.append('|'.join(line[prop].split('; ')))
            csv_snp_writer.writerow(row)
            dict_snp_id_to_infos[snp_id] = row
    else:
        index = 1
        # check if same snp id has different information but only the not merged
        if line['MERGED'] != '1' and not own_merge_check:
            for prop in list_snp:
                if prop in list_snp_list_properties:
                    if ', ' in line[prop]:
                        list_of_values = line[prop].split(', ')
                    else:
                        list_of_values = line[prop].split('; ')

                    for value in list_of_values:
                        if value not in dict_snp_id_to_infos[snp_id][index]:
                            print('different list information', 'first', dict_snp_id_to_infos[snp_id][index],
                                  'second', value)
                    index += 1
                    continue
                if line[prop] != dict_snp_id_to_infos[snp_id][index]:
                    if prop in ['SNPS']:
                        index += 1
                        continue
                    print('id', snp_id)
                    print('ohno', prop, 'first', line[prop], 'second', dict_snp_id_to_infos[snp_id][index])
                    print(index, dict_snp_id_to_infos[snp_id])
                index += 1
    return snp_id


def load_csv_and_prepare_data():
    file_url = 'https://www.ebi.ac.uk/gwas/api/search/downloads/alternative'
    file_name = 'data/alternative'
    if not os.path.exists(file_name):
        file_name = pharmebinetutils.download_file(file_url, './data')

    disease_name = 'output/disease.tsv'
    disease_file = open(disease_name, 'w', encoding='utf-8')
    csv_disease_writer = csv.writer(disease_file, delimiter='\t')
    list_disease = ['DISEASE/TRAIT', 'MAPPED_TRAIT', 'MAPPED_TRAIT_URI']
    prepare_node_cypher_query(disease_name, 'disease',
                              ['disease_id'] + [replace_special_symbols(x) for x in list_disease], ['MAPPED_TRAIT_URI'])
    disease_id = 0
    dict_disease_trait_to_id = {}
    csv_disease_writer.writerow(['disease_id'] + [replace_special_symbols(x) for x in list_disease])

    snp_file_name = 'output/snp.tsv'
    snp_file = open(snp_file_name, 'w', encoding='utf-8')
    csv_snp_writer = csv.writer(snp_file, delimiter='\t')
    list_snp = ['REGION', 'CHR_ID', 'CHR_POS', 'INTERGENIC', 'CONTEXT', 'SNP_ID_CURRENT', 'SNPS',
                'UPSTREAM_GENE_DISTANCE', 'DOWNSTREAM_GENE_DISTANCE', 'UPSTREAM_GENE_ID', 'DOWNSTREAM_GENE_ID',
                'SNP_GENE_IDS', 'MAPPED_GENE']
    list_snp_list_properties = ['SNP_GENE_IDS', 'MAPPED_GENE', 'SNP_GENE_IDS', 'CONTEXT', 'SNPS']
    dict_snp_id_to_infos = {}
    csv_snp_writer.writerow(['snp_id'] + [replace_special_symbols(x) for x in list_snp])
    prepare_node_cypher_query(snp_file_name, 'snp', ['snp_id'] + [replace_special_symbols(x) for x in list_snp],
                              list_snp_list_properties)
    # dict of ids where first merged ids are and value the information
    dict_id_with_merge_info = {}

    first = True
    counter = 0
    counter_edge = 0
    with open(file_name, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file, delimiter='\t')
        for line in csv_reader:
            counter += 1
            if first:
                file_name_edge = 'output/edge.tsv'
                edge_file = open(file_name_edge, 'w', encoding='utf-8')
                csv_edge_writer = csv.writer(edge_file, delimiter='\t')
                list_prop = set(line.keys())
                list_prop = list_prop.difference(list_disease)
                list_prop = list_prop.difference(list_snp)
                list_prop.add('SNPS')
                list_prop = list(list_prop)
                list_prop_list = ['REPORTED GENE(S)', 'STRONGEST SNP-RISK ALLELE']
                prepare_edge_cypher_query(file_name_edge, 'snp', 'disease', 'associates',
                                          ['snp_id', 'disease_id'] + list_prop, list_prop_list)

                csv_edge_writer.writerow(['snp_id', 'disease_id'] + [replace_special_symbols(x) for x in list_prop])

                first = False

            # disease part
            disease_id, real_disease_id = prepare_disease_nodes(line, disease_id, csv_disease_writer,
                                                                dict_disease_trait_to_id)

            # SNP part
            snp_id = prepare_snp_information(line, dict_snp_id_to_infos, dict_id_with_merge_info, list_snp,
                                             list_snp_list_properties, csv_snp_writer)

            edge_row = [snp_id, real_disease_id]
            for prop in list_prop:
                edge_row.append(line[prop])
            counter_edge += 1
            csv_edge_writer.writerow(edge_row)
    print('number of snps which are only merged', len(dict_id_with_merge_info), dict_id_with_merge_info.keys())
    print('number of row in GWAS', counter)
    print('number of edges in GWAS', counter_edge)

    for snp_id, line in dict_id_with_merge_info.items():
        row = [snp_id]
        for prop in list_snp:
            if prop not in list_snp_list_properties:
                row.append(line[prop])
            else:
                if ', ' in line[prop]:
                    row.append('|'.join(line[prop].split(', ')))
                else:
                    row.append('|'.join(line[prop].split('; ')))
        csv_snp_writer.writerow(row)


def main():
    print(datetime.datetime.now())

    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        print(path_of_directory)
    else:
        sys.exit('need a path gwas')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('parse adr to tsv')

    load_csv_and_prepare_data()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
