import datetime
import time
import urllib.request
import sys


sys.path.append("../..")
import pharmebinetutils

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}


def main():
    print(datetime.datetime.now())
    print('download file')

    # download file
    separate_url = 'https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo'
    # request = urllib.request.Request(separate_url, headers=request_headers)
    # success = False
    # counter = 0
    # while not success:
    #     try:
    #         with urllib.request.urlopen(request) as response, open('data/chebi.obo', 'wb') as f:
    #             f.write(response.read())
    #         success = True
    #     except:
    #         # Wait  to hopefully prevent the cloudflare captcha from triggering again
    #         counter += 1
    #         if counter == 10:
    #             print('\tDownload failed completely')
    #             break
    #         print('\tDownload failed, trying again in 5 minutes...')
    #         time.sleep(60 * 1)

    pharmebinetutils.download_file(separate_url, 'data', 'chebi.obo')

    print('#' * 100)

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
