import datetime
import gzip
import urllib.request
import time, sys

request_headers = {

  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                'Chrome/35.0.1916.47 Safari/537.36'
}


def download_and_unzip(url_end):
    """
    download file and generate un zipped csv file
    """
    url = url_start+url_end
    print(url)
    request_headers["Accept-Encoding"] = "gzip"
    request = urllib.request.Request(url, headers=request_headers)
    success = False
    counter=0
    while not success:
        try:
            with urllib.request.urlopen(request) as response, open(path_of_ctd_data+'/ctd_data/'+url_end.rsplit('.', 1)[0], 'wb') as f:
                test = gzip.GzipFile(fileobj=response)
                f.write(test.read())
            time.sleep(30)
            success = True
        except:
            # Wait 5 minutes to hopefully prevent the cloudflare captcha from triggering again
            counter+=1
            print('had an error')
            time.sleep(60 * 5)
            if counter==10:
                print('is not solved')
                break


# url start
url_start='http://ctdbase.org/reports/'
# 'http://ctdbase.org/downloads/'

# list of ctd file names
list_of_ctd_file_names=[
    'CTD_chem_gene_ixns.tsv.gz',
    'CTD_chemicals_diseases.tsv.gz',
    'CTD_chem_go_enriched.tsv.gz',
    'CTD_chem_pathways_enriched.tsv.gz',
    'CTD_genes_diseases.tsv.gz', # need to be add manually
    'CTD_genes_pathways.tsv.gz',
    'CTD_diseases_pathways.tsv.gz',
    'CTD_pheno_term_ixns.tsv.gz',
    'CTD_exposure_studies.tsv.gz',
    'CTD_exposure_events.tsv.gz',
    'CTD_Phenotype-Disease_biological_process_associations.tsv.gz',
    'CTD_Phenotype-Disease_cellular_component_associations.tsv.gz',
    'CTD_Phenotype-Disease_molecular_function_associations.tsv.gz',
    'CTD_chemicals.tsv.gz',
    'CTD_diseases.tsv.gz',
    'CTD_genes.tsv.gz',
    'CTD_pathways.tsv.gz',
    'CTD_anatomy.tsv.gz'
]

#sepearate
seperate='CTD_chem_gene_ixn_types.csv'

def main():
    print(datetime.datetime.now())
    print('download files')
    global path_of_ctd_data
    if len(sys.argv) > 1:
        path_of_ctd_data = sys.argv[1]
    else:
        sys.exit('need a path')

    # the file without gzip
    seperate_url = url_start + seperate
    request = urllib.request.Request(seperate_url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open(path_of_ctd_data+'/ctd_data/' + seperate, 'wb') as f:
        f.write(response.read())

    #down load all gz files from ctd
    for url_end in list_of_ctd_file_names:
        download_and_unzip(url_end)

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())



if __name__ == "__main__":
    # execute only if run as a script
    main()