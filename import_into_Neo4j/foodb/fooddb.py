from collections import defaultdict
import csv, sys
from aenum import Enum, NoAlias

sys.path.append("../..")
import pharmebinetutils

# aenum bib, because NoAlias allows the use of multiple enums with the same value.
# This ist needed, because CompoundAlternateParent and CompoundSubstituent are having the same values

if len(sys.argv) > 1:
    print(sys.argv)
    path_of_directory = sys.argv[1]
else:
    sys.exit('need path')
# Config
orig_food_folder = "data/foodb_2020_4_7_csv/foodb_2020_04_07_csv/"

# the Content.csv file
content_file = orig_food_folder + "Content.csv"
fooddb_content = open(content_file, newline='\n')
# fooddb_reader = csv.reader(fooddb)

# output folder
output_folder_csv_files = "output/"
output_folder_csv_files_for_cypher = "output/"
# "output/"
# output_folder_cypher_file = "C:/Users/Jan-Simon Baasner/Desktop/db_spam/foodb_2020_04_07/"
cypher_file_name = "fooddb_cypher.cypher"
delimiter_standard = ","

# Food.csv
food_file_path = orig_food_folder + "Food.csv"
food_upgrade_path = output_folder_csv_files + "Food.csv"

# Compound.csv
compound_file_path = orig_food_folder + "Compound.csv"
compound_upgrade_path = output_folder_csv_files + "Compound.csv"

# HealthEffect.csv
HealthEffect_file_path = orig_food_folder + "HealthEffect.csv"
HealthEffect_upgrade_path = output_folder_csv_files + "HealthEffect.csv"

# FoodTaxonomy.csv
FoodTaxonomy_file_path = orig_food_folder + "FoodTaxonomy.csv"
FoodTaxonomy_upgrade_path = output_folder_csv_files + "FoodTaxonomy.csv"

# Content Reading and correcting
content_upgrade = output_folder_csv_files + "Content.csv"
c_upgrade = open(content_upgrade, "w")

for line in fooddb_content.readlines():
    # removing escaped quotes
    line = line.replace("\\\"", "\"")
    c_upgrade.write(line)

c_upgrade.close()
fooddb_content.close()


def replace_some_newlines(orig_file, upgrade_file):
    """
    THe function will remove newlines in the previous line, if a line starts with a ", because this is a problem for cypher.
    :param orig_file: The original csv file, which will be changed
    :param upgrade_file: The new csv file, with the updates included
    :return:
    """
    orig_file = open(orig_file, "r")
    upgrade_file = open(upgrade_file, "w")

    all_lines = orig_file.readlines()
    orig_file.close()
    all_len = len(all_lines)
    for i, line in enumerate(all_lines):
        # there is a Problem, when a line starts with ", so when the next line starts with " the "\n" will be removed
        if i + 1 < all_len - 1 and all_lines[i + 1].startswith('"'):
            upgrade_file.write(line.replace("\n", ""))
        else:
            upgrade_file.write(line)
    upgrade_file.close()


replace_some_newlines(food_file_path, food_upgrade_path)
replace_some_newlines(compound_file_path, compound_upgrade_path)
replace_some_newlines(HealthEffect_file_path, HealthEffect_upgrade_path)


def replace_some_quotes(orig_FoodTaxonomy, upgrade_FoodTaxonomy):
    """
    The function will remove quotes in the csv file, because after that it can be used as an ID.
    :param orig_file: The original csv file, which will be changed
    :param upgrade_file: The new csv file, with the updates included
    """
    orig_file = open(orig_FoodTaxonomy, "r")
    upgrade_file = open(upgrade_FoodTaxonomy, "w")

    all_lines = orig_file.readlines()
    orig_file.close()
    for i, line in enumerate(all_lines):
        upgrade_file.write(line.replace('\"\"\"', ""))
    upgrade_file.close()


replace_some_quotes(FoodTaxonomy_file_path, FoodTaxonomy_upgrade_path)


class fooddb_table_enums(Enum):
    """
    In this enum class are all normal node-names and all associated headers in the form of:
    Nodename = ["header1", "header2", ....]
    The name of the nodes are identical to the csv-files and the name of the headers are identical to the headers of the
    associated files.
    Empty files were removed from this class.
    """
    _settings_ = NoAlias

    AccessionNumber = ["id", "number", "compound_id", "created_at", "updated_at", "source_id", "source_type"]
    Compound = ["id", "public_id", "name", "moldb_iupac", "state", "annotation_quality", "description", "cas_number",
                "moldb_inchikey", "moldb_inchi", "moldb_smiles", "moldb_mono_mass", "kingdom", "superklass", "klass",
                "subklass"]
    CompoundAlternateParent = ["id", "name", "compound_id", "creator_id", "updater_id", "created_at", "updated_at"]
    CompoundSubstituent = ['id', 'name', 'compound_id', 'creator_id', 'updater_id', 'created_at', 'updated_at']
    CompoundExternalDescriptor = ["id", "external_id", "annotations", "compound_id", "creator_id", "updater_id",
                                  "created_at", "updated_at"]
    CompoundSynonym = ['id', 'synonym', 'synonym_source', 'created_at', 'updated_at', 'source_id', 'source_type']
    Content = ['id', 'source_id', 'source_type', 'food_id', 'orig_food_id', 'orig_food_common_name',
               'orig_food_scientific_name', 'orig_food_part', 'orig_source_id', 'orig_source_name',
               'orig_content', 'orig_min', 'orig_max', 'orig_unit', 'orig_citation', 'citation', 'citation_type',
               'creator_id', 'updater_id', 'created_at', 'updated_at', 'orig_method', 'orig_unit_expression',
               'standard_content', 'preparation_type', 'export']
    Enzyme = ['id', 'name', 'gene_name', 'description', 'go_classification', 'general_function', 'specific_function',
              'pathway', 'reaction', 'cellular_location', 'signals', 'transmembrane_regions', 'molecular_weight',
              'theoretical_pi', 'locus', 'chromosome', 'uniprot_name', 'uniprot_id', 'pdb_id', 'genbank_protein_id',
              'genbank_gene_id', 'genecard_id', 'genatlas_id', 'hgnc_id', 'hprd_id', 'organism', 'general_citations',
              'comments', 'creator_id', 'updater_id', 'created_at', 'updated_at']
    Flavor = ['id', 'name', 'flavor_group', 'category', 'created_at', 'updated_at', 'creator_id', 'updater_id']
    Food = ['id', 'name', 'name_scientific', 'description', 'itis_id', 'wikipedia_id', 'picture_file_name',
            'picture_content_type', 'picture_file_size', 'picture_updated_at', 'legacy_id', 'food_group',
            'food_subgroup', 'food_type', 'created_at', 'updated_at', 'creator_id', 'updater_id', 'export_to_afcdb',
            'category', 'ncbi_taxonomy_id', 'export_to_foodb', 'public_id']
    HealthEffect = ['id', 'name', 'description', 'chebi_name', 'chebi_id', 'created_at', 'updated_at', 'creator_id',
                    'updater_id', 'chebi_definition']
    NcbiTaxonomyMap = ['id', 'TaxonomyName', 'Rank', 'created_at', 'updated_at']
    Nutrient = ['id', 'legacy_id', 'type', 'public_id', 'name', 'export', 'state', 'annotation_quality', 'description',
                'wikipedia_id', 'comments', 'dfc_id', 'duke_id', 'eafus_id', 'dfc_name', 'compound_source',
                'metabolism', 'synthesis_citations', 'general_citations', 'creator_id', 'updater_id', 'created_at',
                'updated_at']
    OntologySynonym = ['id', 'ontology_term_id', 'synonym', 'external_id', 'external_srouce', 'parent_id',
                       'parent_source', 'comment', 'curator', 'created_at', 'updated_at']
    OntologyTerm = ['id', 'term', 'definition', 'external_id', 'external_source', 'comment', 'curator', 'parent_id',
                    'level', 'created_at', 'updated_at', 'legacy_id']
    Pathway = ['id', 'smpdb_id', 'kegg_map_id', 'name', 'created_at', 'updated_at']
    Reference = ['id', 'ref_type', 'text', 'pubmed_id', 'link', 'title', 'creator_id', 'updater_id', 'created_at',
                 'updated_at', 'source_id', 'source_type']


class fooddb_enum_edge_tables(Enum):
    """
    In this class are only the connections (edges) between tables (nodes). The name of each enum is the name for the
    csv file and (the part of) the name for the edges.
    The values have the format of a list with two lists inside: [["","",...],["","",..]]
    The first list contains the header information of the csv file: [header-0,header-1,header-2,...]
    the second list hast the values:["table1", "table2", "table1_id", "table1_id_in_csv", "table2_id", "table2_id_in_csv"]
    """
    #
    CompoundOntologyTerm = [["id", "compound_id", "export", "ontology_term_id", "created_at", "updated_at",
                             "OntologyTerm"],
                            ["Compound", "OntologyTerm", "id", "compound_id", "id", "ontology_term_id"]]
    CompoundsEnzyme = [["id", "compound_id", "enzyme_id", "citations", "created_at", "updated_at", "creator_id",
                        "updater_id", "Enzyme"], ["Compound", "Enzyme", "id", "compound_id", "id", "enzyme_id"]]
    CompoundsFlavor = [["id", "compound_id", "flavor_id", "citations", "created_at", "updated_at", "creator_id",
                        "updater_id", "source_id", "source_type", "Flavor"],
                       ["Compound", "Flavor", "id", "compound_id", "id", "flavor_id"]]
    CompoundsHealthEffect = [["id", "compound_id", "health_effect_id", "orig_health_effect_name", "orig_compound_name",
                              "orig_citation", "citation", "citation_type", "created_at", "updated_at", "creator_id",
                              "updater_id", "source_id", "source_type", "HealthEffect"],
                             ["Compound", "HealthEffect", "id", "compound_id", "id", "health_effect_id"]]
    CompoundsPathway = [["id", "compound_id", "pathway_id", "creator_id", "updater_id", "created_at", "updated_at",
                         "Pathway"], ["Compound", "Pathway", "id", "compound_id", "id", "pathway_id"]]
    FoodTaxonomy = [['id', 'food_id', 'ncbi_taxonomy_id', 'classification_name', 'classification_order', 'created_at',
                     'updated_at'], ["Food", "NcbiTaxonomyMap", "id", "food_id", "id", "classification_order"]]


def create_edge_tables(header, table_name, ids_and_more):
    """
    This function creates a cycpher statement for special tables, which data will be saved inside edges.
    -> The information will be inside an edge, not inside a node.
    :param header: A list of the names of the header from the csv file. Must be in the correct order.
    :param table_name: The name of the table (csv file).
    :param ids_and_more: A list, containing: ["table1-name", "table2-name", "table1_id", "table1_id_in_csv",
    "table2_id", "table2_id_in_csv"]
    :return: A cypher string for with MATCH, WHERE, CREATE for the incomming data.
    """
    values = header[:len(header) - 1]
    entrys_query = []
    for entry in values:
        if "id" in entry:
            entrys_query.append("{}:line.{}\n".format(entry, entry))
        else:
            buffer = "{}:split(line.{},'" + delimiter_standard + "')\n"
            entrys_query.append(buffer.format(entry, entry))
    entry_str = "{" + ",".join(entrys_query) + "}"
    print(entry_str)
    template = "\n" \
              "MATCH (edge1:{table1}),(edge2:{table2})\n" \
              "WHERE edge1.{table1_id} = line.{table1_id_in_csv} AND edge2.{table2_id} = line.{table2_id_in_csv}\n" \
              "CREATE (edge1) - [:{link_name}{data_stuff}] -> (edge2)"
    buffer = template.format(
        table1="foodb_" + ids_and_more[0],
        table2="foodb_" + ids_and_more[1],
        table1_id=ids_and_more[2],
        table1_id_in_csv=ids_and_more[3],
        table2_id=ids_and_more[4],
        table2_id_in_csv=ids_and_more[5],
        link_name="foodb_" + table_name,
        data_stuff=entry_str
    )
    return buffer


class links_2(Enum):
    """
    Here is the data for the creation of new csv-files. The planed files containing only the id-to-id-connection.
    The reason for these files: neo4j will crash without, too much work.
    Each enum contains the values: ["old_filename", "new_filename", "id-1-name", "id-1-Position", "id-2-name",
                                    "id-2-Position"]
    """
    Compound_AccessionNumber = ["AccessionNumber", "Compound_AccessionNumber", "id", 0, "compound_id", 2]
    Compound_CompoundSynonym = ["CompoundSynonym", "Compound_CompoundSynonym", "id", 0, "source_id", 5]
    Compound_CompoundAlternateParent = ["CompoundAlternateParent", "Compound_CompoundAlternateParent", "id", 0,
                                        "compound_id", 2]
    Compound_CompoundExternalDescriptor = ["CompoundExternalDescriptor", "Compound_CompoundExternalDescriptor", "id", 0,
                                           "compound_id", 3]
    Compound_CompoundSubstituent = ["CompoundSubstituent", "Compound_CompoundSubstituent", "id", 0, "compound_id", 2]
    Content_WHERE_Nutrient = ["Content", "Content_Nutrient", "id", 0, "source_id", 1]
    Food_Content = ["Content", "Food_Content", "id", 0, "food_id", 3]
    Food_FoodTaxonomy = ["FoodTaxonomy", "Food_FoodTaxonomy", "id", 0, "food_id", 1]
    NcbiTaxonomyMap_FoodTaxonomy = ["FoodTaxonomy", "NcbiTaxonomyMap_FoodTaxonomy", "id", 0, "classification_order", 4]
    OntologyTerm_OntologySynonym = ["OntologySynonym", "OntologyTerm_OntologySynonym", "id", 0, "ontology_term_id", 1]
    Content_WHERE_Compound = ["Content", "Content_Compound", "id", 0, "food_id", 3]


class new_csv_link_tables(Enum):
    """
    The enums here having the values [new_csv_file_name, first_table, second_table, first_table_id,
            name_of_first_table_id_in_csv_file, second_table_id, name_of_second_table_id_in_csv_file]
    """
    Compound_AccessionNumber = ["Compound_AccessionNumber", "Compound", "AccessionNumber", "id", "compound_id", "id",
                                "id"]
    Compound_CompoundAlternateParent = ["Compound_CompoundAlternateParent", "Compound", "CompoundAlternateParent", "id",
                                        "compound_id", "id", "id"]
    Compound_CompoundExternalDescriptor = ["Compound_CompoundExternalDescriptor", "Compound",
                                           "CompoundExternalDescriptor", "id", "compound_id", "id", "id"]
    Compound_CompoundSubstituent = ["Compound_CompoundSubstituent", "Compound", "CompoundSubstituent", "id",
                                    "compound_id", "id", "id"]
    Compound_CompoundSynonym = ["Compound_CompoundSynonym", "Compound", "CompoundSynonym", "id", "id", "id",
                                "source_id"]
    Content_WHERE_Compound = ["Content_Compound", "Compound", "Content", "id", "id", "id", "food_id"]
    Food_Content = ["Food_Content", "Food", "Content", "id", "food_id", "id", "id"]
    Content_WHERE_Nutrient = ["Content_Nutrient", "Content", "Nutrient", "id", "id", "id", "source_id"]
    OntologyTerm_OntologySynonym = ["OntologyTerm_OntologySynonym", "OntologyTerm", "OntologySynonym", "id",
                                    "ontology_term_id", "id", "id"]


def create_fooddb_cypher_data_table(header, path_to_csv_file, filename, tablename):
    """
    This function creates the cypher text for data tables.
    :param header: A list of the headline (first row) of the csv file.
    :param path_to_csv_file: The path to the folder.
    :param filename: The name of the csv file.
    :return: Cypher command string. Simply input it in a cypher file.
    """

    key = header[0]
    values = header
    print(key, values)

    entrys_query = []
    i = 0
    for entry in values:
        i += 1
        if i == 1 or "id" in entry:
            entrys_query.append("{}:line.{}\n".format(entry, entry))
        else:
            buffer = "{}:split(line.{},'" + delimiter_standard + "')\n"
            entrys_query.append(buffer.format(entry, entry))
    entry_str = "{" + ",".join(entrys_query) + "}"

    cypher_output_commands = """Create (n:foodb_{} {} )""".format(tablename, entry_str)
    cypher_output_commands = pharmebinetutils.get_query_import(path_of_directory, f'{filename}',
                                                               cypher_output_commands, ',')
    cypher_output_commands += pharmebinetutils.prepare_index_query(f'foodb_' + tablename, key)
    return cypher_output_commands


def create_link_csv_files(orig_data_file_location, new_data_file_location):
    """
    Creates csv files.
    :param orig_data_file_location: The original location of csv files (folder).
    :param new_data_file_location: The location of the new csv files (folder).
    """
    for link_table in links_2:
        # Every entry of this enum class has the values:
        # ["old_filename", "new_filename", "id-1-name", "id-2-Position", "id-2-name", "id-2-Position"]
        print(link_table, link_table.value)
        old_filename, new_filename, table1_id, table1_id_position, table2_id, table2_id_position = link_table.value
        file1 = open(orig_data_file_location + old_filename + ".csv", newline='\n')
        file1_data = csv.reader(file1)
        table1_table2_file = open(new_data_file_location + new_filename + ".csv", "w")
        connection_list_t1 = []
        for spline in file1_data:
            if "WHERE" in link_table.name:
                if "Nutrient" in link_table.name:
                    connection_list_t1.append(
                        spline[table1_id_position] + delimiter_standard + spline[table2_id_position] + "\n")
                elif spline[2] == "Compound":
                    connection_list_t1.append(
                        spline[table1_id_position] + delimiter_standard + spline[table2_id_position] + "\n")
                else:
                    connection_list_t1.append(
                        spline[table1_id_position] + delimiter_standard + spline[table2_id_position] + "\n")

            else:
                connection_list_t1.append(
                    spline[table1_id_position] + delimiter_standard + spline[table2_id_position] + "\n")
        table1_table2_file.writelines(connection_list_t1)
        table1_table2_file.close()
        file1.close()


create_link_csv_files(orig_food_folder, output_folder_csv_files)


def use_new_csv_files(path_of_directory, orig_path):
    """
    Creates commands in cypher for edges from csv files.
    :param path_of_directory: Base path.
    :param orig_path: File path.
    :return: The created commands (for all enums in new_csv_link_tables) as a String.
    """
    cypher_output_commands = ""
    template = "\n" \
               "MATCH (edge1:{first_table}),(edge2:{second_table})\n" \
               "WHERE edge1.{first_table_id} = line.{name_of_first_table_id_in_csv_file}\n" \
               "AND edge2.{second_table_id} = line.{name_of_second_table_id_in_csv_file}\n" \
               "CREATE (edge1) - [:{merged_table_name}] -> (edge2)"
    for enum in new_csv_link_tables:
        new_csv_file_name, first_table, second_table, first_table_id, name_of_first_table_id_in_csv_file, \
            second_table_id, name_of_second_table_id_in_csv_file = enum.value

        command = template.format(first_table="foodb_" + str(first_table),
                                  second_table="foodb_" + str(second_table),
                                  first_table_id=first_table_id,
                                  name_of_first_table_id_in_csv_file=name_of_first_table_id_in_csv_file,
                                  second_table_id=second_table_id,
                                  name_of_second_table_id_in_csv_file=name_of_second_table_id_in_csv_file,
                                  merged_table_name="foodb_" + str(first_table) + "_foodb_" + str(second_table)
                                  )

        path = path_of_directory
        cypher_output_commands += pharmebinetutils.get_query_import(path,
                                                                    "import_into_Neo4j/foodb/" + orig_path + new_csv_file_name + ".csv",
                                                                    command,
                                                                    delimiter_standard)
        cypher_output_commands += "\n"

    return cypher_output_commands


# Creating the first part of the cypher file.
# Data tables and the IDs.
cypher_file_data = []

for enums in fooddb_table_enums:
    header = []
    for evalue in enums.value:
        header.append(evalue)
    if enums.name not in ["Food", "Compound", "HealthEffect", "FoodTaxonomy", "Content"]:
        cypher_file_data.append(create_fooddb_cypher_data_table(header,
                                                                output_folder_csv_files_for_cypher,
                                                                "import_into_Neo4j/foodb/" + orig_food_folder + enums.name + ".csv",
                                                                enums.name))
    else:
        cypher_file_data.append(create_fooddb_cypher_data_table(header,
                                                                output_folder_csv_files_for_cypher,
                                                                "import_into_Neo4j/foodb/" + output_folder_csv_files_for_cypher + enums.name + ".csv",
                                                                enums.name))

for enums in fooddb_enum_edge_tables:
    header = []
    ids_and_more = []
    for evalue in enums.value[0]:
        header.append(evalue)
    for id in enums.value[1]:
        ids_and_more.append(id)
    erg = create_edge_tables(header, enums.name, ids_and_more)
    erg = pharmebinetutils.get_query_import(path_of_directory,
                                            f'import_into_Neo4j/foodb/{orig_food_folder}{enums.name}.csv',
                                            erg, ',')
    cypher_file_data.append(erg)

cypher_file_data.append(use_new_csv_files(path_of_directory.replace(" ", "%20"), output_folder_csv_files_for_cypher))

# Creating a new cyhper file and write the entire cypher file data.
with open(output_folder_csv_files + cypher_file_name, 'w') as cypher_file:
    cypher_file.write("\n\n".join(cypher_file_data))
