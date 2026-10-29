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
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlparse
import struct
import time
#import playwright
from playwright.sync_api import sync_playwright

USE_VERSION_5 = True

# path to database
path_to_databases = '/mnt/d/databases/'

# dictionary label to abbreviation
dictionary_label_to_abbreviation = {
    'Anatomy': 'A', 'BiologicalProcess': 'BP', 'BlackBoxEvent': 'B', 'CellType': 'CT', 'CellularComponent': 'CC',
    'Chemical': 'CH',
    'ClinicalAnnotation': 'CA', 'Compound': 'C', 'Depolymerisation': 'DP', 'Disease': 'D',
    'EnzymeReactantSet': 'E', 'FailedReaction': 'F', 'Food':'FO', 'Gene': 'G', 'GeneVariant': 'GV', 'Genotype': 'GT',
    'Haplotype': 'H', 'Interaction': 'I', 'Metabolite': 'M', 'MolecularComplex': 'MC', 'MolecularFunction': 'MF',
    'Pathway': 'PW', 'PharmacologicClass': 'PC', 'Phenotype': 'PT' ,'Polymerisation': 'PO', 'Product': 'PR',
    'Protein': 'P', 'PTM':'PTM', 'Reaction': 'RN', 'ReactionLikeEvent': 'RLE', 'Regulation': 'RG', 'RNA': 'R', 'Salt': 'SA',
    'SideEffect': 'SE', 'Symptom': 'S', 'Treatment': 'T', 'Variant': 'V', 'VariantAnnotation': 'VA'
}

get_all_properties_of_on_label = '''MATCH (p:%s) WITH DISTINCT keys(p) AS keys
UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
RETURN allfields order by allfields;'''


dict_source_to_license = {
    'adrecs': 'CC BY-NC-SA 4.0',
    'aeolus': 'CC0 1.0',
    'bindingdb':'CC BY 3.0 + CC BY-SA 3.0',
    'biogrid':'The MIT License',
    'chebi':'CC BY 4.0',
    'cl':'CC BY 4.0',
    'clinvar':'https://www.ncbi.nlm.nih.gov/home/about/policies/',
    'ctd':"© 2002–2012 MDI Biological Laboratory. © 2012–2026 NC State University. All rights reserved.",
    'dbsnp':'https://www.ncbi.nlm.nih.gov/home/about/policies/',
    'ddinter':'CC BY-NC-SA 4.0',
    'diseases': 'CC BY 4.0',
    'disgenet': "CC BY-NC-SA 4.0",
    'do': 'CC0 1.0',
    'drugbank':'CC BY-NC 4.0',
    'drugcentral':"CC BY-SA 4.0",
    'efo':"Apache-2.0",
    'fideo':"CC0 1.0",
    'foodon':'CC BY 4.0',
    'gencc':"CC0 1.0",
    'go':'CC BY 4.0',
    'gwas':"EBI Terms of Use + CC0", #  https://www.ebi.ac.uk/about/terms-of-use/
    'hetionet':'CC0 1.0',
    'hgnc':'CC0 1.0',
    'hippie':"free for academic purposes", # Hippie itself is open source and not protected by any proprietary license. There are some source databases that had some restrictions on commercial usage etc. I think for academic purposes there aren't any restrictions though.
    'hmdb':'CC BY-NC 4.0',
    'hpo':'This service/product uses the Human Phenotype Ontology (v2026-02-16). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well.', #The HPO vocabularies, annotation files, tools and documentation are freely available. The HPO is copyrighted to protect the integrity of the vocabularies, which means that changes to the HPO vocabularies need to be done by HPO developers. However, anyone can download the HPO and use the ontologies or other HPO files under three conditions: That the Human Phenotype Ontology Consortium is acknowledged and cited properly. That any HPO Consortium file(s) displayed publicly include the date(s) and/or version number(s) of the relevant HPO file(s). That neither the content of the HPO file(s) nor the logical relationships embedded within the HPO file(s) be altered in any way. (Content additions and modifications have to be suggested using our issue tracker.) We suggest that you follow standard scientific citation practice if you use the HPO in publications. Users of the HPO should add the following statement to their online presence. This service/product uses the Human Phenotype Ontology (version information). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well.
    'iid':"free for academic purposes", # for academic purposes - it is free to use. For commercial, we can license it through UHN.
    'iptmnet':"CC BY-NC-SA 4.0",
    'kegg': 'Use of all or parts of the material requires reference to the WHO Collaborating Centre for Drug Statistics Methodology. Copying and distribution for commercial purposes is not allowed. Changing or manipulating the material is not allowed.', # Academic users may freely use the KEGG website athttps://www.kegg.jp/or its mirror site at GenomeNethttps://www.genome.jp/kegg/. Academic users who utilize KEGG for providing services are requested to obtain an academic service provider license, which is included in theKEGG FTP academic subscription.
    'markerdb':'CC BY-NC 4.0',
    'medrt':'US government work (VHA), UMLS License Level 0',
    'mirbase':'CC0 1.0',
    'mondo':"CC BY 4.0",
    'ncbi':"https://www.ncbi.nlm.nih.gov/home/about/policies/",
    'ndfrt':'US government work (VHA), UMLS License Level 0',
    'omim':'https://www.omim.org/help/agreement',
    'openfda':'',
    'pathwaycommons':' All of the data provided by Pathway Commons is free! In particular, Pathway Commons distributes pathway information with the intellectual property restrictions of the source database; Only databases that are freely available for academics are included. All of the software that we provide is open-source.',
    'pharmgkb':"CC BY-SA 4.0",
    'pharmebinet':"CC0 1.0",
    'ptmd':"Non-Commercial, Requires Attribution", # found only a license in ptmd v 1 so I think this is the same for 2
    'pubchem':"https://www.ncbi.nlm.nih.gov/home/about/policies/",
    'qptm':"Non-Commercial, Requires Attribution",
    'reactome':"CC0 1.0",
    'refseq':"https://www.ncbi.nlm.nih.gov/home/about/policies/",
    'rnadisease':"Non-Commercial, Requires Attribution",
    'rnainter':"Non-Commercial, Requires Attribution",
    'sider':"CC BY-NC-SA 4.0",
    'smpdb': "Non-Commercial, Requires Attribution",
    'ttd':"Requires Attribution", # No license is required for using TTD data, just citing TTD when publishing your work.
    'uberon':"CC BY 3.0",
    'uniprot':'CC BY 4.0',
    'wikipathways': 'CC BY 3.0'

}


request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/124.0.0.0 Safari/537.36',
}


request_headers_test = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
 }

def get_website_source(url: str) -> str:
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode('utf-8')

def get_website_source_with_playwright(url: str) -> str:
    with sync_playwright() as p:
        # Launch a headless browser (set headless=False if you want to watch it work)
        browser = p.chromium.launch(headless=True, args=["--disable-gpu"])

        # Create a clean browser context
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )

        page = context.new_page()

        try:
            print(f"Opening page: {url}")
            page.goto(url, wait_until="domcontentloaded")

            # Give Cloudflare a few seconds to run its JavaScript and redirect you
            print("Waiting for Cloudflare verification to clear...")
            time.sleep(6)

            # Extract the fully rendered HTML source code
            html_content = page.content()

            return html_content

        except Exception as e:
            print(f"Playwright encountered an error: {e}")
            return None
        finally:
            browser.close()


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
            request = urllib.request.Request(url, headers=request_headers)
            with urllib.request.urlopen(request) as response, open(output_file_path, 'wb') as f:
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


def get_gzip_modified_date(url):
    # Set a header to look like a standard request
    req = urllib.request.Request(url, headers=request_headers)

    # Use HTTP Range header to fetch only the first 10 bytes
    req.add_header("Range", "bytes=0-9")

    try:
        with urllib.request.urlopen(req) as response:
            header_bytes = response.read(10)

            # Ensure we got enough bytes and the file has the correct magic number
            if len(header_bytes) < 10 or header_bytes[0:2] != b"\x1f\x8b":
                return "Error: Not a valid gzip header or insufficient data."

            # Extract the 4-byte MTIME (bytes 4-7) as a little-endian unsigned int
            mtime_bytes = header_bytes[4:8]
            timestamp = struct.unpack("<I", mtime_bytes)[0]

            # A timestamp of 0 means no modification time was set during compression
            if timestamp == 0:
                return "No modification time stored in this gzip file."

            # Convert Unix timestamp to a readable datetime object
            return datetime.datetime.fromtimestamp(timestamp)

    except Exception as e:
        return f"Request failed: {e}"


def parse_msdos_datetime(time_int, date_int):
    # Extract time components from 16-bit integer
    second = (time_int & 0x1F) * 2
    minute = (time_int >> 5) & 0x3F
    hour = (time_int >> 11) & 0x1F

    # Extract date components from 16-bit integer
    day = date_int & 0x1F
    month = (date_int >> 5) & 0x0F
    year = ((date_int >> 9) & 0x7F) + 1980

    # Handle edge cases (e.g., MS-DOS empty timestamps) safely
    try:
        return datetime.datetime(year, month, day, hour, minute, max(0, min(second, 59)))
    except ValueError:
        return None

def peek_zip_modification_datetime(url):
    req = urllib.request.Request(url, headers=request_headers)
    req.add_header("Range", "bytes=0-13")  # Fetch only the first 14 bytes

    try:
        with urllib.request.urlopen(req) as response:
            data = response.read(14)

            if len(data) < 14 or data[0:4] != b"PK\x03\x04":
                return "Error: Not a valid ZIP file header."

            # Unpack bytes 10-11 (time) and 12-13 (date) as Little-Endian unsigned shorts
            time_bytes = data[10:12]
            date_bytes = data[12:14]

            time_int = struct.unpack("<H", time_bytes)[0]
            date_int = struct.unpack("<H", date_bytes)[0]

            return parse_msdos_datetime(time_int, date_int)

    except Exception as e:
        return f"Request failed: {e}"

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


def getOneIDFromUMLSBaseOnAnotherIds(umls_connection, start_ids, start_type, target_type):
    dict_start_id_to_target_ids = {}
    cur = umls_connection.cursor()
    query = ("Select DISTINCT CUI, CODE From MRCONSO Where SAB = '%s' AND CODE in ('%s') ;")
    cuis = "','".join(start_ids)
    query = query % (start_type, cuis)
    rows_counter = cur.execute(query)
    dict_start_id_to_umls_cuis = {}
    if rows_counter > 0:
        for (umls_cui, start_id) in cur:
            add_entry_to_dict_to_set(dict_start_id_to_umls_cuis, start_id, umls_cui)

    if len(dict_start_id_to_umls_cuis) > 0:
        for start_id, set_umls_cuis in dict_start_id_to_umls_cuis.items():
            cur = umls_connection.cursor()
            query = ("Select DISTINCT CODE From MRCONSO Where SAB = '%s' AND CUI in ('%s') ;")
            cuis = "','".join(set_umls_cuis)
            query = query % (target_type, cuis)
            rows_counter = cur.execute(query)
            if rows_counter > 0:
                for (target_id,) in cur:
                    add_entry_to_dict_to_set(dict_start_id_to_target_ids, start_id, target_id)

    return dict_start_id_to_target_ids

def getMeshFromUMLSWithRxCUI(umls_connection, rxcuis:set):
    """
    ge a connection to UMLS database and a list or set of rxcuis. The search in UMLS for UMLS CUIS with this rxcuis.
    The search in UMLS for mesh ids for the given UMLS cuis and return a dictionary of mappings.
    """
    return getOneIDFromUMLSBaseOnAnotherIds(umls_connection, rxcuis, 'RXNORM', 'MSH')


def getRxCUIFromUMLSWithMesh(umls_connection, mesh_ids:set):
    """
    ge a connection to UMLS database and a list or set of rxcuis. The search in UMLS for UMLS CUIS with this rxcuis.
    The search in UMLS for mesh ids for the given UMLS cuis and return a dictionary of mappings.
    """
    return getOneIDFromUMLSBaseOnAnotherIds(umls_connection, mesh_ids, 'MSH', 'RXNORM')

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
