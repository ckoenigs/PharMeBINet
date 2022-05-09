import csv, datetime, sys
from enum import Enum


# filenames
cypher_file_name = "cypher.cypher"

# variables
cypher_file_data = []

"""
Example Data-row (2022)
In here we have the name of the column between ", a short description, following a ":" and some example value.
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
01: "gene_curie" (HUGO Gene Nomenclature Committee):  	HGNC:10896
02: "gene_symbol":	SKI
03: "disease_curie":	MONDO:0008426
04: "disease_title":	Shprintzen-Goldberg syndrome
05: "disease_original_curie":	OMIM:182212
06: "disease_original_title":	OMIM:182212
07: "classification_curie":	GENCC:100001
08: "classification_title":	Definitive
09: "moi_curie" Multiplicity of infection (MOI):	HP:0000006
10: "moi_title":	Autosomal dominant
11: "submitter_curie":	GENCC:000101
12: "submitter_title":	Ambry Genetics
13: "submitted_as_hgnc_id":	HGNC:10896
14: "submitted_as_hgnc_symbol":	SKI
15: "submitted_as_disease_id":	OMIM:182212
16: "submitted_as_disease_name":	Shprintzen-Goldberg syndrome
17: "submitted_as_moi_id":	HP:0000006
18: "submitted_as_moi_name":	Autosomal dominant inheritance
19: "submitted_as_submitter_id":	GENCC:000101
20: "submitted_as_submitter_name":	Ambry Genetics
21: "submitted_as_classification_id":	GENCC:100001
22: "submitted_as_classification_name":	Definitive
23: "submitted_as_date":	'2018-03-30 13:31:56
24: "submitted_as_public_report_url" urls, if there are any:	
25: "submitted_as_notes" sometimes notes:	
26: "submitted_as_pmids" pmids,sometimes lists seperated by ',' :	 "24939586, 25862627, 27942422"
27: "submitted_as_assertion_criteria_url" sometimes URLS to pdfs, sometimes random stuff: "PMID: 28106320" 
28: "submitted_as_submission_id": "1034" or "000104.pa48.v1.73.hgnc23336.m1.p1"
29: "submitted_run_date":	'2020-12-24
"""


class gencc_enums(Enum):
    # not used at the moment, but maybe useful in the future, so I don't want to delete it
    uuid_0 = 0, "uuid"
    gene_curie_1 = 1, "gene_curie"
    gene_symbol_2 = 2, "gene_symbol"
    disease_curie_3 = 3, "disease_curie"
    disease_title_4 = 4, "disease_title"
    disease_original_curie_5 = 5, "disease_original_curie"
    disease_original_title_6 = 6, "disease_original_title"
    classification_curie_7 = 7, "classification_curie"
    classification_title_8 = 8, "classification_title"
    moi_curie_9 = 9, "moi_curie"
    moi_title_10 = 10, "moi_title"
    submitter_curie_11 = 11, "submitter_curie"
    submitter_title_12 = 12, "submitter_title"
    submitted_as_hgnc_id_13 = 13, "submitted_as_hgnc_id"
    submitted_as_hgnc_symbol_14 = 14, "submitted_as_hgnc_symbol"
    submitted_as_disease_id_15 = 15, "submitted_as_disease_id"
    submitted_as_disease_name_16 = 16, "submitted_as_disease_name"
    submitted_as_moi_id_17 = 17, "submitted_as_moi_id"
    submitted_as_moi_name_18 = 18, "submitted_as_moi_name"
    submitted_as_submitter_id_19 = 19, "submitted_as_submitter_id"
    submitted_as_submitter_name_20 = 20, "submitted_as_submitter_name"
    submitted_as_classification_id_21 = 21, "submitted_as_classification_id"
    submitted_as_classification_name_22 = 22, "submitted_as_classification_name"
    submitted_as_date_23 = 23, "submitted_as_date"
    submitted_as_public_report_url_24 = 24, "submitted_as_public_report_url"
    submitted_as_notes_25 = 25, "submitted_as_notes"
    submitted_as_pmids_26 = 26, "submitted_as_pmids"
    submitted_as_assertion_criteria_url_27 = 27, "submitted_as_assertion_criteria_url"
    submitted_as_submission_id_28 = 28, "submitted_as_submission_id"
    submitted_run_date_29 = 29, "submitted_run_date"

    delimiter_standard = "|"
    delimiter_submitter_title = ","


# data table init
gencc_uuid_dict = {}  # 0 #sort everything for uuid (basically for itself) + other parts with general information
gencc_uuid_dict_unique_keys = set()
gencc_disease_mondo_dict = {}  # 3 # sort everything for mondo (disease_curie)
gencc_disease_mondo_dict_unique_keys = set()
gencc_moi_curie_dict = {}  # 9 #sort everything for moi (moi_curie)
gencc_moi_curie_dict_unique_keys = set()
gencc_sub_hgnc_id = {}  # 13 # sort everything for hgnc id (submitted_as_hgnc_id)
gencc_sub_hgnc_id_unique_keys = set()
gencc_sub_disease_id = {}  # 15 # sort everything for disease id (submitted_as_disease_id)
gencc_sub_disease_id_unique_keys = set()
gencc_gene_curie = {}  # 1,2 sort the curie
gencc_gene_curie_dict_unique_keys = set()

# data table content
"""
gencc_uuid_dict contains: #0, 24,25,26,27
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
24: "submitted_as_public_report_url" urls, if there are any:	
25: "submitted_as_notes" sometimes notes:	
26: "submitted_as_pmids" pmids,sometimes lists seperated by ',' :	 "24939586, 25862627, 27942422"
27: "submitted_as_assertion_criteria_url" sometimes URLS to pdfs, sometimes random stuff: "PMID: 28106320" 

gencc_disease_mondo_dict:  #3, 4, 5, 6, 7, 8
03: "disease_curie":	MONDO:0008426
04: "disease_title":	Shprintzen-Goldberg syndrome
05: "disease_original_curie":	OMIM:182212
06: "disease_original_title":	OMIM:182212
07: "classification_curie":	GENCC:100001
08: "classification_title":	Definitive

gencc_moi_curie_dict: #9, 10, 11, 12
09: "moi_curie" Multiplicity of infection (MOI):	HP:0000006
10: "moi_title":	Autosomal dominant
11: "submitter_curie":	GENCC:000101
12: "submitter_title":	Ambry Genetics

gencc_sub_hgnc_id: #13,14
13: "submitted_as_hgnc_id":	HGNC:10896
14: "submitted_as_hgnc_symbol":	SKI

gencc_sub_disease_id: #15, 16, 17, 18, 19, 20, 21, 22, 23, 28, 29
15: "submitted_as_disease_id":	OMIM:182212
16: "submitted_as_disease_name":	Shprintzen-Goldberg syndrome
17: "submitted_as_moi_id":	HP:0000006
18: "submitted_as_moi_name":	Autosomal dominant inheritance
19: "submitted_as_submitter_id":	GENCC:000101
20: "submitted_as_submitter_name":	Ambry Genetics
21: "submitted_as_classification_id":	GENCC:100001
22: "submitted_as_classification_name":	Definitive
23: "submitted_as_date":	'2018-03-30 13:31:56
28: "submitted_as_submission_id": "1034" or "000104.pa48.v1.73.hgnc23336.m1.p1"
29: "submitted_run_date":	'2020-12-24

gencc_gene_curie:#1, 2
01: "gene_curie" (HUGO Gene Nomenclature Committee):  	HGNC:10896
02: "gene_symbol":	SKI

"""

# Link tables init
gencc_uuid_dict_to_gencc_disease_mondo_dict = {}
gencc_uuid_dict_to_gencc_moi_curie_dict = {}
gencc_uuid_dict_to_gencc_sub_hgnc_id = {}
gencc_uuid_dict_to_gencc_sub_disease_id = {}
gencc_uuid_dict_to_gencc_gene_curie = {}

def prepare_link_table_header():

    # link table header
    gencc_uuid_dict_to_gencc_gene_curie[(gencc_enums.uuid_0.value[1], gencc_enums.gene_curie_1.value[1])] = \
        (gencc_enums.uuid_0.value[1], gencc_enums.gene_curie_1.value[1])
    gencc_uuid_dict_to_gencc_disease_mondo_dict[(gencc_enums.uuid_0.value[1], gencc_enums.disease_curie_3.value[1])] = \
        (gencc_enums.uuid_0.value[1], gencc_enums.disease_curie_3.value[1])
    gencc_uuid_dict_to_gencc_moi_curie_dict[(gencc_enums.uuid_0.value[1], gencc_enums.moi_curie_9.value[1])] = \
        (gencc_enums.uuid_0.value[1], gencc_enums.moi_curie_9.value[1])
    gencc_uuid_dict_to_gencc_sub_hgnc_id[(gencc_enums.uuid_0.value[1], gencc_enums.submitted_as_hgnc_id_13.value[1])] = \
        (gencc_enums.uuid_0.value[1], gencc_enums.submitted_as_hgnc_id_13.value[1])
    gencc_uuid_dict_to_gencc_sub_disease_id[
        (gencc_enums.uuid_0.value[1], gencc_enums.submitted_as_disease_id_15.value[1])] = \
        (gencc_enums.uuid_0.value[1], gencc_enums.submitted_as_disease_id_15.value[1])

# Link table content:
"""
gencc_uuid_dict_to_gencc_disease_mondo_dict:  0, 3
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
03: "disease_curie":	MONDO:0008426

gencc_uuid_dict_to_gencc_moi_curie_dict:  0, 9
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
09: "moi_curie" Multiplicity of infection (MOI):	HP:0000006

gencc_uuid_dict_to_gencc_sub_hgnc_id: 0, 13
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
13: "submitted_as_hgnc_id":	HGNC:10896

gencc_uuid_dict_to_gencc_sub_disease_id: 0, 15
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
15: "submitted_as_disease_id":	OMIM:182212

gencc_uuid_dict_to_gencc_gene_curie: 0 , 1
00: "uuid" ID-stuff, for example: GENCC_000101-HGNC_10896-OMIM_182212-HP_0000006-GENCC_100001
01: "gene_curie" (HUGO Gene Nomenclature Committee):  	HGNC:10896
"""
def run_trough_file_and_prepare_data():
    # where the big gencc file lies
    gencc = open("data/gencc-submissions.csv", newline='\n');
    gencc_reader = csv.reader(gencc)
    # the first row with headlines
    # "uuid","gene_curie","gene_symbol","disease_curie","disease_title","disease_original_curie","disease_original_title","classification_curie","classification_title","moi_curie","moi_title","submitter_curie","submitter_title","submitted_as_hgnc_id","submitted_as_hgnc_symbol","submitted_as_disease_id","submitted_as_disease_name","submitted_as_moi_id","submitted_as_moi_name","submitted_as_submitter_id","submitted_as_submitter_name","submitted_as_classification_id","submitted_as_classification_name","submitted_as_date","submitted_as_public_report_url","submitted_as_notes","submitted_as_pmids","submitted_as_assertion_criteria_url","submitted_as_submission_id","submitted_run_date"


    for i, spline in enumerate(gencc_reader):
        """
        This for-loop uses all data from the gencc_reader (with the one big data file inside) and  puts this data into the 
        link tables and the data tables.
        """

        if i == 0:
            # no header needed
            continue

        for j, checkme in enumerate(spline):
            # '|' is a forbidden symbol in all but one column
            # ',' is a forbiddden symbol in one column
            if j == gencc_enums.submitter_title_12.value[0]:
                if gencc_enums.delimiter_submitter_title.value in checkme:
                    print("Warning: Forbidden ',' in submitter_title column!")
                    print(checkme)
                continue
            if gencc_enums.delimiter_standard.value in checkme:
                print("Warning: Forbidden '|' in column ", j, " !")
                print(checkme)

        # link tables
        gencc_uuid_dict_to_gencc_gene_curie[
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.gene_curie_1.value[0]])] = \
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.gene_curie_1.value[0]])
        gencc_uuid_dict_to_gencc_disease_mondo_dict[
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.disease_curie_3.value[0]])] = \
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.disease_curie_3.value[0]])
        gencc_uuid_dict_to_gencc_moi_curie_dict[
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.moi_curie_9.value[0]])] = \
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.moi_curie_9.value[0]])
        gencc_uuid_dict_to_gencc_sub_hgnc_id[
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.submitted_as_hgnc_id_13.value[0]])] = \
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.submitted_as_hgnc_id_13.value[0]])
        gencc_uuid_dict_to_gencc_sub_disease_id[
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.submitted_as_disease_id_15.value[0]])] = \
            (spline[gencc_enums.uuid_0.value[0]], spline[gencc_enums.submitted_as_disease_id_15.value[0]])

        # data tables

        try:
            gencc_uuid_dict_unique_keys.add(spline[gencc_enums.uuid_0.value[0]])
            gencc_uuid_dict[
                spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_public_report_url_24.value[0]].add(
                spline[gencc_enums.submitted_as_public_report_url_24.value[0]])
            gencc_uuid_dict[spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_notes_25.value[0]].add(
                spline[gencc_enums.submitted_as_notes_25.value[0]])
            for pmid in spline[gencc_enums.submitted_as_pmids_26.value[0]].split(", "):
                gencc_uuid_dict[spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_pmids_26.value[0]].add(
                    pmid)
            gencc_uuid_dict[
                spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_assertion_criteria_url_27.value[0]].add(
                spline[gencc_enums.submitted_as_assertion_criteria_url_27.value[0]])

        except KeyError:
            gencc_uuid_dict[
                spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_public_report_url_24.value[0]] = set()
            gencc_uuid_dict[spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_notes_25.value[0]] = set()
            gencc_uuid_dict[spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_pmids_26.value[0]] = set()
            gencc_uuid_dict[
                spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_assertion_criteria_url_27.value[0]] = set()

            gencc_uuid_dict[
                spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_public_report_url_24.value[0]].add(
                spline[gencc_enums.submitted_as_public_report_url_24.value[0]])
            gencc_uuid_dict[spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_notes_25.value[0]].add(
                spline[gencc_enums.submitted_as_notes_25.value[0]])
            for pmid in spline[gencc_enums.submitted_as_pmids_26.value[0]].split(", "):
                gencc_uuid_dict[spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_pmids_26.value[0]].add(
                    pmid)
            gencc_uuid_dict[
                spline[gencc_enums.uuid_0.value[0]], gencc_enums.submitted_as_assertion_criteria_url_27.value[0]].add(
                spline[gencc_enums.submitted_as_assertion_criteria_url_27.value[0]])

            # print("gencc_uuid_dict\t", spline[0])

        try:
            gencc_gene_curie_dict_unique_keys.add(spline[gencc_enums.gene_curie_1.value[0]])
            gencc_gene_curie[spline[gencc_enums.gene_curie_1.value[0]], gencc_enums.gene_symbol_2.value[0]].add(
                spline[gencc_enums.gene_symbol_2.value[0]])

        except KeyError:
            gencc_gene_curie[spline[gencc_enums.gene_curie_1.value[0]], gencc_enums.gene_symbol_2.value[0]] = set()
            gencc_gene_curie[spline[gencc_enums.gene_curie_1.value[0]], gencc_enums.gene_symbol_2.value[0]].add(
                spline[gencc_enums.gene_symbol_2.value[0]])

            # print("gencc_gene_curie\t", spline[1])

        try:
            gencc_disease_mondo_dict_unique_keys.add(spline[gencc_enums.disease_curie_3.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_title_4.value[0]].add(
                spline[gencc_enums.disease_title_4.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_original_curie_5.value[0]].add(
                spline[gencc_enums.disease_original_curie_5.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_original_title_6.value[0]].add(
                spline[gencc_enums.disease_original_title_6.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.classification_curie_7.value[0]].add(
                spline[gencc_enums.classification_curie_7.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.classification_title_8.value[0]].add(
                spline[gencc_enums.classification_title_8.value[0]])

        except KeyError:
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_title_4.value[0]] = set()
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_original_curie_5.value[0]] = set()
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_original_title_6.value[0]] = set()
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.classification_curie_7.value[0]] = set()
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.classification_title_8.value[0]] = set()

            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_title_4.value[0]].add(
                spline[gencc_enums.disease_title_4.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_original_curie_5.value[0]].add(
                spline[gencc_enums.disease_original_curie_5.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.disease_original_title_6.value[0]].add(
                spline[gencc_enums.disease_original_title_6.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.classification_curie_7.value[0]].add(
                spline[gencc_enums.classification_curie_7.value[0]])
            gencc_disease_mondo_dict[
                spline[gencc_enums.disease_curie_3.value[0]], gencc_enums.classification_title_8.value[0]].add(
                spline[gencc_enums.classification_title_8.value[0]])

            # print("gencc_disease_mondo_dict\t", spline[3])

        try:
            # gencc_moi_curie_dict[spline[9]].update(spline[10:13])
            gencc_moi_curie_dict_unique_keys.add(spline[gencc_enums.moi_curie_9.value[0]])
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.moi_title_10.value[0]].add(
                spline[gencc_enums.moi_title_10.value[0]])
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.submitter_curie_11.value[0]].add(
                spline[gencc_enums.submitter_curie_11.value[0]])
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.submitter_title_12.value[0]].add(
                spline[gencc_enums.submitter_title_12.value[0]])

        except KeyError:
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.moi_title_10.value[0]] = set()
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.submitter_curie_11.value[0]] = set()
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.submitter_title_12.value[0]] = set()

            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.moi_title_10.value[0]].add(
                spline[gencc_enums.moi_title_10.value[0]])
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.submitter_curie_11.value[0]].add(
                spline[gencc_enums.submitter_curie_11.value[0]])
            gencc_moi_curie_dict[spline[gencc_enums.moi_curie_9.value[0]], gencc_enums.submitter_title_12.value[0]].add(
                spline[gencc_enums.submitter_title_12.value[0]])

            # print("gencc_moi_curie_dict\t", spline[9])

        try:
            gencc_sub_hgnc_id_unique_keys.add(spline[gencc_enums.submitted_as_hgnc_id_13.value[0]])
            gencc_sub_hgnc_id[
                spline[gencc_enums.submitted_as_hgnc_id_13.value[0]], gencc_enums.submitted_as_hgnc_symbol_14.value[0]].add(
                spline[gencc_enums.submitted_as_hgnc_symbol_14.value[0]])

        except KeyError:
            gencc_sub_hgnc_id[
                spline[gencc_enums.submitted_as_hgnc_id_13.value[0]], gencc_enums.submitted_as_hgnc_symbol_14.value[
                    0]] = set()
            gencc_sub_hgnc_id[
                spline[gencc_enums.submitted_as_hgnc_id_13.value[0]], gencc_enums.submitted_as_hgnc_symbol_14.value[0]].add(
                spline[gencc_enums.submitted_as_hgnc_symbol_14.value[0]])

            # print("gencc_sub_hgnc_id\t", spline[13])

        try:
            # gencc_sub_disease_id[spline[15]].update(spline[16:24])
            # gencc_sub_disease_id[spline[15]].update(spline[28:])
            gencc_sub_disease_id_unique_keys.add(spline[gencc_enums.submitted_as_disease_id_15.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_disease_name_16.value[
                    0]].add(
                spline[gencc_enums.submitted_as_disease_name_16.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_moi_id_17.value[0]].add(
                spline[gencc_enums.submitted_as_moi_id_17.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_moi_name_18.value[0]].add(
                spline[gencc_enums.submitted_as_moi_name_18.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submitter_id_19.value[
                    0]].add(
                spline[gencc_enums.submitted_as_submitter_id_19.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submitter_name_20.value[
                    0]].add(
                spline[gencc_enums.submitted_as_submitter_name_20.value[0]])
            gencc_sub_disease_id[spline[gencc_enums.submitted_as_disease_id_15.value[0]],
                                 gencc_enums.submitted_as_classification_id_21.value[0]].add(
                spline[gencc_enums.submitted_as_classification_id_21.value[0]])
            gencc_sub_disease_id[spline[gencc_enums.submitted_as_disease_id_15.value[0]],
                                 gencc_enums.submitted_as_classification_name_22.value[0]].add(
                spline[gencc_enums.submitted_as_classification_name_22.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_date_23.value[0]].add(
                spline[gencc_enums.submitted_as_date_23.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submission_id_28.value[
                    0]].add(
                spline[gencc_enums.submitted_as_submission_id_28.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_run_date_29.value[0]].add(
                spline[gencc_enums.submitted_run_date_29.value[0]])

        except KeyError:
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_disease_name_16.value[
                    0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_moi_id_17.value[
                    0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_moi_name_18.value[
                    0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submitter_id_19.value[
                    0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submitter_name_20.value[
                    0]] = set()
            gencc_sub_disease_id[spline[gencc_enums.submitted_as_disease_id_15.value[0]],
                                 gencc_enums.submitted_as_classification_id_21.value[0]] = set()
            gencc_sub_disease_id[spline[gencc_enums.submitted_as_disease_id_15.value[0]],
                                 gencc_enums.submitted_as_classification_name_22.value[0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_date_23.value[0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submission_id_28.value[
                    0]] = set()
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_run_date_29.value[0]] = set()

            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_disease_name_16.value[
                    0]].add(
                spline[gencc_enums.submitted_as_disease_name_16.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_moi_id_17.value[0]].add(
                spline[gencc_enums.submitted_as_moi_id_17.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_moi_name_18.value[0]].add(
                spline[gencc_enums.submitted_as_moi_name_18.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submitter_id_19.value[
                    0]].add(
                spline[gencc_enums.submitted_as_submitter_id_19.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submitter_name_20.value[
                    0]].add(
                spline[gencc_enums.submitted_as_submitter_name_20.value[0]])
            gencc_sub_disease_id[spline[gencc_enums.submitted_as_disease_id_15.value[0]],
                                 gencc_enums.submitted_as_classification_id_21.value[0]].add(
                spline[gencc_enums.submitted_as_classification_id_21.value[0]])
            gencc_sub_disease_id[spline[gencc_enums.submitted_as_disease_id_15.value[0]],
                                 gencc_enums.submitted_as_classification_name_22.value[0]].add(
                spline[gencc_enums.submitted_as_classification_name_22.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_date_23.value[0]].add(
                spline[gencc_enums.submitted_as_date_23.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_as_submission_id_28.value[
                    0]].add(
                spline[gencc_enums.submitted_as_submission_id_28.value[0]])
            gencc_sub_disease_id[
                spline[gencc_enums.submitted_as_disease_id_15.value[0]], gencc_enums.submitted_run_date_29.value[0]].add(
                spline[gencc_enums.submitted_run_date_29.value[0]])

            # print("gencc_sub_disease_id\t", spline[15])

    gencc.close()

# print the length of each data table
print("gencc_uuid_dict\t" + str(len(gencc_uuid_dict.keys())))
print("gencc_disease_mondo_dict\t" + str(len(gencc_disease_mondo_dict.keys())))
print("gencc_moi_curie_dict\t" + str(len(gencc_moi_curie_dict.keys())))
print("gencc_sub_hgnc_id\t" + str(len(gencc_sub_hgnc_id.keys())))
print("gencc_sub_disease_id\t" + str(len(gencc_sub_disease_id.keys())))

# print the length of each link table
print("gencc_uuid_dict_to_gencc_gene_curie", len(gencc_uuid_dict_to_gencc_gene_curie.keys()))
print("gencc_uuid_dict_to_gencc_disease_mondo_dict", len(gencc_uuid_dict_to_gencc_disease_mondo_dict.keys()))
print("gencc_uuid_dict_to_gencc_moi_curie_dict", len(gencc_uuid_dict_to_gencc_moi_curie_dict.keys()))
print("gencc_uuid_dict_to_gencc_sub_hgnc_id", len(gencc_uuid_dict_to_gencc_sub_hgnc_id.keys()))
print("gencc_uuid_dict_to_gencc_sub_disease_id", len(gencc_uuid_dict_to_gencc_sub_disease_id.keys()))


def create_cypher_data_table(header,  path_to_csv_file, filename):
    """
    This function creates the cypher text for data tables.
    :param header: A list of the headline (first row) of the csv file.
    :param path_to_csv_file: The path to the folder.
    :param filename: The name of the csv file.
    :return: Cypher command string. Simply input it in a cypher file.
    """

    # unedited example, can stay here, in case it's needed later
    cypher_output_commands = """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_and_csv_file}.tsv" 
As line FIELDTERMINATOR '\\t' Create (n:{table_name} {entrys} );\n
Create Constraint On (node:{table_name}) Assert node.{unique_id} Is Unique;\n"""

    key = header[0]
    values = header

    print(key, values)

    # this part is needed for splitting the pmid-list. Sometimes there are multiple pmid.
    submitter_title = False
    if filename == "gencc_moi_curie_dict":
        submitter_title = True

    entrys_query = []
    i = 0
    for entry in values:
        i += 1
        if i == 1:
            entrys_query.append("{}:line.{}\n".format(entry, entry))
        else:
            if submitter_title == True:
                if i == 4:
                    # third entry
                    buffer = "{}:split(line.{},'" + gencc_enums.delimiter_submitter_title.value + "')\n"
                    entrys_query.append(buffer.format(entry, entry))
                else:
                    buffer = "{}:split(line.{},'" + gencc_enums.delimiter_standard.value + "')\n"
                    entrys_query.append(buffer.format(entry, entry))
            else:
                buffer = "{}:split(line.{},'" + gencc_enums.delimiter_standard.value + "')\n"
                entrys_query.append(buffer.format(entry, entry))
    entry_str = "{" + ",".join(entrys_query) + "}"

    cypher_output_commands = """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{}.tsv" As line FIELDTERMINATOR '\\t' Create (n:{} {} );\n
Create Constraint On (node:{}) Assert node.{} Is Unique;\n""".format(
        path_to_csv_file + filename, filename, entry_str, filename, key
    )
    return cypher_output_commands


def csv_writer(output_folder_csv_files, filename, keys_set, dict, header, deli_value_list):
    """
    :param output_folder_csv_files: Output folder for the csv files.
    :param filename: The name of the csv files.
    :param keys_set: Set of unique keys.
    :param dict: Dictionary  with all entrys. {key, value}; value == the column
    :param header: All headers for the columns. Otherwise they would be lost in the set or sorting process.
    :param deli_value_list: Some columns have different delimiter.
    :return:
    """
    with open(output_folder_csv_files + filename+'.tsv', "w", newline='') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        keys_unique_sorted = list(keys_set)
        keys_unique_sorted.sort()

        csvWriter.writerow(header)

        for key in keys_unique_sorted:
            writeme = [key]
            for delimiter, value in deli_value_list:
                writeme.append(delimiter.join(dict[key, value]))
            csvWriter.writerow(writeme)


def generate_tsv_and_cypher_query_for_nodes(filename, keys_set, current_dict, header, deli_value_list):
    """
    Prepare csv and cypher query for a node label
    :param filename: string
    :param keys_set: unique properties
    :param current_dict:dictionary with the information
    :param header: First row
    :param deli_value_list: Combination of delimiter and values
    :return:
    """
    csv_writer(output_folder_csv_files, filename, keys_set, current_dict, header, deli_value_list)

    # get cypher commands
    cypher_file_data.append(
        create_cypher_data_table(header, output_folder_csv_files_for_cypher, filename))


def prepare_different_node_tsv_and_cypher_queries():
    ########################
    ### gencc_gene_curie ###
    ########################

    generate_tsv_and_cypher_query_for_nodes("gencc_gene_curie", gencc_gene_curie_dict_unique_keys, gencc_gene_curie,
                                            [gencc_enums.gene_curie_1.value[1], gencc_enums.gene_symbol_2.value[1]],
                                            [(
                                                gencc_enums.delimiter_standard.value,
                                                gencc_enums.gene_symbol_2.value[0])])

    #######################
    ### gencc_uuid_dict ###
    #######################

    generate_tsv_and_cypher_query_for_nodes("gencc_uuid_dict", gencc_uuid_dict_unique_keys, gencc_uuid_dict,
                                            [gencc_enums.uuid_0.value[1],
                                             gencc_enums.submitted_as_public_report_url_24.value[1],
                                             gencc_enums.submitted_as_notes_25.value[1],
                                             gencc_enums.submitted_as_pmids_26.value[1],
                                             gencc_enums.submitted_as_assertion_criteria_url_27.value[1]],
                                            [(
                                                gencc_enums.delimiter_standard.value,
                                                gencc_enums.submitted_as_public_report_url_24.value[
                                                    0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.submitted_as_notes_25.value[
                                                        0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.submitted_as_pmids_26.value[
                                                        0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.submitted_as_assertion_criteria_url_27.value[
                                                        0])])

    ################################
    ### gencc_disease_mondo_dict ###
    ################################

    generate_tsv_and_cypher_query_for_nodes("gencc_disease_mondo_dict", gencc_disease_mondo_dict_unique_keys,
                                            gencc_disease_mondo_dict,
                                            [gencc_enums.disease_curie_3.value[1],
                                             gencc_enums.disease_title_4.value[1],
                                             gencc_enums.disease_original_curie_5.value[1],
                                             gencc_enums.disease_original_title_6.value[1],
                                             gencc_enums.classification_curie_7.value[1],
                                             gencc_enums.classification_title_8.value[1]],
                                            [(
                                                gencc_enums.delimiter_standard.value,
                                                gencc_enums.disease_title_4.value[
                                                    0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.disease_original_curie_5.value[
                                                        0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.disease_original_title_6.value[
                                                        0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.classification_curie_7.value[
                                                        0]),
                                                (
                                                    gencc_enums.delimiter_standard.value,
                                                    gencc_enums.classification_title_8.value[
                                                        0])])

    ############################
    ### gencc_moi_curie_dict ###
    ############################

    generate_tsv_and_cypher_query_for_nodes("gencc_moi_curie_dict", gencc_moi_curie_dict_unique_keys,
                                            gencc_moi_curie_dict,
                                            [gencc_enums.moi_curie_9.value[1],
                                             gencc_enums.moi_title_10.value[1],
                                             gencc_enums.submitter_curie_11.value[1],
                                             gencc_enums.submitter_title_12.value[1]],
                                            [(gencc_enums.delimiter_standard.value, gencc_enums.moi_title_10.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitter_curie_11.value[0]),
                                             (gencc_enums.delimiter_submitter_title.value,
                                              gencc_enums.submitter_title_12.value[0])])

    #########################
    ### gencc_sub_hgnc_id ###
    #########################

    generate_tsv_and_cypher_query_for_nodes("gencc_sub_hgnc_id", gencc_sub_hgnc_id_unique_keys, gencc_sub_hgnc_id,
                                            [gencc_enums.submitted_as_hgnc_id_13.value[1],
                                             gencc_enums.submitted_as_hgnc_symbol_14.value[1]],
                                            [(gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_hgnc_symbol_14.value[0])])

    ############################
    ### gencc_sub_disease_id ###
    ############################

    generate_tsv_and_cypher_query_for_nodes("gencc_sub_disease_id", gencc_sub_disease_id_unique_keys,
                                            gencc_sub_disease_id,
                                            [gencc_enums.submitted_as_disease_id_15.value[1],
                                             gencc_enums.submitted_as_disease_name_16.value[1],
                                             gencc_enums.submitted_as_moi_id_17.value[1],
                                             gencc_enums.submitted_as_moi_name_18.value[1],
                                             gencc_enums.submitted_as_submitter_id_19.value[1],
                                             gencc_enums.submitted_as_submitter_name_20.value[1],
                                             gencc_enums.submitted_as_classification_id_21.value[1],
                                             gencc_enums.submitted_as_classification_name_22.value[1],
                                             gencc_enums.submitted_as_date_23.value[1],
                                             gencc_enums.submitted_as_submission_id_28.value[1],
                                             gencc_enums.submitted_run_date_29.value[1]],
                                            [(gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_disease_name_16.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_moi_id_17.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_moi_name_18.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_submitter_id_19.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_submitter_name_20.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_classification_id_21.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_classification_name_22.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_date_23.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_as_submission_id_28.value[0]),
                                             (gencc_enums.delimiter_standard.value,
                                              gencc_enums.submitted_run_date_29.value[0])])

    # write cypher queries into cypher file
    with open(output_folder_cypher_file + cypher_file_name, 'w') as cypher_file:
        # writes the cypher file
        cypher_file.write("\n\n".join(cypher_file_data))
    print(output_folder_csv_files + cypher_file_name)


def prepare_edge_tsv_files():
    """

    :return:
    """
    # contains a list with tuples: (filenames, dictionaries)
    link_tables = [("gencc_uuid_dict_to_gencc_gene_curie", gencc_uuid_dict_to_gencc_gene_curie),
                   ("gencc_uuid_dict_to_gencc_disease_mondo_dict", gencc_uuid_dict_to_gencc_disease_mondo_dict),
                   ("gencc_uuid_dict_to_gencc_moi_curie_dict", gencc_uuid_dict_to_gencc_moi_curie_dict),
                   ("gencc_uuid_dict_to_gencc_sub_hgnc_id", gencc_uuid_dict_to_gencc_sub_hgnc_id),
                   ("gencc_uuid_dict_to_gencc_sub_disease_id", gencc_uuid_dict_to_gencc_sub_disease_id)]

    # Writes csv-files, when format problems occur check the delimiter and quotechar first
    for filenames, dictis in link_tables:
        with open(output_folder_csv_files + filenames+'.tsv', 'w', newline='') as csvfile:
            csvWriter = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for keys, values in dictis.items():
                # keys and values are identical
                csvWriter.writerow(values)


def create_cypher_link_table(output_folder_csv_files_for_cypher, link_table_file_name, edge_2, edge_1, non_uuid_ID,
                             edge_description):
    """
    This function creates the cypher data of a link table.
    :param output_folder_csv_files_for_cypher: Path to the cypher file. No spaces allowed. Example: gencc_uuid_dict_to_gencc_gene_curie
    :param link_table_file_name: Name of the table. Example: gencc_uuid_dict
    :param edge_1: Name of the first edge. Example: gencc_uuid_dict
    :param edge_2: Name of the second edge. Example: gencc_gene_curie
    :param non_uuid_ID: Name of the column, which is the ID. Example: gene_curie
    :param edge_description: The description of the edge (and most times the file name). Example: gencc_uuid_dict_to_gencc_gene_curie
    :return: Returns the cypher commands as string output.
    """

    cypher_output_commands = """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{}{}.tsv" As line FIELDTERMINATOR '\\t' 
    MATCH (edge1:{}),(edge2:{})
    WHERE edge1.{} = line.{} AND edge2.uuid = line.uuid
    CREATE (edge1) - [:{}] -> (edge2);\n""".format(output_folder_csv_files_for_cypher, link_table_file_name, edge_1,
                                                   edge_2, non_uuid_ID, non_uuid_ID, edge_description)

    # Here we see, what the format command is doing (in here variable names, but the content in reality)
    # """Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/C:/Users/Jan-Simon%20Baasner/Desktop/db_spam/gencc/gencc_uuid_dict_to_gencc_gene_curie" As line FIELDTERMINATOR '\\t'
    # MATCH (edge1:gencc_gene_curie),(edge2:gencc_uuid_dict)
    # WHERE edge1.gene_curie = line.gene_curie AND edge2.uuid = line.uuid
    # CREATE (edge1) - [:edge_description] -> (edge2)
    # """

    return cypher_output_commands


def prepare_edge_cypher_queries():
    """
    Connections: A list of (0,1,2,3,4 ) == 5 elements
    0: File name of the link table
    1: First edge
    2: Second edge
    3: The key-id which is not uuid
    4: The description of the edge
    """
    connections = [("gencc_uuid_dict_to_gencc_gene_curie", "gencc_uuid_dict", "gencc_gene_curie", "gene_curie",
                    "gencc_uuid_dict_to_gencc_gene_curie"),
                   ("gencc_uuid_dict_to_gencc_disease_mondo_dict", "gencc_uuid_dict", "gencc_disease_mondo_dict",
                    "disease_curie", "gencc_uuid_dict_to_gencc_disease_mondo_dict"),
                   ("gencc_uuid_dict_to_gencc_moi_curie_dict", "gencc_uuid_dict", "gencc_moi_curie_dict", "moi_curie",
                    "gencc_uuid_dict_to_gencc_moi_curie_dict"),
                   ("gencc_uuid_dict_to_gencc_sub_hgnc_id", "gencc_uuid_dict", "gencc_sub_hgnc_id",
                    "submitted_as_hgnc_id", "gencc_uuid_dict_to_gencc_sub_hgnc_id"),
                   ("gencc_uuid_dict_to_gencc_sub_disease_id", "gencc_uuid_dict", "gencc_sub_disease_id",
                    "submitted_as_disease_id", "gencc_uuid_dict_to_gencc_sub_disease_id")]

    for name, edge1, edge2, non_uuid_ID, file_name in connections:
        # cypher_file_data = create_cypher_link_table(tuples[0],tuples[1],tuples[2],tuples[3],tuples[4])
        cypher_file_data = create_cypher_link_table(output_folder_csv_files_for_cypher, name, edge1, edge2, non_uuid_ID,
                                                    file_name)
        print(cypher_file_data)
        with open(output_folder_csv_files + cypher_file_name, 'a') as cypher_file:
            # Opens the cypher file with the option 'a', which extends the file.
            cypher_file.write("\n\n".join([cypher_file_data]))
        print(output_folder_csv_files + cypher_file_name + "\t" + name)


def main():
    global path_of_directory, output_folder_csv_files, output_folder_csv_files_for_cypher, output_folder_cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    # output folder
    output_folder_csv_files = "output/"
    output_folder_csv_files_for_cypher = path_of_directory+"import_into_Neo4j/gencc/output/"
    output_folder_cypher_file = "output/"

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('prepare link table header')

    prepare_link_table_header()


    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load gene information')

    run_trough_file_and_prepare_data()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('prepare node tsv and cypher queries')

    prepare_different_node_tsv_and_cypher_queries()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('Prepare edge tsv files')

    prepare_edge_tsv_files()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('prepare edge cypher query')

    prepare_edge_cypher_queries()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
