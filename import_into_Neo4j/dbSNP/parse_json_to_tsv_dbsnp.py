import sys
import time
import datetime
import glob
import bz2
import urllib.request
import os.path
import wget

sys.path.append(".")
import prepare_a_single_node

request_headers = {

    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}


def download_file(url, file_name):
    """
    Download file
    :param url: string
    :param file_name: string
    :return:
    """
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open('./' + file_name, 'wb') as f:
        f.write(response.read())



def open_json_file_write_into_csv(path_to_data):
    """
    open json file
    """

    if not os.path.isfile(path_to_data + '/refsnp-chrY.json.bz2'):
        url = 'https://ftp.ncbi.nih.gov/snp/latest_release/JSON/refsnp-chr%s.json.bz2'
        list_chromosome = list(range(1, 22))
        list_chromosome.append('X')
        list_chromosome.append('Y')
        # list_chromosome=['Y']
        for chr in list_chromosome:
            url_file = url % (chr)
            print(url_file)
            filename = wget.download(url_file, out=path_to_data + '/')
            # request= urllib.request.Request(url_file, headers=request_headers)
            # with urllib.request.urlopen(request) as response, open(path_to_data+'/'+url_file.rsplit('/',1)[1], 'wb') as f:
            #     f.write(response.read())
            time.sleep(30)

        # sys.exit('only download else it takes  too much time')

    # open and load the content of the json file
    # json_file = open('data/refsnp-sample.json', 'r')
    # json_file = open('data/part.json', 'r')
    # json_file = open('data/biger_head.json', 'r')
    # json_file = open('data/refsnp-chrY.json', 'r')
    counter = 0

    files = glob.glob(path_to_data + '/refsnp-chr*.json.bz2')
    for file in files:
        print(file)
        print(datetime.datetime.utcnow())
        json_file = bz2.open(file, "rb")
        print(datetime.datetime.utcnow())
        chr=file.split('refsnp-')[1].split('.json')[0]
        prepare_a_single_node.run_through_list_of_nodes_as_json_string(path_of_directory, path_to_data, json_file,chr )
        # counter = 0
        # for line in json_file:
        #     counter += 1
        #     # if counter == 15727:
        #     #     print('huhu')
        #     prepare_a_single_node.prepare_json_information_to_tsv(line, chr, path_to_data)
        #     # prepare_json_information_to_tsv(line, chr)
        #     if counter % 10000 == 0:
        #         print(counter)
        #         print(datetime.datetime.utcnow())
        sys.exit()


def main():
    global path_of_directory, path_to_data
    # path to data for windows
    if len(sys.argv) == 3:
        path_to_data = sys.argv[1]+'/'
        path_of_directory = sys.argv[2]
    else:
        sys.exit('need path to project (dbsnp)')

    print('load json and prepare files')
    print(datetime.datetime.utcnow())

    open_json_file_write_into_csv(path_to_data)

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
