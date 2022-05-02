import datetime
import time
import urllib.request

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}


def download_file(url, file_name):
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response, open('./' + file_name, 'wb') as f:
        f.write(response.read())


def main():
    print(datetime.datetime.now())
    print('download files')

    with open('key_omim', 'r') as file_key:
        first_line = next(file_key)
        omim_key = first_line.split('=')[1].replace('"', '').replace('\n', '').replace('\r', '')

    download_file('https://omim.org/static/omim/data/mim2gene.txt', 'mim2gene.txt')

    for file_name in ['mimTitles.txt', 'genemap2.txt', 'morbidmap.txt']:
        url = 'https://data.omim.org/downloads/%s/%s' % (omim_key, file_name)
        print(url)
        download_file(url, file_name)
        time.sleep(10)

    print('#' * 100)
    print(datetime.datetime.now())


if __name__ == '__main__':
    # execute only if run as a script
    main()
