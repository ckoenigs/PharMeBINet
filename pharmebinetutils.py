"""
import os
import sys
# Import pharmebinet utils without proper module structure from two directories up (../../)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import pharmebinetutils
"""
import os
import datetime
import urllib.request
from urllib.parse import urlparse


def download_file(url: str, out: str = './', file_name: str or None = None, retries: int = 10, silent: bool = False,
                  force_download: bool = True) -> str or False:
    """
    Download a file from the provided url

    Args:
        url: Url of the file to be downloaded
        out: Output path where the file is downloaded to (default "./")
        file_name: File name of the downloaded file on disk (by default extracted from url)
        retries: Number of download retries if download failed (default 10)
        silent: Whether console output should be printed or not (default False)
        force_download: Whether the file is re-downloaded if already on disk or not (default True)

    Returns:
        Returns the file path of the downloaded file on disk or False if all download retries failed
    """
    # Prevent infinite loop if provided retries is negative
    retries = max(retries, 0)
    # Retrieve the file name from the url if not provided as parameter
    if file_name is None:
        file_name = os.path.basename(urlparse(url).path)
    output_file_path = os.path.join(out, file_name)
    # Create the output directly if not exists
    if not os.path.exists(out):
        os.makedirs(out)
    # If we don't force a re-download and the file already exists just return the file name
    if not force_download and os.path.exists(output_file_path):
        return output_file_path
    if not silent:
        print('Downloading file "%s"' % url)
    counter_tries = 0
    while True:
        try:
            with urllib.request.urlopen(url) as response, open(output_file_path, 'wb') as f:
                f.write(response.read())
            return output_file_path
        except:
            counter_tries += 1
            if counter_tries >= retries:
                return False
            if not silent:
                print('Download failed, retry %s/%s' % (counter_tries, retries))


def print_timestamp():
    print(datetime.datetime.now())


def add_entry_to_dict_to_set(dictionary, key, value):
    """
    Add key and value to a dictionary.
    :param dictionary: dictionary
    :param key: any
    :param value: any but no list or dict
    :return:
    """
    if key not in dictionary:
        dictionary[key]=set()
    dictionary[key].add(value)


def print_hline():
    print('#' * 100)


def get_query_start(base_path: str, file_path: str) -> str:
    base_path = base_path.rstrip('/')
    return """USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:%s/%s" AS line FIELDTERMINATOR '\\t'""" % (
        base_path, file_path)


def resource_add_and_prepare(resource, source):
    """
    add to resource a new source and generate a sort join string
    :param resource: list/set
    :param source: string
    :return: string
    """
    resource = set(resource)
    resource.add(source)
    return '|'.join(sorted(resource, key=lambda s: s.lower()))

def prepare_obo_synonyms(synonym):
    """
    Prepare the somtimes synonyms looking like '"synonym" [source]' and to get only the synonym information this split
    for [ and remove the first " and last " fom synonyms.
    :param synonym:
    :return:
    """
    if ' [' in synonym:
        synonym = synonym.rsplit(' [', 1)[0][1:-1]
    return synonym
