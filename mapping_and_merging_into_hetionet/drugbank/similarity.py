import itertools
import sys, csv
import rdkit.Chem
import rdkit.Chem.AllChem
import rdkit.DataStructs
import openbabel.pybel
import datetime

sys.path.append("../..")
import pharmebinetutils

# https://www.rdkit.org/UGM/2012/Landrum_RDKit_UGM.Fingerprints.Final.pptx.pdf
# rdkit dictionary for fingerprint functions
dict_rdfkit_fingerprint = {
    'morgan': rdkit.Chem.AllChem.GetMorganFingerprint,
    'morgan bit vec': rdkit.Chem.AllChem.GetMorganFingerprintAsBitVect,
    'morgan hash': rdkit.Chem.AllChem.GetHashedMorganFingerprint,
    'topologic': rdkit.Chem.RDKFingerprint,
    'maccs_rdkit': rdkit.Chem.AllChem.GetMACCSKeysFingerprint,
    'atom pair': rdkit.Chem.AllChem.GetAtomPairFingerprint,
    'atom pair hash': rdkit.Chem.AllChem.GetHashedAtomPairFingerprint,
    'atom pair hash bit vec': rdkit.Chem.AllChem.GetHashedAtomPairFingerprintAsBitVect,
    'topologic torsin': rdkit.Chem.AllChem.GetTopologicalTorsionFingerprint,
    'topologic torsin bit vec': rdkit.Chem.AllChem.GetHashedTopologicalTorsionFingerprintAsBitVect
}

set_of_bit_vector = set(['morgan_bit_vec', 'atom_pair_hash_bit_vec', 'topologic_torsin_bit_vec'])

# rdkit similarity metrics
# https://www.daylight.com/dayhtml/doc/theory/theory.finger.html
# https://www.rdkit.org/UGM/2012/Landrum_RDKit_UGM.Fingerprints.Final.pptx.pdf
dict_rdfkit_similarity_metric = {
    'dice': rdkit.DataStructs.DiceSimilarity,
    'tanimoto': rdkit.DataStructs.TanimotoSimilarity,
    'cosine': rdkit.DataStructs.CosineSimilarity,
    'sokal': rdkit.DataStructs.SokalSimilarity,
    'russel': rdkit.DataStructs.RusselSimilarity,
    'kulczynski': rdkit.DataStructs.KulczynskiSimilarity,
    'mcconnaughey': rdkit.DataStructs.McConnaugheySimilarity,
    'tversky': rdkit.DataStructs.TverskySimilarity
}

pybel_fingerprints = ['FP2', 'FP3', 'FP4', 'MACCS']


def transform_into_ob_and_rdkit_fromart():
    """
    transform sdf file into open babel and rdkit formart
    :return: mol_pybel, mol_rdkit
    """
    path_to_sdf = '/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/Drugbank_database/drugbank_files_without_preperation/structure/structures.sdf'
    # path_to_sdf='data/structures.sdf'
    # rdkit data
    supplier = rdkit.Chem.SDMolSupplier(path_to_sdf)
    mols_rdf = [x for x in supplier]

    mols_pyble = list(openbabel.pybel.readfile("sdf", path_to_sdf))
    return mols_pyble, mols_rdf


def openbabel_mol_to_smiles(mol):
    return mol.write("smi")


def rdkit_smiles_to_mol(smiles):
    return rdkit.Chem.MolFromSmiles(smiles)


# dictionary rdkit drugbank id to rdkit fingerprints
dict_rdkit_id_to_fingerprints = {}
# dictionary drugbank id to op fingerprints
dict_pybel_id_to_fingerprints = {}


def prepare_fingerprints(mols_pyble, mols_rdf):
    """
    run to all ob/rdkit structures and calculate the different fingerprints and write into dictionaries
    :param mols_pyble:
    :param mols_rdf:
    :return:
    """
    counter = 0

    for mol_pybel in mols_pyble:
        mol_rdk = mols_rdf[counter]

        # some smiles are not correct and they do not need to be checked
        if mol_rdk is None:
            counter += 1
            continue

        drugbank_id = mol_pybel.data['DATABASE_ID']
        # print(drugbank_id)
        dict_pybel = {}
        for fingerprint_formart in pybel_fingerprints:
            fingerprint = mol_pybel.calcfp(fptype=fingerprint_formart)
            dict_pybel[fingerprint_formart] = fingerprint
        dict_pybel_id_to_fingerprints[drugbank_id] = dict_pybel

        dict_rdkit = {}

        for key, funct in dict_rdfkit_fingerprint.items():
            if key.startswith('morgan'):
                fingerprint = funct(mol_rdk, 2)
            else:
                fingerprint = funct(mol_rdk)
            dict_rdkit[key] = fingerprint
        dict_rdkit_id_to_fingerprints[drugbank_id] = dict_rdkit

        if drugbank_id == 'DB00006':
            print(dict_pybel_id_to_fingerprints)
            print(dict_rdkit_id_to_fingerprints)

        counter += 1


# print(dict_pybel_id_to_fingerprints.keys())
# print(len(dict_pybel_id_to_fingerprints))
# print(dict_pybel_id_to_fingerprints['DB00006'])

# set the threshold
threshold = 0.75


def generate_cypher(header, file_name):
    cypherfile = open('compound_interaction/cypher_resemble.cypher', 'w', encoding='utf-8')
    query = '''Match (c1:Compound)-[r:RESEMBLES_CrC]->(c2:Compound) Delete r;\n '''
    cypherfile.write(query)
    query = ''' Match (c1:Compound{identifier:line.id1}), (c2:Compound{identifier:line.id2}) Create (c1)-[:RESEMBLES_CrC{source:"Open Babel and rdKit", unbiased:false, url:"https://pharmebi.net/#/compounds/"+line.id1, resource:['OpenBabel','rdKit'], open_babel_and_rdkit:'yes', license:'%s', '''
    for head in header:
        query += head + ':toFloat(line.' + head + '), '
    query = query % ('CC0 1.0')
    query = query[:-2] + '''}]->(c2) '''

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/drugbank/compound_interaction/{file_name}',
                                              query)
    cypherfile.write(query)
    cypherfile.close()


# dictionary fingerprints_to methods
dict_fp_to_metrics = {}


def calculate_similarities_and_write_into_file():
    set_of_types = set()
    header = ['id1', 'id2', 'morgan bit vec_cosine', 'maccs_dice', 'morgan bit vec_tanimoto', 'morgan bit vec_dice',
              'topologic_tanimoto', 'morgan bit vec_mcconnaughey', 'topologic torsin_tanimoto', 'maccs_rdkit_dice',
              'maccs_rdkit_tanimoto', 'fp3_tanimoto', 'fp4_tanimoto', 'fp2_tanimoto', 'maccs_open_babel_tanimoto',
              'maccs_rdkit_tversky', 'topologic torsin bit vec_dice', 'topologic torsin bit vec_cosine',
              'atom pair_tanimoto', 'topologic_dice', 'morgan_dice', 'atom pair hash_tanimoto', 'atom pair_tversky',
              'topologic torsin_tversky', 'topologic torsin bit vec_tversky', 'morgan_tanimoto',
              'morgan bit vec_russel', 'morgan bit vec_sokal', 'morgan_tversky', 'morgan bit vec_tversky',
              'atom pair hash_dice', 'topologic torsin bit vec_kulczynski', 'topologic torsin bit vec_tanimoto',
              'topologic torsin bit vec_mcconnaughey', 'morgan hash_dice', 'morgan bit vec_kulczynski',
              'atom pair_dice', 'morgan hash_tversky', 'morgan hash_tanimoto', 'topologic torsin_dice',
              'topologic torsin bit vec_russel', 'atom pair hash_tversky', 'topologic torsin bit vec_sokal',
              'topologic_tversky', 'atom_pair_hash_bit_vec_mcconnaughey', 'atom_pair_hash_bit_vec_cosine',
              'atom_pair_hash_bit_vec_kulczynski', 'atom_pair_hash_bit_vec_tanimoto', 'atom_pair_hash_bit_vec_russel',
              'atom_pair_hash_bit_vec_dice', 'atom_pair_hash_bit_vec_sokal', 'atom_pair_hash_bit_vec_tversky']
    header = [x.replace(' ', '_') for x in header]
    file_write = open('compound_interaction/pair_to_similarity.tsv', 'w', encoding='utf-8')
    csv_writer = csv.DictWriter(file_write, fieldnames=header, delimiter='\t')
    csv_writer.writeheader()
    generate_cypher(header, 'pair_to_similarity.tsv')
    counter = 0
    for (id0, fp0), (id1, fp1) in itertools.combinations(dict_pybel_id_to_fingerprints.items(), 2):
        dict_pair = {'id1': id0, 'id2': id1}
        found_at_least_one_similarity = False
        for fingerprint_formart, value in fp0.items():
            value2 = fp1[fingerprint_formart]
            similarity = value | value2
            similarity = round(similarity, 4)
            fingerprint_formart = fingerprint_formart.lower()
            if fingerprint_formart == 'maccs':
                fingerprint_formart = fingerprint_formart + '_open_babel'
            set_of_types.add(fingerprint_formart + '_tanimoto')
            dict_fp_to_metrics[fingerprint_formart] = ['tanimoto']
            # only the one with a higher similarity the 0.5 are written into the file
            if similarity < threshold:
                continue
            found_at_least_one_similarity = True
            dict_pair[fingerprint_formart + '_tanimoto'] = similarity

        if id0 in dict_rdkit_id_to_fingerprints and id1 in dict_rdkit_id_to_fingerprints:
            fp0_rdki = dict_rdkit_id_to_fingerprints[id0]
            fp1_rdki = dict_rdkit_id_to_fingerprints[id1]
            for fp_formart, value in fp0_rdki.items():
                # print(fp_formart)
                value2 = fp1_rdki[fp_formart]
                for metric, func in dict_rdfkit_similarity_metric.items():
                    if metric in ['cosine', 'sokal', 'russel', 'kulczynski',
                                  'mcconnaughey'] and fp_formart not in set_of_bit_vector:
                        continue
                    if metric == 'tversky':
                        similarity = func(value, value2, 0.4, 0.6)
                    else:
                        similarity = func(value, value2)

                    # normalize to 0 and 1 because before it is between -1 and 1
                    if metric == 'mcconnaughey':
                        # formular Z = (x- min(x))/(max(x)-min(x))
                        similarity = (similarity - (-1)) / (1 - (-1))
                    fp_formart = fp_formart.replace(' ', '_')
                    set_of_types.add(fp_formart + '_' + metric)

                    similarity = round(similarity, 4)
                    if similarity < threshold:
                        continue
                    found_at_least_one_similarity = True
                    dict_pair[fp_formart + '_' + metric] = similarity
                    if fp_formart not in dict_fp_to_metrics:
                        dict_fp_to_metrics[fp_formart] = set()
                    dict_fp_to_metrics[fp_formart].add(metric)
        # print(set_of_types)
        if found_at_least_one_similarity:
            csv_writer.writerow(dict_pair)
        counter += 1
        # sys.exit()
        if counter % 1000000 == 0:
            print(counter)

    print(set_of_types)
    print(dict_fp_to_metrics)


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Extract information from sdf into rdkit and open babel')

    mol_pybel, mol_rdkit = transform_into_ob_and_rdkit_fromart()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Calculate different fingerprints')

    prepare_fingerprints(mol_pybel, mol_rdkit)

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('calculates pair was similarities')

    calculate_similarities_and_write_into_file()
    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
