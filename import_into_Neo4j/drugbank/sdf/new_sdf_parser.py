import sys, csv

set_properties_sdf = set()
dict_header = ['ALOGPS_LOGP', 'ALOGPS_LOGS', 'ALOGPS_SOLUBILITY', 'CAS_NUMBER', 'DATABASE_ID', 'DATABASE_NAME',
               'DRUGBANK_ID', 'EXACT_MASS', 'FORMULA', 'INCHI_IDENTIFIER', 'INCHI_KEY', 'JCHEM_ACCEPTOR_COUNT',
               'JCHEM_ATOM_COUNT', 'JCHEM_AVERAGE_NEUTRAL_MICROSPECIES_CHARGE', 'JCHEM_AVERAGE_POLARIZABILITY',
               'JCHEM_BIOAVAILABILITY', 'JCHEM_DONOR_COUNT', 'JCHEM_FORMAL_CHARGE', 'JCHEM_GHOSE_FILTER', 'JCHEM_IUPAC',
               'JCHEM_LOGP', 'JCHEM_MDDR_LIKE_RULE', 'JCHEM_NEUTRAL_CHARGE', 'JCHEM_NUMBER_OF_RINGS',
               'JCHEM_PHYSIOLOGICAL_CHARGE', 'JCHEM_PKA', 'JCHEM_PKA_STRONGEST_ACIDIC', 'JCHEM_PKA_STRONGEST_BASIC',
               'JCHEM_POLAR_SURFACE_AREA', 'JCHEM_REFRACTIVITY', 'JCHEM_ROTATABLE_BOND_COUNT', 'JCHEM_RULE_OF_FIVE',
               'JCHEM_TRADITIONAL_IUPAC', 'JCHEM_VEBER_RULE', 'MOLECULAR_WEIGHT', 'NAME', 'SECONDARY_ACCESSION_NUMBERS',
               'SMILES', 'UNII']


def prepare_sdf_file(from_file_name, to_file_name):
    from_file = open(from_file_name, 'r', encoding='utf-8')
    to_file = open(to_file_name, 'w', encoding='utf-8')
    to_csv=csv.DictWriter(to_file,fieldnames=dict_header)
    to_csv.writeheader()
    dict_one_node_information = {}
    key = ''
    counter_entries=0
    for line in from_file:
        if len(line.strip()) != 0:
            if line.startswith("> "):
                key = line.split('<')[1].split('>')[0]
                set_properties_sdf.add(key)
            elif line.strip() == "$$$$":
                counter_entries+=1
                to_csv.writerow(dict_one_node_information)
                dict_one_node_information = {}
                key = ''
            elif key != '':
                if key in dict_one_node_information:
                    print(key)
                    print(dict_one_node_information)
                    sys.exit('multi line information')
                dict_one_node_information[key] = line.strip()

    print('number of entries', counter_entries)


if len(sys.argv) != 3:
    sys.exit('This need as input a sdf file and an output file name as .csv')
my_sdf_file = sys.argv[1]
to_file = sys.argv[2]
prepare_sdf_file(my_sdf_file, to_file)

print(sorted(set_properties_sdf))
