
import datetime
import time
import urllib.request


request_headers = {

  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                'Chrome/35.0.1916.47 Safari/537.36'
}

def download_file(url,file_name):
    """
    Download file
    :param url: string
    :param file_name: string
    :return:
    """
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open('./' + file_name, 'wb') as f:
        f.write(response.read())

file_key=open('key_omim','r')
first_line=next(file_key)
OMIM_KEY=first_line.split("=")[1].replace('"','').replace('\n','')

url_start='https://data.omim.org/downloads/'

url_end={"mimTitles.txt","genemap2.txt","morbidmap.txt"}

def main():
    print(datetime.datetime.utcnow())
    print('download files')

    seperate_url="https://omim.org/static/omim/data/mim2gene.txt"
    download_file(seperate_url, "mim2gene.txt")


    for file in url_end:
        seperate_url = url_start + OMIM_KEY+ '/'+file
        print(seperate_url)
        download_file(seperate_url,file)

        time.sleep(10)


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())



if __name__ == "__main__":
    # execute only if run as a script
    main()