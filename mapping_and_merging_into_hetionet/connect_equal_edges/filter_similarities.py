import sys
import csv
import datetime

from rdkit.Chem.Fingerprints.UnitTestSimScreener import fingerprinter

sys.path.append("../..")
import pharmebinetutils

header = ['id1', 'id2', 'morgan_bit_vec_cosine', 'morgan_bit_vec_tanimoto', 'topologic_tanimoto',
          'morgan_bit_vec_mcconnaughey', 'maccs_rdkit_tanimoto', 'fp3_tanimoto', 'fp4_tanimoto', 'fp2_tanimoto',
          'maccs_open_babel_tanimoto', 'maccs_rdkit_tversky', 'topologic_torsin_bit_vec_cosine', 'atom_pair_tanimoto',
          'atom_pair_hash_tanimoto', 'atom_pair_tversky', 'topologic_torsin_bit_vec_tversky', 'morgan_tanimoto',
          'morgan_tversky', 'morgan_bit_vec_tversky', 'topologic_torsin_bit_vec_kulczynski',
          'topologic_torsin_bit_vec_tanimoto', 'topologic_torsin_bit_vec_mcconnaughey', 'morgan_bit_vec_kulczynski',
          'morgan_hash_tversky', 'morgan_hash_tanimoto', 'atom_pair_hash_tversky', 'topologic_tversky',
          'atom_pair_hash_bit_vec_mcconnaughey', 'atom_pair_hash_bit_vec_cosine', 'atom_pair_hash_bit_vec_kulczynski',
          'atom_pair_hash_bit_vec_tanimoto', 'atom_pair_hash_bit_vec_tversky']


def generate_cypher( file_name):
    """
    Generate cypher file and add cypher query
    :param header:
    :param file_name:
    :return:
    """
    cypherfile = open('output/cypher_resemble.cypher', 'w', encoding='utf-8')
    query = ''' Match (c1:Compound{identifier:line.id1}), (c2:Compound{identifier:line.id2}) Create (c1)-[:RESEMBLES_CrC{source:"Open Babel and rdKit by PharMeBINet", unbiased:false, url:"https://pharmebi.net/#/compounds/"+line.id1, resource:['OpenBabel','rdKit', 'PharMeBINet'], open_babel_and_rdkit:true, licenses:['%s'], '''
    for head in header:
        if head    in ['id1','id2']:
            continue 
        query += head + ':toFloat(line.' + head + '), '
    query = query % (pharmebinetutils.dict_source_to_license['pharmebinet'])
    query = query[:-2] + '''}]->(c2) '''

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/connect_equal_edges/{file_name}',
                                              query)
    cypherfile.write(query)
    cypherfile.close()


dict_fingerprint_metric_to_threshold = {'atom_pair_hash_bit_vec_cosine': 0.59,
                                        'atom_pair_hash_bit_vec_kulczynski': 0.62,
                                        'atom_pair_hash_bit_vec_mcconnaughey': 0.62,
                                        'atom_pair_hash_bit_vec_tanimoto': 0.41, 'atom_pair_hash_bit_vec_tversky': 0.59,
                                        'atom_pair_hash_tanimoto': 0.32, 'atom_pair_hash_tversky': 0.49,
                                        'atom_pair_tanimoto': 0.30, 'atom_pair_tversky': 0.47, 'fp2_tanimoto': 0.41,
                                        'fp3_tanimoto': 0.99, 'fp4_tanimoto': 0.57, 'maccs_open_babel_tanimoto': 0.64,
                                        'maccs_rdkit_tanimoto': 0.64, 'maccs_rdkit_tversky': 0.78,
                                        'morgan_bit_vec_cosine': 0.36, 'morgan_bit_vec_kulczynski': 0.38,
                                        'morgan_bit_vec_mcconnaughey': 0.38, 'morgan_bit_vec_tanimoto': 0.21,
                                        'morgan_bit_vec_tversky': 0.35, 'morgan_hash_tanimoto': 0.29,
                                        'morgan_hash_tversky': 0.45, 'morgan_tanimoto': 0.28, 'morgan_tversky': 0.44,
                                        'topologic_tanimoto': 0.54, 'topologic_torsin_bit_vec_cosine': 0.44,
                                        'topologic_torsin_bit_vec_kulczynski': 0.46,
                                        'topologic_torsin_bit_vec_mcconnaughey': 0.5,
                                        'topologic_torsin_bit_vec_tanimoto': 0.28,
                                        'topologic_torsin_bit_vec_tversky': 0.44, 'topologic_tversky': 0.7}



def prepare_filter_file():
    file_name = 'similarity/pair_to_similarity_filter.tsv'
    counter_edges_added = 0
    i = 0
    with open('similarity/pair_to_similarity.tsv', 'r', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f, delimiter='\t')
        with open(file_name, 'w', encoding='utf-8') as write_file:
            csv_writer = csv.DictWriter(write_file, fieldnames=header, delimiter='\t')
            csv_writer.writeheader()
            for row in csv_reader:
                i += 1
                dict_entry = dict()
                dict_entry['id1'] = row['id1']
                dict_entry['id2'] = row['id2']
                counter_over_threshold = 0
                for head in header:
                    if head in {'id1', 'id2'}:
                        continue
                    value = row[head]
                    if value == '' or value == 'nan':
                        continue
                    if float(value) > dict_fingerprint_metric_to_threshold[head]:
                        dict_entry[head] = value
                        counter_over_threshold += 1
                if counter_over_threshold > 0:
                    csv_writer.writerow(dict_entry)
                    counter_edges_added += 1
                if i % 500_000 == 0:
                    print(datetime.datetime.now(), f"{i:,}", f"{counter_edges_added:,}")
    print('number of added edges: ', counter_edges_added)
    print(datetime.datetime.now())
    generate_cypher(file_name)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('go through calculated similarities and filter')

    prepare_filter_file()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
