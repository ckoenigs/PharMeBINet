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

request_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                  'Chrome/35.0.1916.47 Safari/537.36'
}

dict_source_to_license = {
    'adrecs': 'CC BY-NC-SA 4.0',
    'aeolus': 'CC0 1.0',
    'bindingdb':'CC BY 3.0 US Deed',
    'biogrid':'The MIT License',
    'chebi':'CC BY 4.0',
    'cl':'CC BY 4.0',
    'clinvar':'https://www.ncbi.nlm.nih.gov/home/about/policies/',
    'ctd':"© 2002–2012 MDI Biological Laboratory. © 2012–2026 NC State University. All rights reserved.",
    'dbsnp':'https://www.ncbi.nlm.nih.gov/home/about/policies/',
    'ddinter':'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International',
    'diseases': 'CC BY 4.0 Deed',
    'disgenet': "Attribution-NonCommercial-ShareAlike 4.0 International License",
    'do': 'CC0 1.0 Universal',
    'drugbank':'Attribution-NonCommercial 4.0 International',
    'drugcentral':"Creative Commons Attribution-ShareAlike 4.0 International Public License",
    'efo':"Apache-2.0",
    'fideo':"CC-BY 4.0",
    'foodon':'CC BY 4.0',
    'gencc':"CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
    'go':'CC BY 4.0',
    'gwas':"CC BY-NC 4.0 Deed",
    'hetionet':'CC0',
    'hgnc':'CC0',
    'hippie':"free to use for academic purposes",
    'hmdb':'Creative Commons (CC) Attribution-NonCommercial (NC) 4.0 International Licensing',
    'hpo':'This service/product uses the Human Phenotype Ontology (v2026-02-16). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well.',
    'iid':"free to use for academic purposes",
    'iptmnet':"CC BY-NC-SA 4.0 Deed",
    'kegg': 'Use of all or parts of the material requires reference to the WHO Collaborating Centre for Drug Statistics Methodology. Copying and distribution for commercial purposes is not allowed. Changing or manipulating the material is not allowed.',
    'markerdb':'Attribution-NonCommercial 4.0 International CC BY-NC 4.0 Deed',
    'medrt':'UMLS license, available at https://uts.nlm.nih.gov/license.html',
    'mirbase':'CC0 with attribution',
    'mondo':"CC-BY-SA 3.0",
    'ncbi':"https://www.ncbi.nlm.nih.gov/home/about/policies/",
    'ndfrt':'UMLS license, available at https://uts.nlm.nih.gov/license.html',
    'omim':'https://www.omim.org/help/agreement',
    'openfda':'',
    'pathwaycommons':' All of the data provided by Pathway Commons is free! In particular, Pathway Commons distributes pathway information with the intellectual property restrictions of the source database; Only databases that are freely available for academics are included. All of the software that we provide is open-source.',
    'pharmgkb':"CC BY-SA 4.0",
    'pharmebinet':"CC0 1.0",
    'ptmd':"ONLY freely available for academic research",
    'pubchem':"https://www.ncbi.nlm.nih.gov/home/about/policies/",
    'qptm':"ONLY freely available for academic research",
    'reactome':"CC BY-SA 4.0",
    'refseq':"https://www.ncbi.nlm.nih.gov/home/about/policies/",
    'rnadisease':"Provide data for non-commercial use, distribution, or reproduction in any medium, only if you properly cite the original work.",
    'rnainter':"Provide data for non-commercial use, distribution, or reproduction in any medium, only if you properly cite the original work.",
    'sider':"CC BY-NC-SA 4.0",
    'smpdb': "SMPDB is offered to the public as a freely available resource. Use and re-distribution of the data, in whole or in part, for commercial purposes requires explicit permission of the authors and explicit acknowledgment of the source material (SMPDB) and the original publication",
    'ttd':"No license",
    'uberon':"CC BY 3.0",
    'uniprot':'CC BY 4.0',
    'wikipathways': 'CC BY 3.0'

}

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
