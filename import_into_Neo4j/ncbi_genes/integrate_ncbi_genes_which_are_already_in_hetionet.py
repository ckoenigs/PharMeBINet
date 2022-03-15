import datetime
import sys, csv, wget
import gzip, io, requests

url_data = 'ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz'

# list of found genes
found_gene_ids = []

'''
load ncbi tsv file in and write only the important lines into a new tsv file for integration into Neo4j
'''


def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():
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

    filename_without_gz = filename.rsplit('.', 1)[0]
    # file = open(filename_without_gz, 'wb')
    with io.TextIOWrapper(gzip.open(filename, 'rb')) as f:
        csv_reader = csv.DictReader(f, delimiter='\t')

        unzip_file = open('data/Homo_sapiens.gene_info', 'w', encoding='utf-8')
        csv_unzip = csv.DictWriter(unzip_file, fieldnames=csv_reader.fieldnames, delimiter='\t')
        csv_unzip.writeheader()

        # create cypher file
        cypher_file = open('cypher_node.cypher', 'w')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/import_into_Neo4j/ncbi_genes/output_data/genes.tsv" As line Fieldterminator '\\t' Create (n:Gene_Ncbi {'''

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

        query = query + ' license:"CC0 1.0"});\n'
        cypher_file.write(query)
        query = 'Create Constraint On (node:Gene_Ncbi) Assert node.identifier Is Unique;\n'
        cypher_file.write(query)

        # file for integration into hetionet
        file = open('output_data/genes.tsv', 'w')
        writer = csv.DictWriter(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                fieldnames=csv_reader.fieldnames)
        # writer.writeheader()
        writer.writerow(dict_header)

        # file with all gene from hetionet which are not human
        file_nH = open('output_data/genes_not_human.tsv', 'w')
        writer_not_human = csv.DictWriter(file_nH, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                                          fieldnames=csv_reader.fieldnames)
        writer_not_human.writeheader()

        # count all row in the file
        counter_all = 0
        # count all row which will be integrated
        counter_included = 0
        # counter all gene which are human and in hetionet
        counter_gene_in_hetionet_and_human = 0

        counter_not_same_name_and_description = 0

        # generate human gene tsv
        for row in csv_reader:
            new_row = {}
            for key, value in row.items():
                if value == '-':
                    new_row[key] = ''
                else:
                    new_row[key] = value
            csv_unzip.writerow(new_row)

            counter_all += 1
            gene_id = new_row['GeneID']
            name = new_row['Full_name_from_nomenclature_authority']
            description = new_row['description']

            # tax id 9606 is human
            tax_id = new_row['#tax_id']

            if name != description and name != '':
                counter_not_same_name_and_description += 1
                if tax_id == '9606':
                    print(name)
                    print(description)
                    print(gene_id)

            if tax_id != '9606':
                writer_not_human.writerow(new_row)
                found_gene_ids.append(int(gene_id))
            else:
                counter_gene_in_hetionet_and_human += 1
                counter_included += 1
                writer.writerow(new_row)
                found_gene_ids.append(int(gene_id))

    print(len(found_gene_ids))
    print('all rows in ncbi gene_info file:' + str(counter_all))
    print('all included ncbi gene_info rows in new file:' + str(counter_included))
    print('all genes which are in hetionet and human:' + str(counter_gene_in_hetionet_and_human))
    print('number of name and description not equal:' + str(counter_not_same_name_and_description))


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('generate a tsv file with only the human genes')

    load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
