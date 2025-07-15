"""
import os
import sys
# Import pharmebinet utils without proper module structure from two directories up (../../)
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import pharmebinetutils
"""
import os
import datetime
import shutil
import csv
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlparse

USE_VERSION_5 = True

# path to database
path_to_databases = '/mnt/System_Volume_Information/'

# dictionary label to abbreviation
dictionary_label_to_abbreviation = {
    'Anatomy': 'A', 'BiologicalProcess': 'BP', 'BlackBoxEvent': 'B', 'CellType': 'CT', 'CellularComponent': 'CC',
    'Chemical': 'CH',
    'ClinicalAnnotation': 'CA', 'Complex': 'CX', 'Compound': 'C', 'Depolymerisation': 'DP', 'Disease': 'D',
    'EnzymeReactantSet': 'E', 'FailedReaction': 'F', 'Food':'FO', 'Gene': 'G', 'GeneVariant': 'GV', 'Genotype': 'GT',
    'Haplotype': 'H', 'Interaction': 'I', 'Metabolite': 'M', 'MolecularComplex': 'MC', 'MolecularFunction': 'MF',
    'Pathway': 'PW', 'PharmacologicClass': 'PC', 'Phenotype': 'PT', 'PTM':'PTM' ,'Polymerisation': 'PO', 'Product': 'PR',
    'Protein': 'P', 'Reaction': 'RN', 'ReactionLikeEvent': 'RLE', 'Regulation': 'RG', 'RNA': 'R', 'Salt': 'SA',
    'SideEffect': 'SE', 'Symptom': 'S', 'Treatment': 'T', 'Variant': 'V', 'VariantAnnotation': 'VA'
}

get_all_properties_of_on_label = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys
UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
RETURN allfields order by allfields;'''


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
                shutil.copyfileobj(response, f)
            return output_file_path
        except HTTPError as ex:
            if ex.code == 308:
                if 'Location' in ex.headers.keys():
                    url = ex.headers.get('Location')
            else:
                counter_tries += 1
                if counter_tries >= retries:
                    return False
                if not silent:
                    print('Download failed, retry %s/%s' % (counter_tries, retries))
        except Exception as ex:
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
        dictionary[key] = set()
    dictionary[key].add(value)


def print_hline() -> str:
    print('#' * 100)


def get_query_start(base_path: str, file_path: str) -> str:
    base_path = base_path.rstrip('/')
    return """USING PERIODIC COMMIT 10000 LOAD CSV WITH HEADERS FROM "file:%s/%s" AS line FIELDTERMINATOR '\\t'""" % (
        base_path, file_path)


def get_query_import(base_path: str, file_path: str, query: str, delimiter: str = '\\t',
                     batch_number: int = 10000) -> str:
    base_path = base_path.rstrip('/')
    file_path = file_path.lstrip('/')
    if USE_VERSION_5:
        return """LOAD CSV WITH HEADERS FROM "file:%s/%s" AS line FIELDTERMINATOR '%s' Call { with line %s } IN TRANSACTIONS OF %s ROWS;\n""" % (
            base_path, file_path, delimiter, query, str(batch_number))
    else:
        return """USING PERIODIC COMMIT %s LOAD CSV WITH HEADERS FROM "file:%s/%s" AS line FIELDTERMINATOR '%s' %s ;\n""" % (
            str(batch_number), base_path, file_path, delimiter, query)


def prepare_index_query(label: str, prop: str, additional_index: str = '') -> str:
    if USE_VERSION_5:
        # return 'CREATE INDEX index%s%s FOR (node:%s) ON (node.%s);\n' % (label, additional_index, label, prop)
        return 'CREATE CONSTRAINT index%s%s FOR (node:%s) REQUIRE node.%s IS UNIQUE;\n' % (
        label, additional_index, label, prop)
    else:
        return 'Create Constraint On (node:%s) Assert node.%s Is Unique;\n' % (label, prop)


def prepare_index_query_text(label: str, prop: str, additional_index: str = '') -> str:
    return 'CREATE TEXT INDEX indexText%s%s FOR (node:%s) ON (node.%s);\n' % (label, additional_index, label, prop)


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


def prepare_rela_great(rela, label1, label2):
    """
    prepare rela type with right abbreviation
    :param rela:
    :param label1:
    :param label2:
    :return:
    """
    letter_1 = dictionary_label_to_abbreviation[label1]
    letter_2 = dictionary_label_to_abbreviation[label2]
    return rela.upper() + '_' + letter_1 + ''.join([x.lower()[0] for x in rela.split('_')]) + letter_2

# def main():
#     with open('label_to_short.tsv', 'r', encoding='utf-8') as f:
#         csv_reader = csv.reader(f, delimiter='\t')
#         next(csv_reader)
#         dict_label_to_short = {}
#         for row in csv_reader:
#             dict_label_to_short[row[0]] = row[1]
#         print(dict_label_to_short)
#
#
# if __name__ == "__main__":
#     # execute only if run as a script
#     main()
