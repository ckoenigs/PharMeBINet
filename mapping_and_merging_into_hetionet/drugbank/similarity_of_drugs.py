import itertools
import gzip, sys
import pandas, csv
import rdkit.Chem
import rdkit.Chem.AllChem
import rdkit.DataStructs
import matplotlib.pyplot as plt
import openbabel.pybel

################################
# https://think-lab.github.io/d/70/
# From  https://github.com/dhimmel/drugbank/blob/55587651ee9417e4621707dac559d84c984cf5fa/similarity.ipynb
####################################

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


def gerenrate_csv_and_plot(similarity_rows, extra_name):
    # Create a DataFrame of pairwise similarities
    similarity_df = pandas.DataFrame(similarity_rows, columns=['compound0', 'compound1', 'similarity'])
    with open('data/similarity_'+extra_name+'.tsv', 'w') as write_file:
        csv_writer=csv.writer(write_file,delimiter='\t')
        csv_writer.writerow(['compound0', 'compound1', 'similarity'])
        for similarity_info in similarity_rows:
            csv_writer.writerow(similarity_info)
    similarity_df.head()

    # histogram of similarities
    plt.hist(similarity_df.similarity, 100);
    plt.show()

def similiarity_with_rdkit(path_to_sdf):
    # https://www.rdkit.org/docs/GettingStartedInPython.html#morgan-fingerprints-circular-fingerprints
    # read sdf file
    supplier = rdkit.Chem.SDMolSupplier(path_to_sdf)
    molecules = [mol for mol in supplier if mol is not None]
    print(len(molecules))

    # calculate fingerprints
    # http://bigchem.eu/sites/default/files/Martin_Vogt_algorithms_in_cheminformatics_150519.pdf
    fingerprints = dict()
    for mol in molecules:
        drugbank_id = mol.GetProp('DATABASE_ID')
        fingerprint = rdkit.Chem.AllChem.GetMorganFingerprint(mol, 2)
        fingerprints[drugbank_id] = fingerprint

    # Calculate pairwise compound similarities
    similarity_rows = list()
    # itertools are combine the element of the dictionary to  "tuples" of all combinations
    for (id0, fp0), (id1, fp1) in itertools.combinations(fingerprints.items(), 2):
        # https://radiopaedia.org/articles/dice-similarity-coefficient#:~:text=The%20Dice%20similarity%20coefficient%2C%20also,between%20two%20sets%20of%20data.
        similarity = rdkit.DataStructs.DiceSimilarity(fp0, fp1)
        similarity = round(similarity, 4)
        similarity_rows.append([id0, id1, similarity])

    gerenrate_csv_and_plot(similarity_rows, 'rdkit')




def similarity_with_pybel(path_to_sdf, fingerprint_formart):
    """

    :param path_to_sdf: string
    :param fingerprint_formart:
            FP2    Indexes linear fragments up to 7 atoms.
            FP3    SMARTS patterns specified in the file patterns.txt
            FP4    SMARTS patterns specified in the file SMARTS_InteLigand.txt
            MACCS    SMARTS patterns specified in the file MACCS.txt
    :return:
    """
    #https://open-babel.readthedocs.io/en/latest/UseTheLibrary/Python_Pybel.html
    fingerprints = dict()

    for mol in openbabel.pybel.readfile("sdf", path_to_sdf):
        # the defaul is fp2
        fingerprint= mol.calcfp(fptype=fingerprint_formart)
        drugbank_id = mol.data['DATABASE_ID']
        fingerprints[drugbank_id] = fingerprint

    # Calculate pairwise compound similarities
    similarity_rows = list()
    # itertools are combine the element of the dictionary to  "tuples" of all combinations
    for (id0, fp0), (id1, fp1) in itertools.combinations(fingerprints.items(), 2):
        # Tanimoto coefficient
        similarity = fp0| fp1
        similarity = round(similarity, 4)
        similarity_rows.append([id0, id1, similarity])


    gerenrate_csv_and_plot(similarity_rows, 'open_babel')


def main():
    if len(sys.argv) > 1:
        path_to_sdf = sys.argv[1]
    else:
        sys.exit('similarity')
    # similiarity_with_rdkit(path_to_sdf)

    similarity_with_pybel(path_to_sdf, 'FP2')


if __name__ == "__main__":
    # execute only if run as a script
    main()




