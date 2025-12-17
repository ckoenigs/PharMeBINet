import os.path
import sys, csv
import gzip
import urllib.request
import glob, datetime

if len(sys.argv) < 2:
    sys.exit('missing path where to save the data')

path_to_data = sys.argv[1]
if not os.path.exists('output'):
    os.mkdir('output')

if not os.path.exists(os.path.join(path_to_data, 'pubchem')):
    os.mkdir(os.path.join(path_to_data, 'pubchem'))

# inchikey to pubchem id file
to_file = "output/inchikey_to_pubchem.tsv"
to_file = open(to_file, 'w', encoding='utf-8', newline='')
to_csv = csv.writer(to_file, delimiter='\t')
to_csv.writerow(['inchikey', 'pubmed_id'])

# request header
request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}


def get_website_source(url: str) -> str:
    """
    Request the html content of a page with a request header
    """
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')


# list of all file name form pubchem or already downloaded data folder
file_name_list = []
url_start = 'https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF/'
try:
    # get html code of page and extract the file names
    source = get_website_source(url_start)
    for file_name in source.split('</a>'):
        if file_name.strip() == '':
            continue
        file_name_with_link = file_name.split('\n')[1].split('>')[1]
        if file_name_with_link.endswith('.gz') and file_name_with_link.startswith('Compound'):
            # print('file_name', file_name_with_link)
            file_name_list.append(file_name_with_link)
except:
    sys.exit('error getting file names')
print(file_name_list)

# set of multiline sdf properties
set_of_list_props = {'PUBCHEM_BONDANNOTATIONS', 'PUBCHEM_COORDINATE_TYPE', 'PUBCHEM_NONSTANDARDBOND'}


def prepare_sdf_file(from_file_name, to_csv_file):
    """
    open gz file and parse the sdf information into a dictionary and in the end write it into sql and tsv file
    :param from_file_name:
    :param to_csv_file:
    :return:
    """

    dict_one_node_information = {}
    key = ''
    counter_entries = 0

    with gzip.open(from_file_name, 'rt') as f:
        for line in f:
            if len(line.strip()) != 0:
                if line.startswith("> "):
                    key = line.split('<')[1].split('>')[0]
                elif line.strip() == "$$$$":
                    counter_entries += 1
                    if 'PUBCHEM_IUPAC_INCHIKEY' in dict_one_node_information:
                        to_csv_file.writerow([dict_one_node_information['PUBCHEM_IUPAC_INCHIKEY'],
                                              dict_one_node_information['PUBCHEM_COMPOUND_CID']
                                              ])
                    else:
                        print('no inchikey',dict_one_node_information)
                    dict_one_node_information = {}
                    key = ''
                elif key != '':
                    if key in dict_one_node_information and key not in set_of_list_props:
                        sys.exit('multi line information')
                    if not key in set_of_list_props:
                        dict_one_node_information[key] = line.strip()
                    else:
                        if not key in dict_one_node_information:
                            dict_one_node_information[key] = []
                        dict_one_node_information[key].append(line.strip())


counter = 0
print('number of files', len(file_name_list), datetime.datetime.now())
# go through all file names and if they are not in data than download
# then parse the file
for file_name in file_name_list:
    combined_file_name = path_to_data + 'pubchem/' + file_name
    if not os.path.exists(combined_file_name):
        url_file = url_start + file_name
        print('downloading', url_file, datetime.datetime.now())
        request = urllib.request.Request(url_file, headers=request_headers)
        with urllib.request.urlopen(request) as response, open(combined_file_name, 'wb') as out_file:
            out_file.write(response.read())
    prepare_sdf_file(combined_file_name, to_csv)
    counter += 1
    if counter % 100 == 0:
        print('finished files', counter, datetime.datetime.now())
