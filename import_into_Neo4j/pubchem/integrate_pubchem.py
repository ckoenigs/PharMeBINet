import sys, csv, datetime
import gzip, os

sys.path.append("..")
import pharmebinetutils

# set of properties
set_properties_sdf = set()

# set of properties which are list
set_list_prop = set()


def prepare_dictionary(dictionary):
    '''
    Prepare the dictionary properties
    '''
    for key, value in dictionary.items():
        if type(value) == list:
            dictionary[key] = '|'.join(value)


def prepare_sdf_file(from_file_name, to_csv):
    """
    Download if not already existing. Extract from SDF information for TSV file.
    """
    filename = path_of_pubchem_data + 'data/' + from_file_name
    if not os.path.exists(filename):
        print('download')
        url_path = f'https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF/{from_file_name}'
        # download ncbi human genes
        pharmebinetutils.download_file(url_path, out=path_of_pubchem_data + 'data/')

    file = gzip.open(filename, 'rb')

    # from_file = open(from_file_name, 'r')
    dict_one_node_information = {}
    key = ''
    counter_entries = 0
    for line in file:
        line = line.decode('utf-8')
        if len(line.strip()) != 0:
            if line.startswith("> "):
                key = line.split('<')[1].split('>')[0]
                set_properties_sdf.add(key)
            elif line.strip() == "$$$$":
                counter_entries += 1
                try:
                    prepare_dictionary(dict_one_node_information)
                    to_csv.writerow(dict_one_node_information)
                except:
                    print('no header')
                dict_one_node_information = {}
                key = ''
            elif key != '':
                if key in dict_one_node_information:
                    set_list_prop.add(key)
                    if type(dict_one_node_information[key]) != list:
                        dict_one_node_information[key] = [dict_one_node_information[key]]
                    dict_one_node_information[key].append(line.strip())
                    continue

                dict_one_node_information[key] = line.strip()

    print('number of entries', counter_entries)


def prepare_cypher_file(file_name):
    """
    prepare cypher file with cypher query
    """
    with open('output/cypher.cypher', 'w', encoding='utf8') as f:
        list_of_prop = []
        for head in header:
            if head not in set_list_prop:
                list_of_prop.append(head + ':line.' + head)
            else:
                list_of_prop.append(head + ':split(line.' + head + ',"|")')

        query = f'Create (n:PubChem_Compound {{ {", ".join(list_of_prop)} }})'
        f.write(pharmebinetutils.get_query_import(path_of_pubchem_data, file_name, query))
        f.write(pharmebinetutils.prepare_index_query('PubChem_Compound','PUBCHEM_COMPOUND_CID'))


header = ['PUBCHEM_COMPOUND_CID', 'PUBCHEM_CACTVS_TAUTO_COUNT', 'PUBCHEM_XLOGP3_AA', 'PUBCHEM_ATOM_UDEF_STEREO_COUNT',
          'PUBCHEM_CACTVS_COMPLEXITY', 'PUBCHEM_IUPAC_INCHI', 'PUBCHEM_IUPAC_INCHIKEY', 'PUBCHEM_CACTVS_ROTATABLE_BOND',
          'PUBCHEM_COORDINATE_TYPE', 'PUBCHEM_IUPAC_CAS_NAME', 'PUBCHEM_XLOGP3', 'PUBCHEM_ISOTOPIC_ATOM_COUNT',
          'PUBCHEM_NONSTANDARDBOND', 'PUBCHEM_MOLECULAR_WEIGHT', 'PUBCHEM_CACTVS_HBOND_ACCEPTOR', 'PUBCHEM_IUPAC_NAME',
          'PUBCHEM_COMPONENT_COUNT', 'PUBCHEM_CACTVS_HBOND_DONOR', 'PUBCHEM_MOLECULAR_FORMULA',
          'PUBCHEM_MONOISOTOPIC_WEIGHT', 'PUBCHEM_CACTVS_SUBSKEYS', 'PUBCHEM_HEAVY_ATOM_COUNT',
          'PUBCHEM_IUPAC_SYSTEMATIC_NAME', 'PUBCHEM_COMPOUND_CANONICALIZED', 'PUBCHEM_BONDANNOTATIONS',
          'PUBCHEM_OPENEYE_CAN_SMILES', 'PUBCHEM_IUPAC_TRADITIONAL_NAME', 'PUBCHEM_CACTVS_TPSA',
          'PUBCHEM_IUPAC_NAME_MARKUP', 'PUBCHEM_TOTAL_CHARGE', 'PUBCHEM_EXACT_MASS', 'PUBCHEM_BOND_DEF_STEREO_COUNT',
          'PUBCHEM_BOND_UDEF_STEREO_COUNT', 'PUBCHEM_ATOM_DEF_STEREO_COUNT', 'PUBCHEM_OPENEYE_ISO_SMILES',
          'PUBCHEM_REFERENCE_STANDARDIZATION', 'PUBCHEM_IUPAC_OPENEYE_NAME']


def main():
    print(datetime.datetime.now())

    global path_of_pubchem_data
    if len(sys.argv) > 1:
        path_of_pubchem_data = sys.argv[1] + 'pubchem/'
    else:
        sys.exit('need a path SMPDB')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pubchem data and parse to TSV file')

    file_name = 'pubchem_nodes.tsv'
    to_file = open(path_of_pubchem_data + file_name, 'w', encoding='utf-8', newline='')

    to_csv = csv.DictWriter(to_file, fieldnames=header, delimiter='\t')
    to_csv.writeheader()
    counter = 1
    index = 1
    steps_width = 500000
    # Compound_172000001_172500000.sdf.gz
    while counter < 172500000:
        # 172500000
        prepare_sdf_file(f'Compound_{str(counter).zfill(9)}_{str(steps_width * index).zfill(9)}.sdf.gz', to_csv)
        counter += steps_width
        print(datetime.datetime.now())
        index += 1
    print(set_properties_sdf)

    for prop in set_properties_sdf:
        if prop not in header:
            print('ohje')

    prepare_cypher_file(file_name)

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
