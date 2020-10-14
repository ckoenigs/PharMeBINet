
import datetime
import gzip
from io import StringIO
import urllib.request

request_headers = {

  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                'Chrome/35.0.1916.47 Safari/537.36'
}




'''
download file and generate un ziped csv file
'''
def download_and_unzip(url_end):
    url=url_start+url_end
    print(url)
    request_headers["Accept-Encoding"]="gzip"
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open('./ctd_data/'+url_end.rsplit('.',1)[0], 'wb') as f:
        test=gzip.GzipFile(fileobj=response)
        f.write(test.read())

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
    'CTD_pathways.csv.gz',
    'CTD_anatomy.csv.gz'
]

#sepearate
seperate='CTD_chem_gene_ixn_types.csv'

def main():
    print(datetime.datetime.utcnow())
    print('download files')

    # the file without gzip
    seperate_url = url_start + seperate
    request = urllib.request.Request(seperate_url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open('./ctd_data/' + seperate, 'wb') as f:
        f.write(response.read())

    #down load all gz files from ctd
    for url_end in list_of_ctd_file_names:
        download_and_unzip(url_end)

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()