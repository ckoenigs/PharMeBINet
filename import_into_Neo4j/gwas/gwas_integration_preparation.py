from aenum import Enum, NoAlias
import csv, sys
import pharmebinetutils

# aenum bib, because NoAlias allows the use of multiple enums with the same value.


"""
class gwas_study_published_enums(Enum):
    #not sure, if i can use this
    DATE_ADDED_TO_CATALOG = 0
    PUBMEDID = 1
    FIRST_AUTHOR = 2
    DATE = 3
    JOURNAL = 4
    LINK = 5
    STUDY = 6
    DISEASE_TRAIT = 7
    INITIAL_SAMPLE_SIZE = 8
    REPLICATION_SAMPLE_SIZE = 9
    PLATFORM_SNPS_PASSING_QC = 10
    ASSOCIATION_COUNT = 11
    MAPPED_TRAIT = 12
    MAPPED_TRAIT_URI = 13
    STUDY_ACCESSION = 14
    GENOTYPING_TECHNOLOGY = 15
"""


class gwas_associations_enums(Enum):
    """
    Here we have every header of the bigger file. The enumname is the description and not always the exact string value
    of the headers names.
    """

    DATE_ADDED_TO_CATALOG = 0  # Date a study is published in the catalog
    PUBMEDID = 1  # PubMed identification number
    FIRST_AUTHOR = 2  # Last name and initials of first author
    DATE = 3  # Publication date (online (epub) date if available)
    JOURNAL = 4  # Abbreviated journal name
    LINK = 5  # PubMed URL
    STUDY = 6  # Title of paper
    DISEASE_TRAIT = 7  # Disease or trait examined in study
    INITIAL_SAMPLE_SIZE = 8  # Sample size and ancestry description for stage 1 of GWAS (summing across multiple Stage 1 populations, if applicable)
    REPLICATION_SAMPLE_SIZE = 9  # Sample size and ancestry description for subsequent replication(s) (summing across multiple populations, if applicable)
    REGION = 10  # Cytogenetic region associated with rs number
    CHR_ID = 11  # Chromosome number associated with rs number
    CHR_POS = 12  # Chromosomal position associated with rs number
    REPORTED_GENE_S = 13  # Gene(s) reported by author
    MAPPED_GENE = 14  # Gene(s) mapped to the strongest SNP. If the SNP is located within a gene, that gene is listed. If the SNP is located within multiple genes, these genes are listed separated by commas. If the SNP is intergenic, the upstream and downstream genes are listed, separated by a hyphen.
    UPSTREAM_GENE_ID = 15  # Entrez Gene ID for nearest upstream gene to rs number, if not within gene
    DOWNSTREAM_GENE_ID = 16  # Entrez Gene ID for nearest downstream gene to rs number, if not within gene
    SNP_GENE_IDS = 17  # Entrez Gene ID, if rs number within gene; multiple genes denotes overlapping transcripts
    UPSTREAM_GENE_DISTANCE = 18  # distance in kb for nearest upstream gene to rs number, if not within gene
    DOWNSTREAM_GENE_DISTANCE = 19  # distance in kb for nearest downstream gene to rs number, if not within gene
    STRONGEST_SNP_RISK_ALLELE = 20  # SNP(s) most strongly associated with trait + risk allele (? for unknown risk allele). May also refer to a haplotype.
    SNPS = 21  # Strongest SNP; if a haplotype it may include more than one rs number (multiple SNPs comprising the haplotype)
    MERGED = 22  # denotes whether the SNP has been merged into a subsequent rs record (0 = no; 1 = yes;)
    SNP_ID_CURRENT = 23  # current rs number (will differ from strongest SNP when merged = 1)
    CONTEXT = 24  # provides information on a variant’s predicted most severe functional effect from Ensembl
    INTERGENIC = 25  # denotes whether SNP is in intergenic region (0 = no; 1 = yes)
    RISK_ALLELE_FREQUENCY = 26  # Reported risk/effect allele frequency associated with strongest SNP in controls (if not available among all controls, among the control group with the largest sample size). If the associated locus is a haplotype the haplotype frequency will be extracted.
    PVALUE = 27  # Reported p-value for strongest SNP risk allele (linked to dbGaP Association Browser). Note that p-values are rounded to 1 significant digit (for example, a published p-value of 4.8 x 10-7 is rounded to 5 x 10-7).
    PVALUE_MLOG = 28  # -log(p-value)
    PVALUE_TEXT = 29  # Information describing context of p-value (e.g. females, smokers).
    OR_or_BETA = 30  # Reported odds ratio or beta-coefficient associated with strongest SNP risk allele. Note that if an OR <1 is reported this is inverted, along with the reported allele, so that all ORs included in the Catalog are >1. Appropriate unit and increase/decrease are included for beta coefficients.
    CI_95_percent_TEXT = 31  # Reported 95% confidence interval associated with strongest SNP risk allele, along with unit in the case of beta-coefficients. If 95% CIs are not published, we estimate these using the standard error, where available.
    PLATFORM_SNPS_PASSING_QC = 32  # Genotyping platform manufacturer used in Stage 1; also includes notation of pooled DNA study design or imputation of SNPs, where applicable
    CNV = 33  # Study of copy number variation (yes/no)
    # ASSOCIATION COUNT+: Number of associations identified for this study # does not exist
    MAPPED_TRAIT = 34  # Mapped Experimental Factor Ontology trait for this study
    MAPPED_TRAIT_URI = 35  # URI of the EFO trait
    STUDY_ACCESSION = 36  # Accession ID allocated to a GWAS Catalog study
    GENOTYPING_TECHNOLOGY = 37  # Genotyping technology/ies used in this study, with additional array information (ex. Immunochip or Exome array) in brackets.
    # gene_stuff = ["gene_stuff_id","REGION","CHR_ID","CHR_POS","REPORTED_GENES","MAPPED_GENE","UPSTREAM_GENE_ID","DOWNSTREAM_GENE_ID","SNP_GENE_IDS","UPSTREAM_GENE_DISTANCE","DOWNSTREAM_GENE_DISTANCE","STRONGEST_SNP_RISK_ALLELE","SNPS","MERGED","SNP_ID_CURRENT","INTERGENIC","PLATFORM_SNPS_PASSING_QC","CNV"]
    # context = ["context_id", "CONTEXT"]
    # mapped = ["mapped_ID", "MAPPED_TRAIT", "MAPPED_TRAIT_URI"]
    # w_and_stoch_stuff = ["w_and_stoch_stuff_ID","RISK_ALLELE_FREQUENCY","PVALUE","PVALUE_MLOG","P_VALUE_TEXT","OR_or_BETA","CI_95_TEXT"]
    # GENOTYPING_TECHNOLOGY_table = ["GENOTYPING_TECHNOLOGY_id", "GENOTYPING_TECHNOLOGY"]
    # pubmed = ["DATE_ADDED_TO_CATALOG","PUBMEDID","FIRST_AUTHOR","DATE","JOURNAL","LINK","STUDY","DISEASE_TRAIT","INITIAL_SAMPLE_SIZE","REPLICATION_SAMPLE_SIZE","STUDY_ACCESSION"]


class gwas_associations_enums_tables(Enum):
    """
    We have 4 tables: math_stuff, genetic_stuff, DISEASE_TRAIT and PUBMED.
    In this class are the tables (names will maybe changed later) and which values are inside them.
    Additionally there are now the xyz_list lists, containing False, True and (True, "something") values. They will be
    used to know if the values for cypher are not a list (False), a list (True) or a list with some different seperator
    value like ";" ((True, ";")).
    """
    math_stuff = ["math_stuff_table_id", gwas_associations_enums.REPLICATION_SAMPLE_SIZE,
                  gwas_associations_enums.PVALUE_MLOG,
                  gwas_associations_enums.PVALUE, gwas_associations_enums.PLATFORM_SNPS_PASSING_QC,
                  gwas_associations_enums.PVALUE_TEXT, gwas_associations_enums.INITIAL_SAMPLE_SIZE,
                  gwas_associations_enums.CI_95_percent_TEXT, gwas_associations_enums.RISK_ALLELE_FREQUENCY,
                  gwas_associations_enums.OR_or_BETA]
    genetic_stuff = ["genetic_stuff_table_id", gwas_associations_enums.INTERGENIC,
                     gwas_associations_enums.GENOTYPING_TECHNOLOGY,
                     gwas_associations_enums.CHR_ID, gwas_associations_enums.CONTEXT, gwas_associations_enums.REGION,
                     gwas_associations_enums.SNP_ID_CURRENT, gwas_associations_enums.CHR_POS,
                     gwas_associations_enums.SNPS,
                     gwas_associations_enums.STRONGEST_SNP_RISK_ALLELE,
                     gwas_associations_enums.DOWNSTREAM_GENE_DISTANCE,
                     gwas_associations_enums.UPSTREAM_GENE_ID, gwas_associations_enums.DOWNSTREAM_GENE_ID,
                     gwas_associations_enums.UPSTREAM_GENE_ID, gwas_associations_enums.SNP_GENE_IDS,
                     gwas_associations_enums.REPORTED_GENE_S, gwas_associations_enums.MAPPED_GENE,
                     gwas_associations_enums.STUDY_ACCESSION]
    DISEASE_TRAIT = ["disease_traits_table_id", gwas_associations_enums.DISEASE_TRAIT,
                     gwas_associations_enums.MAPPED_TRAIT,
                     gwas_associations_enums.MAPPED_TRAIT_URI]
    PUBMED = ["pubmed_table_id", gwas_associations_enums.PUBMEDID, gwas_associations_enums.FIRST_AUTHOR,
              gwas_associations_enums.DATE,
              gwas_associations_enums.JOURNAL, gwas_associations_enums.LINK, gwas_associations_enums.STUDY,
              gwas_associations_enums.CNV, gwas_associations_enums.DATE_ADDED_TO_CATALOG,
              gwas_associations_enums.MERGED]


class gwas_associations_enums_tables_header(Enum):
    """
    So, of course the name of the headers must be 100 percent identical to the string inside the files.
    """
    math_stuff_updated_header = [
        "new_math_stuff_table_id",  # "math_stuff_table_id",
        "REPLICATION SAMPLE SIZE", "PVALUE_MLOG", "P-VALUE",
        "PLATFORM [SNPS PASSING QC]", "P-VALUE (TEXT)", "INITIAL SAMPLE SIZE", "95% CI (TEXT)", "RISK ALLELE FREQUENCY",
        "OR or BETA"
    ]
    disease_trait_updated_header = [
        "new_disease_traits_table_id",  # "disease_traits_table_id",
        "DISEASE/TRAIT", "MAPPED_TRAIT", "MAPPED_TRAIT_URI"
    ]
    genetic_stuff_updated_header = [
        "new_genetic_stuff_table_id",  # "genetic_stuff_table_id",
        "INTERGENIC", "GENOTYPING TECHNOLOGY", "CHR_ID", "CONTEXT", "REGION", "SNP_ID_CURRENT", "CHR_POS", "SNPS",
        "STRONGEST SNP-RISK ALLELE", "DOWNSTREAM_GENE_DISTANCE", "UPSTREAM_GENE_ID", "DOWNSTREAM_GENE_ID",
        "UPSTREAM_GENE_ID", "SNP_GENE_IDS", "REPORTED GENE(S)", "MAPPED_GENE", "STUDY ACCESSION"
    ]
    pubmed_updated_header = [
        # "pubmed_table_id",
        "PUBMEDID", "FIRST AUTHOR", "DATE", "JOURNAL", "LINK", "STUDY", "CNV", "DATE ADDED TO CATALOG", "MERGED"
    ]


class gwas_associations_enums_tables_updated(Enum):
    """
    We have 4 tables: math_stuff, genetic_stuff, DISEASE_TRAIT and PUBMED.
    In this class are the tables (names will maybe changed later) and which values are inside them.
    Additionally there are now the xyz_list lists, containing False, True and (True, "something") values. They will be
    used to know if the values for cypher are not a list (False), a list (True) or a list with some different seperator
    value like ";" ((True, ";")).
    """
    math_stuff = ["new_math_stuff_table_id", gwas_associations_enums.REPLICATION_SAMPLE_SIZE,
                  gwas_associations_enums.PVALUE_MLOG,
                  gwas_associations_enums.PVALUE, gwas_associations_enums.PLATFORM_SNPS_PASSING_QC,
                  gwas_associations_enums.PVALUE_TEXT, gwas_associations_enums.INITIAL_SAMPLE_SIZE,
                  gwas_associations_enums.CI_95_percent_TEXT, gwas_associations_enums.RISK_ALLELE_FREQUENCY,
                  gwas_associations_enums.OR_or_BETA]
    math_stuff_list = [
        False, True, False, False, False, False, False, False, False, False
    ]
    genetic_stuff = ["new_genetic_stuff_table_id", gwas_associations_enums.INTERGENIC,
                     gwas_associations_enums.GENOTYPING_TECHNOLOGY,
                     gwas_associations_enums.CHR_ID, gwas_associations_enums.CONTEXT, gwas_associations_enums.REGION,
                     gwas_associations_enums.SNP_ID_CURRENT, gwas_associations_enums.CHR_POS,
                     gwas_associations_enums.SNPS,
                     gwas_associations_enums.STRONGEST_SNP_RISK_ALLELE,
                     gwas_associations_enums.DOWNSTREAM_GENE_DISTANCE,
                     gwas_associations_enums.UPSTREAM_GENE_ID, gwas_associations_enums.DOWNSTREAM_GENE_ID,
                     gwas_associations_enums.UPSTREAM_GENE_ID, gwas_associations_enums.SNP_GENE_IDS,
                     gwas_associations_enums.REPORTED_GENE_S, gwas_associations_enums.MAPPED_GENE,
                     gwas_associations_enums.STUDY_ACCESSION]
    genetic_stuff_list = [
        False, False, True, False, (True, ";"), False, (True, ";"), (True, ";"), (True, ";"), (True, ";"), False, False,
        False, False, True, True, True, False
    ]
    DISEASE_TRAIT = ["new_disease_traits_table_id", gwas_associations_enums.DISEASE_TRAIT,
                     gwas_associations_enums.MAPPED_TRAIT,
                     gwas_associations_enums.MAPPED_TRAIT_URI]
    DISEASE_TRAIT_list = [
        False, False, False, False
    ]
    PUBMED = ["PUBMEDID", gwas_associations_enums.FIRST_AUTHOR, gwas_associations_enums.DATE,
              gwas_associations_enums.JOURNAL, gwas_associations_enums.LINK, gwas_associations_enums.STUDY,
              gwas_associations_enums.CNV, gwas_associations_enums.DATE_ADDED_TO_CATALOG,
              gwas_associations_enums.MERGED]
    PUBMED_list = [
        False, False, False, False, False, False, False, True, True
    ]


def csv_file_manager():
    def create_dict(current_table, current_id=0, delimiter="\t"):
        """
        Opens the big gwas file and creates one dictionary with the needed data.
        The data for this function inside gwas_associations_enums_tables class.
        :param current_table:Is one enum.value from gwas_associations_enums_tables. The value is a list. The first
        entry is a string for the name of the id. Every other entry in the list is a gwas_associations_enums enum. In
        this enums is the position of the column, like FIRST_AUTHOR = 2.
        :param current_id: It is the starting id for the new ids, which are needed. Standard value is 0.
        :return: A dictionary with key = str(id+delimiter+value1+delimiter+....) , value = number of entries
        """
        gencc = open(gwas_associations_data, newline='\n')
        gencc_reader = csv.reader(gencc, delimiter=delimiter)
        buffer_dict = {}
        first_round = True
        for spline in gencc_reader:
            buffer = ""
            for value in current_table:
                if type(value) == str:
                    if first_round == True:
                        # the values are the header
                        buffer += str(value).replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_") \
                            .replace("[", "_").replace("]", "_").replace("95%", "ninetyfive_percent").replace("/", "_")
                else:
                    value = value.value
                    buffer += "\t" + str(spline[value])

            if str(current_id - 1) + buffer in buffer_dict.keys():
                pass
            else:
                if first_round == True:
                    first_round = False
                    buffer_dict[buffer] = current_id
                    current_id += 1
                else:
                    buffer_dict[str(current_id) + buffer] = current_id
                    current_id += 1
        gencc.close()
        return buffer_dict

    def write_csv_files(path_and_filename, data_dict, delimiter="\t"):
        """
        Writing a new csv file from one incomming dictionary.
        :param path_and_filename: Path to the file, including the new file name.
        :param data_dict: A dictionary, the key values are the important ones. Every key is a string seperated with
        the delimiter.
        :param delimiter: Should here always be the same, as in the dcitionarys. Standard is "\t"
        :return: Nothing, but creates a file.
        """
        gencc = open(path_and_filename, "w", newline='\n')
        gencc_writer = csv.writer(gencc, delimiter=delimiter)
        first = True
        for key, value in data_dict.items():
            if first == True:
                first = False
                key = key.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_") \
                    .replace("[", "_").replace("]", "_").replace("95%", "ninetyfive_percent").replace("/", "_")
                spline = key.split(delimiter)
            else:
                spline = key.split(delimiter)
            gencc_writer.writerow(spline)
        gencc.close()

    def create_edge_dict(genetic_dict, genetic_table_values, other_dict, other_table_values, delimiter="\t"):
        """
        Uses the original file and the new dictionaries to create a connection between them. The Connection will be
        a new dictionary with str(current_genetic_fid + delimiter + other_id) : number of entries.

        :param genetic_dict: The genetic table is in the center of this database (now it is), so everything is
        connected to this table. Use the dictionary from the create_dict function ... with the same delimiter.
        :param genetic_table_values: Is one enum.value from gwas_associations_enums_tables. The value is a list. The first
        entry is a string for the name of the id. Every other entry in the list is a gwas_associations_enums enum. In
        this enums is the position of the column, like FIRST_AUTHOR = 2.
        :param other_dict: One of the other dicts, not genetic_dict.
        :param other_table_values: The matching table values to the other dict.
        :return: Dictionary with only the matching ids: str(current_genetic_fid + delimiter + other_id) : number of entries
        """
        gencc = open(gwas_associations_data, newline='\n')
        gencc_reader = csv.reader(gencc, delimiter=delimiter)
        first_round_1 = True
        first_round_2 = True
        current_id_genetic = 0
        current_genetic_fid = 0
        current_id_other = 0
        current_id_other_fid = 0
        connection_dict = {}
        connection_dict[str(genetic_table_values[0]) + delimiter + str(other_table_values[0])] = 0
        for spline in gencc_reader:
            buffer_genetic = ""
            buffer_other = ""
            for value in genetic_table_values:
                if type(value) == str:
                    if first_round_1 == True:
                        # the values are the header
                        buffer_genetic += str(value)
                        first_round_1 = False
                else:
                    value = value.value
                    buffer_genetic += "\t" + str(spline[value])
            for value in other_table_values:
                if type(value) == str:
                    if first_round_2 == True:
                        # the values are the header
                        buffer_other += str(value)
                        first_round_2 = False
                else:
                    value = value.value
                    buffer_other += "\t" + str(spline[value])
            if str(current_id_genetic) + buffer_genetic in genetic_dict.keys():
                pass
            else:
                current_id_genetic += 1
                current_genetic_fid = current_id_genetic

            if str(current_id_other) + buffer_other in other_dict.keys():
                pass
            else:
                current_id_other += 1
                current_id_other_fid = current_id_other
            if str(current_genetic_fid) + "\t" + str(current_id_other_fid) in connection_dict.keys():
                connection_dict[str(current_genetic_fid) + "\t" + str(current_id_other_fid)] += 1
            else:
                connection_dict[str(current_genetic_fid) + "\t" + str(current_id_other_fid)] = 1
        gencc.close()
        return connection_dict

    def update_pubmed_csv_file(path_and_filename, key_position, delimiter="\t"):
        gencc = open(path_and_filename, newline='\n')
        gencc_reader = csv.reader(gencc, delimiter=delimiter)
        first_round_1 = True
        updated_dict = {}

        for spline in gencc_reader:
            if first_round_1 == True:
                # header
                first_round_1 = False
                updated_dict[0] = spline
            else:
                if spline[key_position] in updated_dict.keys():
                    buffer = updated_dict[spline[key_position]]
                    for i, value in enumerate(spline):
                        buffer[i].add(value)
                else:
                    buffer = []
                    for value in spline:
                        fuckit = set()
                        fuckit.add(value)
                        buffer.append(fuckit)
                    updated_dict[spline[key_position]] = buffer
                    # every (hopefully) unique id has now a set of values for every entry
        gencc.close()

        gencc = open(path_and_filename.split(".")[0] + "_updated.tsv", "w", newline='\n')
        gencc_writer = csv.writer(gencc, delimiter=delimiter)
        first_round_1 = True
        for key, value in updated_dict.items():
            spline = []
            if first_round_1 == True:
                first_round_1 = False
                gencc_writer.writerow(value)
                continue
            for entry_set in value:
                if type(entry_set) != str:
                    spline.append(",".join([i for i in entry_set]))
                else:
                    spline.append(entry_set)

            gencc_writer.writerow(spline)
        gencc.close()

    def update_uniquetest_csv_file(path_and_filename, key_position, delimiter="\t"):
        """
        Test of uniqueness for the csv files and... if they are not unique, they will be smaller. But currently no idea,
        how to handle the ids in this case. It's a mess.
        :param path_and_filename:
        :param key_position:
        :param delimiter:
        :return:
        """
        gencc = open(path_and_filename, newline='\n')
        gencc_reader = csv.reader(gencc, delimiter=delimiter)
        first_round_1 = True
        updated_dict = {}

        for spline in gencc_reader:
            if first_round_1 == True:
                # header
                first_round_1 = False
                updated_dict[delimiter.join(spline)] = 0
            else:
                buffer = []
                for i, value in enumerate(spline):
                    if i == key_position:
                        continue
                    buffer.append(value)

                if delimiter.join(buffer) in updated_dict.keys():
                    updated_dict[delimiter.join(buffer)].append(spline[key_position])
                else:
                    updated_dict[delimiter.join(buffer)] = [spline[key_position]]
        gencc.close()

        gencc = open(path_and_filename.split(".")[0] + "_updated.tsv", "w", newline='\n')
        gencc_writer = csv.writer(gencc, delimiter=delimiter)
        first_round_1 = True
        new_epic_id = 0
        for key, value in updated_dict.items():
            spline = []
            if first_round_1 == True:
                first_round_1 = False
                key = "new_" + key.split(delimiter)[0] + delimiter + key  # new id for compressing things
                gencc_writer.writerow(key.split(delimiter))
                continue
            new_epic_id += 1
            spline.append(str(new_epic_id))
            spline.append(",".join(value))
            spline.extend(key.split(delimiter))
            gencc_writer.writerow(spline)
        gencc.close()

    def update_edge_csv_files(path_and_filename_first_file, key_tuple_1, path_and_filename_connection,
                              path_and_filename_second_file, key_tuple_2, delimiter="\t"):
        """
        So, this will create an updated version of the connection csv/tsv files, using the new ids.
        :param path_and_filename_first_file: The first file, which id is the first entry in the connection file
        :param key_tuple_1: Something like (position_new_key, position_old_key)
        :param path_and_filename_connection: the file, which will be updated
        :param path_and_filename_second_file: the second file, which id is the second entry in the connetcion file
        :param key_tuple_2: Something like (position_new_key, position_old_key)
        :return: void
        """
        gencc_1 = open(path_and_filename_first_file, newline='\n')
        gencc_reader = csv.reader(gencc_1, delimiter=delimiter)
        first_round = True
        first_dict = {}

        for spline in gencc_reader:
            if first_round == True:
                # header
                first_round = False
                first_dict[0] = (spline[key_tuple_1[0]], spline[key_tuple_1[1]])
            else:
                # dict[old_key] = new_key
                a = str(spline[key_tuple_1[0]])  # new key
                b = str(spline[key_tuple_1[1]]).split(",")  # old keys
                for old_key in b:
                    first_dict[old_key] = a
        gencc_1.close()

        gencc_2 = open(path_and_filename_second_file, newline='\n')
        gencc_reader = csv.reader(gencc_2, delimiter=delimiter)
        first_round = True
        second_dict = {}

        for spline in gencc_reader:
            if first_round == True:
                # header
                first_round = False
                second_dict[0] = (spline[key_tuple_2[0]], spline[key_tuple_2[1]])
            else:
                # dict[old_key] = new_key
                a = str(spline[key_tuple_2[0]])  # new key
                b = str(spline[key_tuple_2[1]]).split(",")  # old keys
                for old_key in b:
                    second_dict[old_key] = a
        gencc_2.close()

        gencc_3 = open(path_and_filename_connection, newline='\n')
        gencc_reader = csv.reader(gencc_3, delimiter=delimiter)
        first_round = True
        connection_dict = {}

        for spline in gencc_reader:
            if first_round == True:
                # header
                first_round = False
                # should be the new names of the new ids
                connection_dict[first_dict[0][0]] = second_dict[0][0]
            else:
                first_new_key = first_dict[
                    spline[0]]  # new dictionary, on the position of the old key to get the new key
                # print(spline)
                second_new_key = second_dict[
                    spline[1]]  # new dictionary, on the position of the old key to get the new key
                connection_dict[first_new_key] = second_new_key
        gencc_3.close()

        gencc = open(path_and_filename_connection.split(".")[0] + "_updated.tsv", "w", newline='\n')
        gencc_writer = csv.writer(gencc, delimiter=delimiter)
        first_round_1 = True
        for key, value in connection_dict.items():
            if first_round == True:
                # header
                first_round = False
                gencc_writer.writerow([key, value])
                continue
            else:
                gencc_writer.writerow([str(key), str(value)])

        gencc.close()

    # get dictionaries with data for the 4 new csv(tsv) files
    genetic_stuff_dict = create_dict(gwas_associations_enums_tables.genetic_stuff.value, 0)
    math_stuff_dict = create_dict(gwas_associations_enums_tables.math_stuff.value, 0)
    PUBMED_dict = create_dict(gwas_associations_enums_tables.PUBMED.value, 0)
    DISEASE_TRAIT_dict = create_dict(gwas_associations_enums_tables.DISEASE_TRAIT.value, 0)

    # csv connection dictis
    genetic_stuff_to_disease_dict = {}
    genetic_stuff_to_math_stuff_dict = {}
    genetic_stuff_to_pubmed_dict = {}

    # Create csv (tsv) files with all the data from the first big file.
    if create_new_csv_files == True:
        write_csv_files(genetic_stuff, genetic_stuff_dict)
        write_csv_files(math_stuff, math_stuff_dict)
        write_csv_files(PUBMED, PUBMED_dict)
        write_csv_files(DISEASE_TRAIT, DISEASE_TRAIT_dict)

    # update csv (tsv) files
    if create_new_csv_files == True:
        update_pubmed_csv_file(PUBMED, 1)
        update_uniquetest_csv_file(DISEASE_TRAIT, 0)
        update_uniquetest_csv_file(math_stuff, 0)
        update_uniquetest_csv_file(genetic_stuff, 0)

    genetic_stuff_to_disease_dict = create_edge_dict(
        genetic_stuff_dict, gwas_associations_enums_tables.genetic_stuff.value,
        DISEASE_TRAIT_dict, gwas_associations_enums_tables.DISEASE_TRAIT.value
    )
    genetic_stuff_to_math_stuff_dict = create_edge_dict(
        genetic_stuff_dict, gwas_associations_enums_tables.genetic_stuff.value,
        math_stuff_dict, gwas_associations_enums_tables.math_stuff.value
    )
    genetic_stuff_to_pubmed_dict = create_edge_dict(
        genetic_stuff_dict, gwas_associations_enums_tables.genetic_stuff.value,
        PUBMED_dict, gwas_associations_enums_tables.PUBMED.value
    )

    if create_new_csv_files == True:
        write_csv_files(genetic_stuff_to_disease, genetic_stuff_to_disease_dict)
        write_csv_files(genetic_stuff_to_math_stuff, genetic_stuff_to_math_stuff_dict)
        write_csv_files(genetic_stuff_to_pubmed, genetic_stuff_to_pubmed_dict)

    # update edge csv/tsv files with new id
    if create_new_csv_files == True:
        update_edge_csv_files(genetic_stuff.split(".")[0] + "_updated.tsv", (0, 1),
                              genetic_stuff_to_disease,
                              DISEASE_TRAIT.split(".")[0] + "_updated.tsv", (0, 1)
                              )
        update_edge_csv_files(genetic_stuff.split(".")[0] + "_updated.tsv", (0, 1),
                              genetic_stuff_to_pubmed,
                              PUBMED.split(".")[0] + "_updated.tsv", (1, 0)
                              )
        update_edge_csv_files(genetic_stuff.split(".")[0] + "_updated.tsv", (0, 1),
                              genetic_stuff_to_math_stuff,
                              math_stuff.split(".")[0] + "_updated.tsv", (0, 1)
                              )
    # path_and_filename_first_file, key_tuple_1 , path_and_filename_connection, path_and_filename_second_file, key_tuple_2

    # Output for checking values
    # i = -5
    # for key, value in math_stuff_dict.items():
    #     print(value, key)
    #     if i == 1:
    #         break
    #     i +=1
    # i = -5
    # print("\n")
    # for key, value in genetic_stuff_dict.items():
    #     print(value, key)
    #     if i == 1:
    #         break
    #     i +=1
    # i = -5
    # print("\n")
    # for key, value in PUBMED_dict.items():
    #     print(value, key)
    #     if i == 1:
    #         break
    #     i +=1
    # i = -5
    # print("\n")
    # for key, value in DISEASE_TRAIT_dict.items():
    #     print(value, key)
    #     if i == 1:
    #         break
    #     i +=1
    # print("\n")

    for dict in [math_stuff_dict, genetic_stuff_dict, PUBMED_dict, DISEASE_TRAIT_dict]:
        # Short Test - if this prints something, it's bad
        header_len = 0
        header = True
        for key, value in dict.items():
            if header == True:
                header = False
                mehmeh = key.split("\t")
                header_len = len(key.split("\t"))
            if len(key.split("\t")) is not header_len:
                meh = key.split("\t")
                print(len(key.split("\t")), header_len)
                print(value, key)
                print(mehmeh)
                print(meh)


def create_gwas_cypher_data_table(header, is_it_a_list, path_to_csv_file, filename, tablename, delimiter="\t"):
    """
    This function creates the cypher text for data tables.
    :param header: A list of the headline (first row) of the csv file.
    :param path_to_csv_file: The path to the folder.
    :param filename: The name of the csv file.
    :param is_it_a_list: A list with the values: True, False or (True, delimiter)
    :return: Cypher command string. Simply input it in a cypher file.
    """

    key = header[0]
    values = header
    print(key, values)

    entrys_query = []
    for i, entry in enumerate(values):
        if i == 0:
            entrys_query.append("{}:line.{}\n".format(entry, entry))
        else:
            if is_it_a_list[i] == True:
                buffer = "{}:split(line.{},'" + "," + "')\n"
            elif is_it_a_list[i] == False:
                buffer = "{}:line.{}\n"
            else:
                buffer = "{}:split(line.{},'" + is_it_a_list[i][1] + "')\n"
            entrys_query.append(buffer.format(entry, entry))
    entry_str = "{" + ",".join(entrys_query) + "}"

    cypher_output_commands = """Create (n:gwas_{} {} )""".format(tablename, entry_str)
    # cypher_output_commands = pharmebinetutils.get_query_import(path_to_csv_file.replace(" ", "%20"), f'{filename}',
    #                                                            cypher_output_commands, delimiter)
    cypher_output_commands = pharmebinetutils.get_query_import(path_of_directory,
                                                               f'import_into_Neo4j/gwas/output/{filename}',
                                                               cypher_output_commands, delimiter)
    cypher_output_commands += pharmebinetutils.prepare_index_query(f'gwas_' + tablename, key)
    return cypher_output_commands


def create_gwas_cypher_links(directory, filename, details_list, delimiter="\t"):
    """
    Creates commands in cypher for edges from csv files.
    :param directory: Base path to file.
    :param filename: File name.
    :param details_list:  A list containing: [connection-csv-file name, name of the first node, name of the second node,
    id name of the first node, id name of the first node inside the connection file, id name of the second node,
    id name of the second node inside the connection file]
    :return: The created cypher command  as a String.
    """
    template = "\n" \
               "MATCH (edge1:{first_table}),(edge2:{second_table})\n" \
               "WHERE edge1.{first_table_id} = line.{name_of_first_table_id_in_csv_file}\n" \
               "AND edge2.{second_table_id} = line.{name_of_second_table_id_in_csv_file}\n" \
               "CREATE (edge1) - [:{merged_table_name}] -> (edge2)"
    new_csv_file_name, first_table, second_table, first_table_id, name_of_first_table_id_in_csv_file, \
        second_table_id, name_of_second_table_id_in_csv_file = details_list

    command = template.format(first_table="gwas_" + str(first_table),
                              second_table="gwas_" + str(second_table),
                              first_table_id=first_table_id,
                              name_of_first_table_id_in_csv_file=name_of_first_table_id_in_csv_file,
                              second_table_id=second_table_id,
                              name_of_second_table_id_in_csv_file=name_of_second_table_id_in_csv_file,
                              merged_table_name="gwas_" + str(first_table) + "_gwas_" + str(second_table)
                              )

    # return pharmebinetutils.get_query_import(directory.replace(" ", "%20"), filename, command, delimiter)
    return pharmebinetutils.get_query_import(path_of_directory, f'import_into_Neo4j/gwas/output/{filename}',
                                             command, delimiter)


##########################
######### Config #########
##########################
if len(sys.argv) > 1:
    path_of_directory = sys.argv[1]
else:
    sys.exit('need a path gwas rela')

# Turn On/Off the creation fo the csv/tsv files.
create_new_csv_files = True

# gwas data (orig_data)
# gwas_associations_data = "C:/Users/Jan-Simon Baasner/Desktop/db_spam/gwas/gwas_catalog_v1.0.2-associations_e109_r2023-03-27.tsv"
gwas_associations_data = "data/gwas_catalog_v1.0.2-associations_e110_r2023-07-20.tsv"

# gwas data (new folder)
# gwas_new = "C:/Users/Jan-Simon Baasner/Desktop/db_spam/gwas_new/"
gwas_new = "output/"

# planed new csv(tsv) files
genetic_stuff = gwas_new + gwas_associations_enums_tables.genetic_stuff.name + ".tsv"
math_stuff = gwas_new + gwas_associations_enums_tables.math_stuff.name + ".tsv"
PUBMED = gwas_new + gwas_associations_enums_tables.PUBMED.name + ".tsv"
DISEASE_TRAIT = gwas_new + gwas_associations_enums_tables.DISEASE_TRAIT.name + ".tsv"

# csv connection csv(tsv) files
genetic_stuff_to_disease = gwas_new + gwas_associations_enums_tables.genetic_stuff.name + "_to_" + \
                           gwas_associations_enums_tables.DISEASE_TRAIT.name + ".tsv"
genetic_stuff_to_math_stuff = gwas_new + gwas_associations_enums_tables.genetic_stuff.name + "_to_" + \
                              gwas_associations_enums_tables.math_stuff.name + ".tsv"
genetic_stuff_to_pubmed = gwas_new + gwas_associations_enums_tables.genetic_stuff.name + "_to_" + \
                          gwas_associations_enums_tables.PUBMED.name + ".tsv"

# cypher_file
# cypher_file_location = "C:/Users/Jan-Simon Baasner/Desktop/db_spam/gwas_new/cypher_gwas"
cypher_file_location = gwas_new + "cypher_gwas"

#########################
######### Start #########
#########################

# Create new csv (files) files
csv_file_manager()

# creating cypher files
# both lambda functions only get a list, mixed of string and enum and return a list of strings(the headers of the table)
cypher_commands = []
get_header_part_2 = lambda x: x if type(x) == str else x.name
get_header = lambda x: list(map(get_header_part_2, x))
test = lambda x: [x]


def hmpf(headerlist):
    buffer = []
    for h in headerlist:
        buffer.append(h.replace(" ", "_").replace("-", "_").replace("(", "_").replace(")", "_")
                      .replace("[", "_").replace("]", "_").replace("95%", "ninetyfive_percent").replace("/", "_"))
    return buffer


# create cypher tables / nodes
header = hmpf(
    gwas_associations_enums_tables_header.genetic_stuff_updated_header.value)  # get_header(gwas_associations_enums_tables_updated.genetic_stuff.value)
tablename = gwas_associations_enums_tables_updated.genetic_stuff.name
cypher_commands.append(create_gwas_cypher_data_table(
    header, gwas_associations_enums_tables_updated.genetic_stuff_list.value, gwas_new,
    gwas_associations_enums_tables_updated.genetic_stuff.name + "_updated" + ".tsv",
    tablename))

header = hmpf(
    gwas_associations_enums_tables_header.math_stuff_updated_header.value)  # get_header(gwas_associations_enums_tables_updated.math_stuff.value)
tablename = gwas_associations_enums_tables_updated.math_stuff.name
cypher_commands.append(create_gwas_cypher_data_table(
    header, gwas_associations_enums_tables_updated.math_stuff_list.value, gwas_new,
    gwas_associations_enums_tables_updated.math_stuff.name + "_updated" + ".tsv",
    tablename))

header = hmpf(
    gwas_associations_enums_tables_header.pubmed_updated_header.value)  # get_header(gwas_associations_enums_tables_updated.PUBMED.value)
tablename = gwas_associations_enums_tables_updated.PUBMED.name
cypher_commands.append(create_gwas_cypher_data_table(
    header, gwas_associations_enums_tables_updated.PUBMED_list.value, gwas_new,
    gwas_associations_enums_tables_updated.PUBMED.name + "_updated" + ".tsv",
    tablename))

header = hmpf(
    gwas_associations_enums_tables_header.disease_trait_updated_header.value)  # get_header(gwas_associations_enums_tables_updated.DISEASE_TRAIT.value)
tablename = gwas_associations_enums_tables_updated.DISEASE_TRAIT.name
cypher_commands.append(create_gwas_cypher_data_table(
    header, gwas_associations_enums_tables_updated.DISEASE_TRAIT_list.value, gwas_new,
    gwas_associations_enums_tables_updated.DISEASE_TRAIT.name + "_updated" + ".tsv",
    tablename))

# writer cypher file

cfile = open(cypher_file_location + '.cypher', "w")
cfile.write("\n".join(cypher_commands))
cfile.close()

cypher_commands = []

# edge table data
g_to_dis = [
    gwas_associations_enums_tables_updated.genetic_stuff.name + "_to_" +
    gwas_associations_enums_tables_updated.DISEASE_TRAIT.name + "_updated" + ".tsv",  # connection-csv-file name
    gwas_associations_enums_tables_updated.genetic_stuff.name,  # name of the first node
    gwas_associations_enums_tables_updated.DISEASE_TRAIT.name,  # name of the second node
    gwas_associations_enums_tables_updated.genetic_stuff.value[0],  # id name of the first node
    gwas_associations_enums_tables_updated.genetic_stuff.value[0],
    # id name of the first node inside the connection file
    gwas_associations_enums_tables_updated.DISEASE_TRAIT.value[0],  # id name of the second node
    gwas_associations_enums_tables_updated.DISEASE_TRAIT.value[0]
    # id name of the second node inside the connection file
]
g_to_mat = [
    gwas_associations_enums_tables_updated.genetic_stuff.name + "_to_" +
    gwas_associations_enums_tables_updated.math_stuff.name + "_updated" + ".tsv",  # connection-csv-file name
    gwas_associations_enums_tables_updated.genetic_stuff.name,  # name of the first node
    gwas_associations_enums_tables_updated.math_stuff.name,  # name of the second node
    gwas_associations_enums_tables_updated.genetic_stuff.value[0],  # id name of the first node
    gwas_associations_enums_tables_updated.genetic_stuff.value[0],
    # id name of the first node inside the connection file
    gwas_associations_enums_tables_updated.math_stuff.value[0],  # id name of the second node
    gwas_associations_enums_tables_updated.math_stuff.value[0]  # id name of the second node inside the connection file
]
g_to_pub = [
    gwas_associations_enums_tables_updated.genetic_stuff.name + "_to_" +
    gwas_associations_enums_tables_updated.PUBMED.name + "_updated" + ".tsv",  # connection-csv-file name
    gwas_associations_enums_tables_updated.genetic_stuff.name,  # name of the first node
    gwas_associations_enums_tables_updated.PUBMED.name,  # name of the second node
    gwas_associations_enums_tables_updated.genetic_stuff.value[0],  # id name of the first node
    gwas_associations_enums_tables_updated.genetic_stuff.value[0],
    # id name of the first node inside the connection file
    gwas_associations_enums_tables_updated.PUBMED.value[0],  # id name of the second node
    gwas_associations_enums_tables_updated.PUBMED.value[0]  # id name of the second node inside the connection file
]
# create cypher edges
cypher_commands.append(create_gwas_cypher_links(gwas_new, g_to_dis[0], g_to_dis))
cypher_commands.append(create_gwas_cypher_links(gwas_new, g_to_mat[0], g_to_mat))
cypher_commands.append(create_gwas_cypher_links(gwas_new, g_to_pub[0], g_to_pub))

# writer cypher file

cfile = open(cypher_file_location + '_edge.cypher', "w")
cfile.write("\n".join(cypher_commands))
cfile.close()

# history

""" some dict test, maybe obsolete
gwas_file = open(gwas_associations_data, "r")

testdict = {}

meh = gwas_file.readlines()
meh = meh [1:]

for line in meh:
    line = line.split("\t")
    try:
        testdict[line[gwas_associations_enums.DISEASE_TRAIT.value],
                 line[gwas_associations_enums.MAPPED_TRAIT.value],
                line[gwas_associations_enums.MAPPED_TRAIT_URI.value]] += 1
    except KeyError:
        testdict[line[gwas_associations_enums.DISEASE_TRAIT.value],
                 line[gwas_associations_enums.MAPPED_TRAIT.value],
                 line[gwas_associations_enums.MAPPED_TRAIT_URI.value]] = 1
print(testdict)
for key, value in testdict.items():
    print (key, "\t", value)

gwas_file.close()
"""
