
import datetime
import wget
import gzip


import requests
import pandas



'''
download file and generate un ziped csv file
'''
def download_and_unzip(url):
    # download Pathway Commons v11
    filename = wget.download(url, out='ctd_data/')
    filename_without_gz =filename.rsplit('.',1)[0]
    file=open(filename_without_gz,'wb')
    with gzip.open(filename,'rb') as f:
        file.write(f.read())
    file.close()

# url start
url_start='http://ctdbase.org/reports/'
# 'http://ctdbase.org/downloads/'

# list of ctd file names
list_of_ctd_file_names=[
    'CTD_chem_gene_ixns.csv.gz',
    'CTD_chemicals_diseases.csv.gz',
    'CTD_chem_go_enriched.csv.gz',
    'CTD_chem_pathways_enriched.csv.gz',
    'CTD_genes_diseases.csv.gz',
    'CTD_genes_pathways.csv.gz',
    'CTD_diseases_pathways.csv.gz',
    'CTD_pheno_term_ixns.csv.gz',
    'CTD_exposure_studies.csv.gz',
    'CTD_exposure_events.csv.gz',
    'CTD_Phenotype-Disease_biological_process_associations.csv.gz',
    'CTD_Phenotype-Disease_cellular_component_associations.csv.gz',
    'CTD_Phenotype-Disease_molecular_function_associations.csv.gz',
    'CTD_chemicals.csv.gz',
    'CTD_diseases.csv.gz',
    'CTD_genes.csv.gz',
    'CTD_pathways.csv.gz'
]

#sepearate
seperate='CTD_chem_gene_ixn_types.csv'

def main():
    print(datetime.datetime.utcnow())
    print('download files')

    #down load all gz files from ctd
    for url_end in list_of_ctd_file_names:
        url=url_start+url_end
        print(url)
        download_and_unzip(url)

    seperate_url=url_start+seperate
    filename = wget.download(seperate_url, out='ctd_data/')

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()