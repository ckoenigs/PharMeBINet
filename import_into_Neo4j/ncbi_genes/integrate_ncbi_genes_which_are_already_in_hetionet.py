import csv
import gzip
import io
import os
import sys, urllib

from rdkit.Chem.MolKey.InchiInfo import console

# Import pharmebinet utils without proper module structure
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import pharmebinetutils



def get_website_source(url: str) -> str:
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/35.0.1916.47 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')

def check_for_new_version():
    """
    check out when the downloaded ncbi gene where last updated and write it into a file.
    Return if a update is needed.
    """
    file_name='version.txt'
    old_date=''
    if os.path.exists(file_name):
        with open(file_name, 'r',encoding='utf-8') as f:
            line=f.readline()
            if line!='need manual checking!':
                old_date=line
            print(line)
    try:
        source=get_website_source('https://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/')
        infos_behind_homo_sapiens = source.split('<a href="Homo_sapiens.gene_info.gz">Homo_sapiens.gene_info.gz</a>')[1].strip().split('\n')[0]
        date = infos_behind_homo_sapiens.split(' ')[0]
        with open(file_name, 'w', encoding='utf-8') as version_file:
            version_file.write(date)
        if old_date==date:
            return False
    except:
        with open(file_name, 'w', encoding='utf-8') as version_file:
            version_file.write('need manual checking!')
    return True

'''
load ncbi tsv file in and write only the important lines into a new tsv file for integration into Neo4j
'''


def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():
    need_update=check_for_new_version()
    if not need_update:
        print('Do not need new version')
        return
    file_url = 'https://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz'
    for path in ['./data', './output']:
        if not os.path.exists(path):
            os.makedirs(path)
    file_name = pharmebinetutils.download_file(file_url, './data')
    if not file_name:
        sys.exit('did not get any connection to url in ncbi integration\n\n')

    with io.TextIOWrapper(gzip.open(file_name, 'rb')) as f:
        csv_reader = csv.DictReader(f, delimiter='\t')

        # create cypher file
        cypher_file = open('cypher_node.cypher', 'w', newline='')
        query = ''' Create (n:Gene_Ncbi {'''

        dict_header = {}
        # add properties to query and fill dictionary
        for header_property in csv_reader.fieldnames:
            # fill dictionary
            if header_property == '#tax_id':
                dict_header[header_property] = 'tax_id'
            else:
                dict_header[header_property] = header_property
            # add property depending if list or not or int into query

            if header_property in ['Synonyms', 'dbXrefs', 'map_location', 'Feature_type', 'Other_designations']:
                query += header_property.lower() + ':split(line.' + header_property + ",'|') ,"
            elif header_property in ['#tax_id', 'GeneID']:
                if header_property == 'GeneID':
                    query += 'identifier:line.' + header_property + ' ,'
                else:
                    query += 'tax_id:line.tax_id ,'
            else:
                query += header_property.lower() + ':line.' + header_property + ' ,'

        query = query + ' license:"CC0 1.0"})'
        query = pharmebinetutils.get_query_import(path_of_directory,
                                                  'import_into_Neo4j/ncbi_genes/output/genes.tsv', query)
        cypher_file.write(query)
        cypher_file.write(pharmebinetutils.prepare_index_query('Gene_Ncbi', 'identifier'))

        # file for integration into pharmebinet
        file = open('output/genes.tsv', 'w', newline='')
        writer = csv.DictWriter(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                fieldnames=csv_reader.fieldnames)
        # writer.writeheader()
        writer.writerow(dict_header)

        # file with all gene from pharmebinet which are not human
        file_nH = open('output/genes_not_human.tsv', 'w', newline='')
        writer_not_human = csv.DictWriter(file_nH, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                          fieldnames=csv_reader.fieldnames)
        writer_not_human.writeheader()

        # count all row in the file
        counter_all = 0
        # count all row which will be integrated
        counter_included = 0

        counter_not_same_name_and_description = 0

        # generate human gene tsv
        for row in csv_reader:
            new_row = {key: ('' if value == '-' else value) for key, value in row.items()}

            counter_all += 1
            gene_id = new_row['GeneID']
            name = new_row['Full_name_from_nomenclature_authority']
            description = new_row['description']
            # tax id 9606 is human
            tax_id = new_row['#tax_id']
            # check for mismatches between name and description
            if name != description and name != '':
                counter_not_same_name_and_description += 1
                if tax_id == '9606':
                    print('Found name <> description mismatch for gene id', gene_id)
                    print(name)
                    print(description)
            # write the row to the respective output file
            if tax_id != '9606':
                writer_not_human.writerow(new_row)
            else:
                counter_included += 1
                writer.writerow(new_row)

    file.close()
    file_nH.close()
    cypher_file.close()

    print('all rows in ncbi gene_info file:', counter_all)
    print('all included ncbi gene_info rows in new file:', counter_included)
    print('number of name and description not equal:', counter_not_same_name_and_description)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    pharmebinetutils.print_timestamp()
    print('generate a tsv file with only the human genes')

    load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes()

    pharmebinetutils.print_hline()
    pharmebinetutils.print_timestamp()


if __name__ == "__main__":
    # execute only if run as a script
    main()
