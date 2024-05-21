import requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}

url = "https://datadryad.org/stash/downloads/file_stream/67855"
r = requests.get(url, headers=headers)
with open('aeolus_v1.zip', 'wb') as fh:
    fh.write(r.content)
