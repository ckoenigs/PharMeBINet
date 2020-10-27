import itertools
import gzip, sys,  csv
import pandas as pd
import rdkit.Chem
import rdkit.Chem.AllChem
import rdkit.DataStructs
import matplotlib.pyplot as plt
import openbabel.pybel

if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path')

# https://www.rdkit.org/UGM/2012/Landrum_RDKit_UGM.Fingerprints.Final.pptx.pdf
# rdkit dictionary for fingerprint functions
dict_rdfkit_fingerprint={
    'morgan':rdkit.Chem.AllChem.GetMorganFingerprint,
    'morgan bit vec':rdkit.Chem.AllChem.GetMorganFingerprintAsBitVect,
    'morgan hash':rdkit.Chem.AllChem.GetHashedMorganFingerprint,
    'topologic': rdkit.Chem.RDKFingerprint,
    'maccs_rdkit': rdkit.Chem.AllChem.GetMACCSKeysFingerprint,
    'atom pair': rdkit.Chem.AllChem.GetAtomPairFingerprint,
    'atom pair hash': rdkit.Chem.AllChem.GetHashedAtomPairFingerprint,
    'atom pair hash bit vect': rdkit.Chem.AllChem.GetHashedAtomPairFingerprintAsBitVect,
    'topologic torsin': rdkit.Chem.AllChem.GetTopologicalTorsionFingerprint,
    'topologic torsin bit vec': rdkit.Chem.AllChem.GetHashedTopologicalTorsionFingerprintAsBitVect
}

set_of_bit_vector=set(['morgan bit vec','atom pair hash bit vec','topologic torsin bit vec'])

# rdkit similarity metrics
# https://www.daylight.com/dayhtml/doc/theory/theory.finger.html
# https://www.rdkit.org/UGM/2012/Landrum_RDKit_UGM.Fingerprints.Final.pptx.pdf
dict_rdfkit_similarity_metric={
    'dice':rdkit.DataStructs.DiceSimilarity,
    'tanimoto':rdkit.DataStructs.TanimotoSimilarity,
    'cosine':rdkit.DataStructs.CosineSimilarity,
    'sokal':rdkit.DataStructs.SokalSimilarity,
    'russel':rdkit.DataStructs.RusselSimilarity,
    'kulczynski': rdkit.DataStructs.KulczynskiSimilarity,
    'mcconnaughey':rdkit.DataStructs.McConnaugheySimilarity,
    'tversky':rdkit.DataStructs.TverskySimilarity
}

pybel_fingerprints=['FP2', 'FP3', 'FP4', 'MACCS']


# path_to_sdf='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/Drugbank_database/drugbank_files_without_preperation/structure/structures.sdf'
path_to_sdf='data/structures.sdf'
#rdkit data
supplier = rdkit.Chem.SDMolSupplier(path_to_sdf)
mols_rdf= [x for x in supplier]

mols_pyble=list(openbabel.pybel.readfile("sdf", path_to_sdf))

def openbabel_mol_to_smiles(mol):
    return mol.write("smi")

def rdkit_smiles_to_mol(smiles):
    return rdkit.Chem.MolFromSmiles(smiles)


counter = 0
dict_rdkit_id_to_fingerprints = {}
dict_pybel_id_to_fingerprints = {}

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

#print(dict_pybel_id_to_fingerprints.keys())
#print(len(dict_pybel_id_to_fingerprints))
#print(dict_pybel_id_to_fingerprints['DB00006'])

threshold=0.5

def genrate_cypher(header, file_name):
    cypherfile = open('compound_interaction/cypher_resemble.cypher', 'w', encoding='utf-8')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/drugbank/compound_interaction/%s" As line Match (c1:Compound{identifier:line.db1}), (c2:Compound{identifier:line.db2}) Create (c1)-[:RESEMBLES_CrC{source:"Open Babel and rdKit", unbiased:false, resource:['OpenBabel','rdKit'],  license:'%s', '''
    for head in header:
        head=head.replace(' ','_')
        query+= head+':toFloat(line.'+head+'), '
    query = query % (file_name,'CC0 1.0')
    query=query[:-2]+''')}]->(c2);\n '''
    cypherfile.write(query)
    cypherfile.close()

set_of_types=set()
header=['id1','id2','morgan bit vec_cosine', 'maccs_dice', 'morgan bit vec_tanimoto', 'morgan bit vec_dice', 'topologic_tanimoto', 'morgan bit vec_mcconnaughey', 'topologic torsin_tanimoto', 'maccs_rdkit_dice', 'maccs_rdkit_tanimoto', 'fp3_tanimoto', 'fp4_tanimoto', 'fp2_tanimoto', 'maccs_open_babel_tanimoto', 'maccs_rdkit_tversky', 'topologic torsin bit vec_dice', 'topologic torsin bit vec_cosine', 'atom pair_tanimoto', 'topologic_dice', 'morgan_dice', 'atom pair hash_tanimoto', 'atom pair_tversky', 'topologic torsin_tversky', 'topologic torsin bit vec_tversky', 'morgan_tanimoto', 'morgan bit vec_russel', 'morgan bit vec_sokal', 'morgan_tversky', 'morgan bit vec_tversky',  'atom pair hash_dice', 'topologic torsin bit vec_kulczynski', 'topologic torsin bit vec_tanimoto', 'topologic torsin bit vec_mcconnaughey', 'morgan hash_dice', 'morgan bit vec_kulczynski', 'atom pair_dice',  'atom pair hash bit vect_tversky', 'morgan hash_tversky', 'morgan hash_tanimoto', 'topologic torsin_dice', 'topologic torsin bit vec_russel', 'atom pair hash bit vect_tanimoto', 'atom pair hash_tversky',  'topologic torsin bit vec_sokal',  'topologic_tversky', 'atom pair hash bit vect_dice']
file_write=open('pair_to_similarity.tsv','w',encoding='utf-8')
csv_writer= csv.DictWriter(file_write, fieldnames=header)
csv_writer.writeheader()
genrate_cypher(header, 'compound_interaction/pair_to_similarity.tsv')
counter=0
for (id0, fp0), (id1, fp1) in itertools.combinations(dict_pybel_id_to_fingerprints.items(), 2):
    dict_pair = {'id1': id0, 'id2':id1}
    for fingerprint_formart, value in fp0.items():
        value2 = fp1[fingerprint_formart]
        similarity = value | value2
        similarity = round(similarity, 4)
        fingerprint_formart=fingerprint_formart.lower()
        if fingerprint_formart=='maccs':
            fingerprint_formart=fingerprint_formart+'_open_babel'
        set_of_types.add(fingerprint_formart + '_tanimoto')
        # only the one with a higher similarity the 0.5 are written into the file
        if similarity<threshold:
            continue
        dict_pair[fingerprint_formart + '_tanimoto'] = similarity

    if id0 in dict_rdkit_id_to_fingerprints and id1 in dict_rdkit_id_to_fingerprints:
        fp0_rdki = dict_rdkit_id_to_fingerprints[id0]
        fp1_rdki = dict_rdkit_id_to_fingerprints[id1]
        for fp_formart, value in fp0_rdki.items():
            #print(fp_formart)
            value2 = fp1_rdki[fp_formart]
            for metric, func in dict_rdfkit_similarity_metric.items():
                if metric in  ['cosine','sokal','russel','kulczynski','mcconnaughey'] and fp_formart not in set_of_bit_vector:
                    continue
                if metric  =='tversky':
                    similarity = func(value, value2,0.4,0.6)
                else:
                    similarity = func(value, value2)

                # normalize to 0 and 1 because before it is between -1 and 1
                if metric=='mcconnaughey':
                    # formular Z = (x- min(x))/(max(x)-min(x))
                    similarity= (similarity-(-1))/(1-(-1))

                set_of_types.add(fp_formart + '_' + metric)

                similarity = round(similarity, 4)
                if similarity < threshold:
                    continue
                dict_pair[fp_formart + '_' + metric] = similarity
    #print(set_of_types)
    csv_writer.writerow(dict_pair)
    counter+=1
    sys.exit()
    if counter%10000==0:
        print(counter)

print(set_of_types)
