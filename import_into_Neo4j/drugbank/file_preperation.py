# this file go through all csv,fasta and sdf filed from the DrugBank download site and test  if the information are already
# in the xml file or not. Also if some information are not included then they are combinded withe the other files.

import sys, io
import os, csv
from Bio import SeqIO
from itertools import groupby
import datetime, time
from py2neo import Graph, authenticate
import subprocess

# encoding=utf8
reload(sys)
sys.setdefaultencoding('utf8')

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# increase the csv max size
maxInt = sys.maxsize
decrement = True

# drugbank license
drugbank_license = "Creative Common's Attribution-NonCommercial 4.0 International License"

while decrement:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt / 10)
        decrement = True


def fasta_iter(fasta_name):
    """
    given a fasta file. yield tuples of header, sequence
    """
    fh = open(fasta_name)
    # ditch the boolean (x[0]) and just keep the header or sequence since
    # we know they alternate.
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header = header.next()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.next())
        yield header, seq


# only when all arguments are their continue
if len(sys.argv) != 7:
    print(
        '1 to the directory with all drugbank information \n 2 to drug sequence \n 3 to external links \n 4 to protein identifier \n 4 to structure \n 5 to target sequence \n')
    print(len(sys.argv))
    for element in sys.argv:
        print(element)
    sys.exit()
whole_path = sys.argv[1]
path_to_drug_sequences = whole_path + sys.argv[2]
path_to_external_links = whole_path + sys.argv[3]
path_to_protein_identifier = whole_path + sys.argv[4]
path_to_structure = whole_path + sys.argv[5]
path_to_target_sequence = whole_path + sys.argv[6]
path_prepared_drugbank_files = 'drugbank/'

cypher_file = open('output/cypher_file.cypher', 'w')
cypher_rela_file = open('output/cypher_rela_file.cypher', 'w')


def check_for_properties(property_value, xml_property_list, property_name, synonyms):
    if not property_value == '':
        list_property = property_value.split('; ')
        for property in list_property:
            property = property.replace('\t', '')
            if not property in xml_property_list:

                if property_name in ['PRODUCTS']:
                    synonyms.add(property)
                else:
                    print(property_name)
                    print(property)
                    print(xml_property_list)
                    sys.exit('structure problem')


# dictionary with drugbank id as key and value a list of salts ids
dict_drug_salts = {}
# dictionary with salt id as key and dictionary of information of salt
dict_salts = {}

# string for integrate the drubank database to neo4j with the neo4j-admin import tool
import_string='../../../../neo4j-community-3.2.9/bin/neo4j-admin import --mode=csv'

def load_salts_information_in():
    with open('drugbank/drugbank_salt.tsv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='\t')
        for row in spamreader:
            dict_salts[row['id']] = row
    with open('drugbank/drugbank_drug_salt.tsv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='\t')
        for row in spamreader:
            if row['drug_id'] in dict_drug_salts:
                dict_drug_salts[row['drug_id']].append(row['salt_id'])
            else:
                dict_drug_salts[row['drug_id']] = [row['salt_id']]

# dictionary with all drugbank drug ids
dict_drugbank_drug_ids={}

'''

'''
def drugs_combination_and_check(neo4j_label):
    # test if there are another information for the different drugs

    dict_drug_sequence = {}

    # this gather all information from the sequence folder
    print (datetime.datetime.utcnow())
    print('gather all information form drug sequences files')
    for file in os.listdir(path_to_drug_sequences):
        if file.endswith(".fasta"):
            path_file = os.path.join(path_to_drug_sequences, file)
            fasta_file_info = fasta_iter(path_file)
            for header, seq in fasta_file_info:
                # header drugbank|DBID name(|extra)
                db_id = header.split('|')[1].split(' ')[0]

                if db_id in dict_drug_sequence:
                    dict_drug_sequence[db_id].append(seq)
                else:
                    dict_drug_sequence[db_id] = [seq]

    dict_drug_external_ids = {}

    # this take all information from drug links.csv
    print (datetime.datetime.utcnow())
    print('take all information from drug links.csv')
    with open(path_to_external_links + 'drug links.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        i = 0
        properties = []
        for row in spamreader:
            if i == 0:
                properties = row
                i += 1
                continue
            dict_prop = {}
            j = 1
            for element in row[1:]:
                dict_prop[properties[j]] = element
                j += 1
            dict_drug_external_ids[row[0]] = dict_prop
    print(len(dict_drug_external_ids))

    dict_drug_structure_links = {}

    print (datetime.datetime.utcnow())
    print('take all information from structure links')
    # this takes all information from structures -> structure links.csv
    with open(path_to_structure + 'structure links.csv') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        i = 0
        properties = []
        for row in spamreader:
            if i == 0:
                properties = row
                i += 1
                continue
            dict_prop = {}
            j = 1
            for element in row[1:]:
                dict_prop[properties[j]] = element
                j += 1
            dict_drug_structure_links[row[0]] = dict_prop
        print(len(dict_drug_structure_links))

    dict_drug_structure = {}

    print (datetime.datetime.utcnow())
    print('take all information from structure')
    # this takes all information from structures -> structure.sdf which was converted into a csv
    # properties: ALOGPS_LOGP	ALOGPS_LOGS	ALOGPS_SOLUBILITY	DATABASE_ID	DATABASE_NAME	DRUGBANK_ID	DRUG_GROUPS	EXACT_MASS	FORMULA	GENERIC_NAME	ID	INCHI_IDENTIFIER	INCHI_KEY	INTERNATIONAL_BRANDS	JCHEM_ACCEPTOR_COUNT	JCHEM_ATOM_COUNT	JCHEM_AVERAGE_POLARIZABILITY	JCHEM_BIOAVAILABILITY	JCHEM_DONOR_COUNT	JCHEM_FORMAL_CHARGE	JCHEM_GHOSE_FILTER	JCHEM_IUPAC	JCHEM_LOGP	JCHEM_MDDR_LIKE_RULE	JCHEM_NUMBER_OF_RINGS	JCHEM_PHYSIOLOGICAL_CHARGE	JCHEM_PKA	JCHEM_PKA_STRONGEST_ACIDIC	JCHEM_PKA_STRONGEST_BASIC	JCHEM_POLAR_SURFACE_AREA	JCHEM_REFRACTIVITY	JCHEM_ROTATABLE_BOND_COUNT	JCHEM_RULE_OF_FIVE	JCHEM_TRADITIONAL_IUPAC	JCHEM_VEBER_RULE	MOLECULAR_WEIGHT	Molecule	PRODUCTS	SALTS	SECONDARY_ACCESSION_NUMBERS	SMILES	SYNONYMS
    with open('sdf/structure_combined.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=',')
        properties = spamreader.fieldnames
        i = 0
        properties = []
        for row in spamreader:
            dict_drug_structure[row['DRUGBANK_ID']] = row
        print(len(dict_drug_structure))

    dict_changed_external_identifier_source_name = {
        'Wikipedia ID': 'Wikipedia',
        'RxList Link': 'RxList',
        'PubChem Substance ID': 'PubChem Substance',
        'PubChem Compound ID': 'PubChem Compound',
        'UniProt ID': 'UniProtKB',
        'KEGG Drug ID': 'KEGG Drug',
        'TTD ID': 'Therapeutic Targets Database',
        'DPD ID': 'Drugs Product Database (DPD)',
        'Drugs.com Link': 'Drugs.com',
        'PharmGKB ID': 'PharmGKB',
        'GenBank ID': 'GenBank',
        'KEGG Compound ID': 'KEGG Compound',
        'ChEBI ID': 'ChEBI',
        'ChemSpider ID': 'ChemSpider',
        'BindingDB ID': 'BindingDB',
        'Pdrhealth Link': 'PDRhealth',
        'HET ID': 'PDB',
        'ChEMBL ID': 'ChEMBL'
    }

    # dictionary for the structure file,because the properties are different named
    dict_change_structure_property_to_tsv_property = {
        'JCHEM_ROTATABLE_BOND_COUNT': 'Rotatable Bond Count',
        'JCHEM_POLAR_SURFACE_AREA': 'Polar Surface Area (PSA)',
        'MOLECULAR_WEIGHT': 'Molecular Weight',
        'JCHEM_PHYSIOLOGICAL_CHARGE': 'Physiological Charge',
        'JCHEM_RULE_OF_FIVE': 'Rule of Five',
        'FORMULA': 'Molecular Formula',
        'JCHEM_GHOSE_FILTER': 'Ghose Filter',
        'JCHEM_TRADITIONAL_IUPAC': 'Traditional IUPAC Name',
        'ALOGPS_SOLUBILITY': 'Water Solubility',
        'JCHEM_MDDR_LIKE_RULE': 'MDDR-Like Rule',
        'JCHEM_IUPAC': 'IUPAC Name',
        'ALOGPS_LOGP': 'logP',
        'ALOGPS_LOGS': 'logS',
        'JCHEM_PKA_STRONGEST_BASIC': 'pKa (strongest basic)',
        'JCHEM_NUMBER_OF_RINGS': 'Number of Rings',
        'INCHI_KEY': 'InChIKey',
        'JCHEM_ACCEPTOR_COUNT': 'H Bond Acceptor Count',
        'JCHEM_PKA_STRONGEST_ACIDIC': 'pKa (strongest acidic)',
        'EXACT_MASS': 'Monoisotopic Weight',
        'JCHEM_DONOR_COUNT': 'H Bond Donor Count',
        'JCHEM_AVERAGE_POLARIZABILITY': 'Polarizability',
        'JCHEM_BIOAVAILABILITY': 'Bioavailability',
        'INCHI_IDENTIFIER': 'InChI',
        'JCHEM_REFRACTIVITY': 'Refractivity',
        'JCHEM_LOGP': 'logP'
    }

    print (datetime.datetime.utcnow())
    print('missing structure sdf')

    print (datetime.datetime.utcnow())
    print('check and combine the different information source with the xml source in an new file')

    new_properties_for_tsv = ['JCHEM_VEBER_RULE', 'JCHEM_PKA', 'JCHEM_ATOM_COUNT', 'JCHEM_FORMAL_CHARGE']
    dict_new_property_name_to_fitting_names = {
        'JCHEM_VEBER_RULE': 'veber_rule',
        'JCHEM_PKA': 'pka',
        'JCHEM_ATOM_COUNT': 'atom_count',
        'JCHEM_FORMAL_CHARGE': 'formal_charge'
    }

    # dictionary from drug to product list
    dict_drug_product = {}

    # get all information from drug_product file
    with open(path_prepared_drugbank_files + '/drugbank_drug_products.tsv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for line in reader:
            drug_id = line['drugbank_id']
            target_id = line['partner_id']
            if drug_id in dict_drug_product:
                dict_drug_product[drug_id].append(target_id)
            else:
                dict_drug_product[drug_id] = [target_id]

    # dictionary product number to name
    dict_product = {}

    # get all products names
    with open(path_prepared_drugbank_files + '/drugbank_products.tsv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for line in reader:
            name = line['name']
            identifier = line['id']
            dict_product[identifier] = name

    load_salts_information_in()

    tool_path='output/neo4j_import/drugbank_compounds.tsv'
    output_import_file= open(tool_path,'w')

    global import_string
    import_string+= ' --nodes '+ tool_path
    writer = csv.writer(output_import_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)



    # test if the sequence and the external identifier are the same and when something is not in the xml it is add
    # therefore a new file is generated
    # currently only the uniprot title are add to synonyms
    with open(path_prepared_drugbank_files + '/drugbank_drug.tsv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        output_file_drug = open('output/drugbank_drug.tsv', 'w')
        writer_drug = csv.writer(output_file_drug, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer_drug.writerow(header)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/output/drugbank_drug.tsv" As line FIELDTERMINATOR '\\t' Create (b:''' + neo4j_label + '''{ '''
        new_header = []

        list_properties=['alternative_drugbank_ids', 'groups', 'general_references_links_title_url',
                          'general_references_textbooks_isbn_citation', 'general_references_articles_pubmed_citation',
                          'synonyms', 'products', 'international_brands_name_company', 'mixtures_name_ingredients',
                          'packagers_name_url', 'manufacturers', 'prices_description_cost_unit',
                          'categories_category_mesh_id', 'affected_organisms', 'dosages_form_route_strength',
                          'atc_code_levels', 'ahfs_codes', 'pdb_entries',
                          'patents_number_country_approved_expires_pediatric_extension',
                          'food_interaction', 'sequences', 'calculated_properties_kind_value_source',
                          'experimental_properties_kind_value_source', 'external_identifiers',
                          'external_links_resource_url']

        for head in header:
            if head == '\xef\xbb\xbfdrugbank_id':
                query += '''identifier:line.drugbank_id, '''
                new_header.append('identifier:ID')
            elif head in list_properties:
                query += head + ':split(line.' + head + ''', '||'), '''
                new_header.append(head+':string[]')
            else:
                new_header.append(head)
                query += head + ':line.' + head + ', '
        new_header.append('license')
        new_header.append(':LABEL')
        writer.writerow(new_header)

        query = query + '''license:"''' + drugbank_license + '''"});\n'''
        cypher_file.write(query)
        cypher_file.write(':begin\n')
        cypher_file.write('Create Constraint On (node:' + neo4j_label + ') Assert node.identifier Is Unique;\n')
        cypher_file.write(':commit\n')

        counter_uniprot_title = 0
        for row in reader:
            drugbank_id = row['\xef\xbb\xbfdrugbank_id']
            dict_drugbank_drug_ids[drugbank_id]=1
            name = row['name']
            cas_number = row['cas_number']
            drug_type = row['type'].replace(' ', '')
            external_identifier = row['external_identifiers'].split('||') if row['external_identifiers'] != '' else []
            dict_external = {}
            synonyms = set(row['synonyms'].split('||')) if not row['synonyms'] == '' else set([])
            for line in external_identifier:
                if line.split(':', 1)[0] in dict_external:
                    dict_external[line.split(':', 1)[0]].append(line.split(':', 1)[1])
                else:
                    dict_external[line.split(':', 1)[0]] = [line.split(':', 1)[1]]
            external_identifier_links = row['external_links_resource_url'].split('||') if row[
                                                                                              'external_links_resource_url'] != '' else []
            for link_combination in external_identifier_links:
                if link_combination.split('::', 1)[0] in dict_external:
                    dict_external[link_combination.split('::', 1)[0]].append(link_combination.split('::', 1)[1])
                else:
                    dict_external[link_combination.split('::', 1)[0]] = [link_combination.split('::', 1)[1]]

            dict_from_drug = dict_drug_external_ids[drugbank_id]
            if name != dict_from_drug['Name']:
                print(dict_external)
                print(drugbank_id)
                print(dict_from_drug['Name'])
                sys.exit('name ' + name)
            if cas_number != dict_from_drug['CAS Number']:
                print(drugbank_id)
                print(dict_external)
                sys.exit('cas_number ')
            if not drug_type in dict_from_drug['Drug Type'].lower():
                print(dict_external)
                print(drugbank_id)
                print(dict_from_drug['Drug Type'])
                print(drug_type)
                sys.exit('type ')
            for property, value in dict_from_drug.items():
                # print(property)
                # print(property in ['Name','CAS Number','Drug Type'])
                # print('Name' in ['Name', 'CAS Number','Drug Type'])
                if property in ['Name', 'CAS Number', 'Drug Type']:
                    continue
                elif (property == 'UniProt Title') and value != '':
                    counter_uniprot_title += 1
                    synonyms.add(value)
                    # print(dict_external)
                    # print(drugbank_id)
                    # print(property +'###########################################')
                    # print(value)
                    continue
                elif property in dict_changed_external_identifier_source_name:
                    property = dict_changed_external_identifier_source_name[property]

                if property in dict_external:
                    for value_part in value.split('; '):
                        if not value_part in dict_external[property]:
                            print(dict_external)
                            print(drugbank_id)
                            print(property)
                            print(value)
                            print(value_part)
                            print(dict_external[property])
                            sys.exit('external identifier')
                elif value == '':
                    continue
                else:
                    print(dict_external)
                    print(drugbank_id)
                    print(property)
                    print(value)
                    sys.exit('external identifier not existing')

            groups = []
            # dictionary with all experimental properties if the durgbank id is at least on structure file
            dict_experimental_property_value = {}
            # dictionary with all calculated properties if the durgbank id is at least on structure file
            dict_calculated_property_value = {}
            dict_calculated_property_value_to_tool = {}
            if drugbank_id in dict_drug_structure_links or drugbank_id in dict_drug_structure:
                groups = row['groups'].split('||')
                # experimental_properties_kind_value_source
                experimental_property_value = row['experimental_properties_kind_value_source'].split('||') if row[
                                                                                                                  'experimental_properties_kind_value_source'] != '' else []
                for property_value_source in experimental_property_value:
                    split_prop_value_source = property_value_source.split('::')
                    if split_prop_value_source[0] in dict_experimental_property_value:
                        print('ohje')
                        sys.exit('experimental property')
                    else:
                        dict_experimental_property_value[split_prop_value_source[0]] = split_prop_value_source[1]

                calculated_property_value = row['calculated_properties_kind_value_source'].split('||') if row[
                                                                                                              'calculated_properties_kind_value_source'] != '' else []

                for property_value_source in calculated_property_value:
                    split_prop_value_source = property_value_source.split('::')
                    if split_prop_value_source[0] in dict_calculated_property_value:
                        dict_calculated_property_value[split_prop_value_source[0]].append(split_prop_value_source[1])

                    else:
                        dict_calculated_property_value[split_prop_value_source[0]] = [split_prop_value_source[1]]
                    dict_calculated_property_value_to_tool[(split_prop_value_source[0], split_prop_value_source[1])] = \
                        split_prop_value_source[2]

            # check out all information in comparision to the structure link file
            if drugbank_id in dict_drug_structure_links:
                dict_from_drug = dict_drug_structure_links[drugbank_id]

                for group_in_structure_links in dict_from_drug['Drug Groups'].split('; '):
                    if not group_in_structure_links in groups:
                        print(drugbank_id)
                        print(group_in_structure_links)
                        sys.exit('structure link group')

                if name != dict_from_drug['Name']:
                    print(dict_external)
                    print(drugbank_id)
                    print(dict_from_drug['Name'])
                    sys.exit('structure link name ' + name)
                if cas_number != dict_from_drug['CAS Number']:
                    print(drugbank_id)
                    print(dict_external)
                    sys.exit('structure link cas_number ')
                for property, value in dict_from_drug.items():
                    if property in ['Name', 'CAS Number', 'Drug Groups']:
                        continue

                    elif property in dict_changed_external_identifier_source_name:
                        property = dict_changed_external_identifier_source_name[property]
                        if property in dict_external:
                            for value_part in value.split('; '):
                                if not value_part in dict_external[property]:
                                    print(dict_external)
                                    print(drugbank_id)
                                    print(property)
                                    print(value)
                                    print(value_part)
                                    print(dict_external[property])
                                    sys.exit('structure links external identifier')
                        elif value == '':
                            continue
                        else:
                            print(dict_external)
                            print(drugbank_id)
                            print(property)
                            print(value)
                            sys.exit('structure links external identifier not existing')
                    elif property in ['InChIKey', 'InChI', 'SMILES', 'Formula']:
                        found = False
                        if property == 'Formula':
                            property = 'Molecular Formula'
                        if property in dict_experimental_property_value:
                            if value == dict_experimental_property_value[property]:
                                found = True
                        if not found and property in dict_calculated_property_value:
                            if value in dict_calculated_property_value[property]:
                                found = True
                        if not found and value != '':
                            print('property')
                            print(drugbank_id)
                            print(property)
                            print(dict_experimental_property_value)
                            print(dict_calculated_property_value)
                            sys.exit('not in experimental or calculated')
                    else:
                        print(drugbank_id)
                        print(property)
                        print(row)
                        sys.exit('property problem')

            # maybe accurate calculated values
            dict_accurate_calculated_values = {}

            # maybe accurate experimental values
            dict_accurate_experimental_values = {}

            # maybe dictionary of new inchi and or inchikey
            dict_inchi_inchikey = {}

            # check structure information
            if drugbank_id in dict_drug_structure:

                dict_drug_structure_properties = dict_drug_structure[drugbank_id]
                alternative_drugbank_ids_list = row['alternative_drugbank_ids'].split('||')

                salts_name_list = set([])

                if drugbank_id in dict_drug_salts:
                    for salt_id in dict_drug_salts[drugbank_id]:
                        salts_name_list.add(dict_salts[salt_id]['name'])

                products_name_list = set([])
                print(drugbank_id)
                if drugbank_id in dict_drug_product:
                    for product in dict_drug_product[drugbank_id]:
                        # # print(drugbank_id)
                        # # print(product)
                        # # print(product.split(';;'))
                        # dict_product = {property.split(':')[0]: property.split(':')[1] for property in
                        #                 product.split(';;')}
                        products_name_list.add(dict_product[product])

                brand_name_list = set(
                    [brand_name.split(':')[0] for brand_name in row['international_brands_name_company'].split('||')])

                dict_property_name_to_list = {
                    'SECONDARY_ACCESSION_NUMBERS': alternative_drugbank_ids_list,
                    'DRUG_GROUPS': groups,
                    'PRODUCTS': products_name_list,
                    'INTERNATIONAL_BRANDS': brand_name_list,
                    'SALTS': salts_name_list,
                    'SYNONYMS': synonyms
                }
                if drugbank_id == 'DB09496':
                    print('huh')

                # go through all drugbank entries in the structure file and campare the values with the one in the xml file and maybe update the values
                for property_name, property_value in dict_drug_structure_properties.items():

                    # get the toll name
                    tool_name = ''
                    if property_name[0:6] == 'ALOGPS':
                        tool_name = 'ALOGPS'
                    elif property_name[0:5] == 'JCHEM':
                        tool_name = 'ChemAxon'

                    # some of the property names are different in the structure file and xml file
                    if property_name in dict_change_structure_property_to_tsv_property:

                        property_name = dict_change_structure_property_to_tsv_property[property_name]
                    # some properties do not need to be check:
                    # Database ID == Drugbank id (both are already check if they are in the xml)
                    # database name is every time DrugBank
                    # the ID is only important in the structure file
                    # molecule is a python object which contains all information
                    elif property_name in ['', 'Molecule', 'DATABASE_ID', 'DRUGBANK_ID', 'ID', 'DATABASE_NAME']:
                        continue
                    # some properties have multiple values and all need to be checked
                    elif property_name in ['SYNONYMS', 'SECONDARY_ACCESSION_NUMBERS', 'DRUG_GROUPS', 'PRODUCTS',
                                           'INTERNATIONAL_BRANDS', 'SALTS']:
                        # print(property_name)
                        # print(drugbank_id)
                        if property_name == 'SECONDARY_ACCESSION_NUMBERS':
                            if property_value == drugbank_id:
                                print('same ids')
                                continue
                        check_for_properties(property_value, dict_property_name_to_list[property_name], property_name,
                                             synonyms)
                        continue
                    # some properties do not exists in the xml file and are add to calculated information
                    elif property_name in new_properties_for_tsv:
                        if property_value != '':
                            dict_accurate_calculated_values[dict_new_property_name_to_fitting_names[property_name]] = [
                                {'value': property_value, 'tool': tool_name}]
                        continue
                    # generic name should be the same as the name in the xml file
                    elif property_name == 'GENERIC_NAME':
                        if property_value != name:
                            print(name)
                            print(property_value)
                            sys.exit('generic name')
                        continue

                    found_property = False
                    # only if the value is not empty a comparision is needed
                    if property_value != '':
                        # only when there is no tool name it can be compared with the experimental value
                        if tool_name == '':
                            if property_name in dict_experimental_property_value:
                                found_property = True
                                if dict_experimental_property_value[property_name] != property_value:
                                    try:
                                        float(dict_experimental_property_value[property_name])
                                        if not property_name in dict_accurate_experimental_values:
                                            dict_accurate_experimental_values[property_name] = [property_value]
                                        else:
                                            dict_accurate_experimental_values[property_name].append(property_value)
                                        print(dict_experimental_property_value[property_name])
                                        print(drugbank_id)
                                        print(row['experimental_properties_kind_value_source'])
                                        print(property_name + ':' + property_value)
                                        # sys.exit(property_name+':'+property_value)
                                    except ValueError:
                                        print(drugbank_id)
                                        print(row['experimental_properties_kind_value_source'])
                                        print(property_name + ':' + property_value)

                        if property_name in dict_calculated_property_value:
                            found_property = True
                            if property_value not in dict_calculated_property_value[property_name]:
                                # all double string values
                                if '.' in property_value:
                                    if not property_name in dict_accurate_calculated_values:
                                        dict_accurate_calculated_values[property_name] = [
                                            {'value': property_value, 'tool': tool_name}]
                                    else:
                                        dict_accurate_calculated_values[property_name].append(
                                            {'value': property_value, 'tool': tool_name})
                                    print(drugbank_id)
                                    print(property_name)
                                    print(dict_calculated_property_value[property_name])
                                    print(tool_name)
                                    print(property_value)
                                # by inchikey, inchi, smiles are somtimes some different version of the same
                                # test !!!!!!
                                elif property_name in ['SMILES', 'InChIKey', 'InChI']:
                                    dict_accurate_calculated_values[property_name] = []
                                    for value in dict_calculated_property_value[property_name]:
                                        dict_accurate_calculated_values[property_name].append({'value': value, 'tool':
                                            dict_calculated_property_value_to_tool[(property_name, value)]})
                                    dict_accurate_calculated_values[property_name].append(
                                        {'value': property_value, 'tool': tool_name})
                                    print(property_name)
                                    print(drugbank_id)
                                    print(dict_accurate_calculated_values[property_name])

                                # if property_name in ['SMILES','Polar Surface Area (PSA)','logS','pKa (strongest basic)','pKa (strongest acidic)','Polarizability', 'Refractivity','logP']:
                                else:
                                    print(drugbank_id)
                                    print(property_name)
                                    print(dict_calculated_property_value[property_name])
                                    sys.exit(property_name + ':' + property_value)

                        # if the property is not in the xml it is add to the new file
                        if not found_property:

                            # if property_name in ['Physiological Charge', 'Molecular Weight', 'Molecular Formula',
                            #                          'InChIKey', 'Monoisotopic Weight', 'InChI', 'Rotatable Bond Count',
                            #                          'Polar Surface Area (PSA)','SMILES','Refractivity','Bioavailability','Polarizability','H Bond Donor Count','pKa (strongest acidic)','H Bond Acceptor Count','Number of Rings','pKa (strongest basic)','logS','logP','Rule of Five','Ghose Filter','IUPAC Name','Traditional IUPAC Name','Water Solubility','MDDR-Like Rule']:

                            # this drugbank entries contains false information in comparison to other sources like pubchem and other
                            # also it is note really ready annotated in DrugBank
                            if drugbank_id in ['DB14193', 'DB14194']:
                                continue
                            elif property_name in ['InChIKey', 'InChI']:
                                dict_inchi_inchikey[property_name] = property_value
                            print(drugbank_id)
                            print(property_name)
                            print(property_value)
                            print(tool_name)
                            # print(row['calculated_properties_kind_value_source'])
                            dict_accurate_calculated_values[property_name] = [
                                {'value': property_value, 'tool': tool_name}]
                            continue

            # currently no problem with sequences
            if drugbank_id in dict_drug_sequence:
                sequences = row['sequences'].split('||') if row['sequences'] != '' else []
                dict_drug_sequences = {}  #

                for sequence in sequences:
                    # print(drugbank_id)
                    # print(sequence)
                    dict_drug_sequences[sequence.split(' ')[1]] = 1

                for sequence_seq_file in dict_drug_sequence[drugbank_id]:
                    if not sequence_seq_file in dict_drug_sequences:
                        print(dict_drug_sequences)
                        print(drugbank_id)
                        print(sequence_seq_file)
                        sys.exit('sequences')

            # write the infomation into the output file with the updated information
            output_list = []
            new_entry = []



            for head in header:
                # only synonyms and calculated properties are updated
                if not head in ['synonyms', 'calculated_properties_kind_value_source', 'inchikey', 'inchi']:
                    if head == 'classification_description':
                        row[head] = row[head].replace('\"', '\\"')

                    if drugbank_id == 'DB00315' and (head == 'products' or head == 'mixtures_name_ingredients'):
                        output_list.append('')
                        continue
                    output_list.append(row[head])
                    if not head in list_properties:
                        new_entry.append(row[head])
                    else:
                        property_parts=row[head].split('||')
                        property_parts_string = ''
                        for part in property_parts:
                            part=part.replace(';',',')
                            property_parts_string+=part+';'
                        new_entry.append(part[0:-1])


                    if drugbank_id == 'DB00315':
                        print(head)
                        print(len(row[head]))
                elif head == 'synonyms':
                    string_synonyms = '||'.join(synonyms)
                    property_parts_string = ''
                    for part in synonyms:
                        part = part.replace(';', ',')
                        property_parts_string += part + ';'
                    new_entry.append(part[0:-1])
                    output_list.append(string_synonyms)
                    if drugbank_id == 'DB00315':
                        print(head)
                        print(len(string_synonyms))
                elif head in ['inchikey', 'inchi']:
                    if head in dict_inchi_inchikey:
                        output_list.append(dict_inchi_inchikey[head])
                        new_entry.append(dict_inchi_inchikey[head])
                        if drugbank_id == 'DB00315':
                            print(head)
                            print(len(dict_inchi_inchikey[head]))
                    else:
                        output_list.append(row[head])
                        new_entry.append(row[head])
                else:
                    calculated_updated_values = []
                    if row['calculated_properties_kind_value_source'] != '':
                        new_calculated_property_list = []
                        used_new_calculated_values = {}
                        for property_with_value_tool in row['calculated_properties_kind_value_source'].split('||'):
                            # print(property_with_value_tool)
                            [property_name, property_value, tool] = property_with_value_tool.split('::')
                            tool_found = False
                            if property_name in dict_accurate_calculated_values:

                                for dict_property_part in dict_accurate_calculated_values[property_name]:
                                    if tool == dict_property_part['tool']:
                                        tool_found = True
                                        new_calculated_property_list.append(
                                            property_name + '::' + dict_property_part['value'] + '::' + tool)
                                        used_new_calculated_values[(property_name, dict_property_part['value'])] = tool
                            if not tool_found:
                                new_calculated_property_list.append(property_with_value_tool)

                        for property_name, list_dict_values in dict_accurate_calculated_values.items():
                            for part_value_dict in list_dict_values:
                                if not (property_name, part_value_dict['value']) in used_new_calculated_values:
                                    new_calculated_property_list.append(
                                        property_name + '::' + part_value_dict['value'] + '::' + part_value_dict[
                                            'tool'])

                        string_calculated_update = '||'.join(new_calculated_property_list)
                        import_tool_string=''
                        for part_of_calculated in new_calculated_property_list:
                            part_of_calculated=part_of_calculated.replace(';',',')
                            import_tool_string+=part_of_calculated+';'

                        new_entry.append(import_tool_string[0:-1])
                        output_list.append(string_calculated_update)
                        if drugbank_id == 'DB00315':
                            print(head)
                            print(len(string_calculated_update))
                    else:
                        output_list.append(row['calculated_properties_kind_value_source'])
                        new_entry.append(row['calculated_properties_kind_value_source'])
                        if row['calculated_properties_kind_value_source']!='':
                            print('huhu')
                        if drugbank_id == 'DB09495':
                            print(head)
                            print(len(row[head]))
            new_entry.append(drugbank_license)
            new_entry.append(neo4j_label)
            writer.writerow(new_entry)
            writer_drug.writerow(output_list)
            # if drugbank_id == 'DB00315':
            #     sys.exit()

        print('number of new synonyms:' + str(counter_uniprot_title))

    # to reduce the memory
    dict_drug_sequence = {}
    dict_drug_external_ids = {}
    dict_drug_structure_links = {}


###################################################################################################################

# dictionary with all carrier, target, transporter and enzyme every entry has an extra property for the label, because some target  exists in multiple label
dict_target_properties = {}

# dictionary with all carrier, targets, transporter and enzyme
dict_all_targets = {}

'''
take from the external link directory files only the drugbank id, uniprot id and uniprot name
and add the information in the two different dictionary (pair, and info target)
'''


def external_links_for_all_drug_targets(file, dict_drug_targets, dict_targets):
    with open(path_to_external_links + file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        i = 0
        for row in reader:
            if not (row['DrugBank ID'], row['UniProt ID']) in dict_drug_targets:
                dict_drug_targets[(row['DrugBank ID'], row['UniProt ID'])] = 1
            else:
                dict_drug_targets[(row['DrugBank ID'], row['UniProt ID'])] += 1

            if not row['UniProt ID'] in dict_targets:
                dict_targets[row['UniProt ID']] = row['UniProt Name']


'''
take from the target sequences directory files only the drugbank ids, uniprot id, name and gene and protein sequence
and add the information in the two different dictionary (pair, and info target)
'''


def work_with_target_sequence_fasta(directory, file, sequence, dict_targets, dict_drug_targets):
    fasta_file_info = fasta_iter(directory + file)
    for header, seq in fasta_file_info:
        # header drugbank|UniProt ID name (DB ID)
        uniprot_id = header.split('|')[1].split(' ')[0]
        name = header.split('|')[1].split(' ', 1)[1].rsplit(' (', 1)[0]
        db_ids = header.rsplit('(', 1)[1].replace(')', '').split('; ')

        if not uniprot_id in dict_targets:
            dict_targets[uniprot_id] = {
                'name': name,
                sequence: seq
            }
        else:
            dict_targets[uniprot_id][sequence] = seq
        for db_id in db_ids:
            if not (db_id, uniprot_id) in dict_drug_targets:
                dict_drug_targets[(db_id, uniprot_id)] = 1


'''
gather the information in the different dictionaries for gene and protein.fasts
'''


def sequences_for_all_targets(directory, dict_drug_targets, dict_targets):
    work_with_target_sequence_fasta(directory, 'gene.fasta', 'gene_sequence', dict_targets, dict_drug_targets)
    work_with_target_sequence_fasta(directory, 'protein.fasta', 'amino_acid_sequence', dict_targets, dict_drug_targets)


def identifier_for_all_targets(directory, dict_drug_targets, dict_targets, dict_drug_target_pharmacologically_actions):
    with open(directory + 'pharmacologically_active.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        header = reader.fieldnames
        i = 0
        for row in reader:
            dict_target_info = {}
            uniprot_id = row['UniProt ID']
            drug_ids = row['Drug IDs'].split('; ') if row['Drug IDs'] != '' else []
            for head in header:
                if head not in ['ID', 'UniProt ID', 'Drug IDs', 'Species']:
                    dict_target_info[head] = row[head].split('; ') if row[head] != '' else []
            if uniprot_id not in dict_targets:
                dict_targets[uniprot_id] = dict_target_info
            else:
                for head in header:
                    if head not in ['ID', 'UniProt ID', 'Drug IDs', 'Species']:
                        values = row[head].split('; ') if row[head] != '' else []
                        for value in values:
                            if value not in dict_target_info[head]:
                                sys.exit('multiple uniprot in on file and one value is not in there ' + uniprot_id)

            for drug_id in drug_ids:
                dict_drug_target_pharmacologically_actions[(drug_id, uniprot_id)] = row['Species']

    with open(directory + 'all.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        header = reader.fieldnames
        i = 0
        for row in reader:
            dict_target_info = {}
            uniprot_id = row['UniProt ID']
            drug_ids = row['Drug IDs'].split('; ') if row['Drug IDs'] != '' else []
            for head in header:
                if head not in ['ID', 'UniProt ID', 'Drug IDs']:
                    dict_target_info[head] = row[head].split('; ') if row[head] != '' else []
            # only the uniprot id which are not in the pharmacologically file need this add information
            if uniprot_id not in dict_targets:
                dict_targets[uniprot_id] = dict_target_info

            for drug_id in drug_ids:
                if (drug_id, uniprot_id) not in dict_drug_target_pharmacologically_actions:
                    dict_drug_targets[(drug_id, uniprot_id)] = 1


# dictionary for the different names for the same xrefs
dict_target_change_xrefs_name = {
    'GenAtlas ID': 'GenAtlas',
    'GenBank Gene ID': 'GenBank Gene Database',
    'GenBank Protein ID': 'GenBank Protein Database',
    'HGNC ID': 'HUGO Gene Nomenclature Committee (HGNC)'
}

'''
check the information from the different csv for the target files with the from the xml 
'''


def check_and_maybe_generate_a_new_target_file(file, dict_targets_info_external, dict_targets_info_sequence,
                                               dict_targets_info_identifier, output_file, neo4j_label,
                                               neo4j_general_label):
    header_new = []
    with open(file) as csvfile:
        print(file)
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        output_file_csv = open(output_file, 'w')
        writer_output = csv.writer(output_file_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        i = 0
        for head in header:
            header_new.append(head)
        writer_output.writerow(header_new)

        # query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + output_file + '''" As line FIELDTERMINATOR '\\t' Create (b:''' + neo4j_label +' :'+neo4j_general_label+ '''{ '''
        # for head in header_new:
        #     # if head == 'drugbank_id':
        #     #     query += '''identifier:line.''' + head + ', '
        #     if head == 'id':
        #         query += '''identifier:line.''' + head + ', '
        #     elif head in ['go_classifiers', 'pfams', 'gene_sequence', 'amino_acid_sequence', 'synonyms', 'xrefs']:
        #         query += head + ':split(line.' + head + ''', '||'), '''
        #     else:
        #         query += head + ':line.' + head + ', '
        #
        # query = query + '''license:"''' + drugbank_license + '''"});\n'''
        # cypher_file.write(query)
        # cypher_file.write(':begin\n')
        # cypher_file.write('Create Constraint On (node:' + neo4j_label + ') Assert node.identifier Is Unique;\n')
        # cypher_file.write(':commit\n')
        list_of_all_used_uniprot_ids = set([])
        # print(header)
        counter_total_number_of_nodes = 0
        counter_same_id_different_label = 0
        counter_same_id_different_label_not_same_properties = 0
        for row in reader:
            counter_total_number_of_nodes += 1
            drugbank_id = row['drugbank_id']
            uniprot_id = row['id']
            list_of_all_used_uniprot_ids.add(uniprot_id)
            name = row['name']
            synonyms = row['synonyms'].split('||') if row['synonyms'] != '' else []
            gene_sequence_list = []

            if uniprot_id != '' and uniprot_id not in dict_all_targets:
                dict_all_targets[uniprot_id] = 1
            elif uniprot_id == '' and drugbank_id not in dict_all_targets:
                dict_all_targets[drugbank_id] = 1

            if uniprot_id in dict_targets_info_external:
                if name != dict_targets_info_external[uniprot_id] and dict_targets_info_external[
                    uniprot_id] not in synonyms:
                    print(row)
                    print(name)
                    print(dict_targets_info_external[uniprot_id])
                    print(
                        '###############################################################################################################################')
                    # sys.exit('uniprot name not the same ' + uniprot_id)

            if uniprot_id in dict_targets_info_sequence:
                # print(row)
                # print(uniprot_id)
                gene_sequence = row['gene_sequence'].split(' ')[1] if row['gene_sequence'] != '' else ''
                amino_acid_sequence = row['amino_acid_sequence'].split(' ')[1] if row[
                                                                                      'amino_acid_sequence'] != '' else ''
                dict_targets_info_sequence[uniprot_id]['gene_sequence'] = dict_targets_info_sequence[uniprot_id][
                    'gene_sequence'] if 'gene_sequence' in dict_targets_info_sequence[uniprot_id] else ''
                if dict_targets_info_sequence[uniprot_id]['gene_sequence'] != '' and gene_sequence != \
                        dict_targets_info_sequence[uniprot_id]['gene_sequence']:
                    # take for the sequences both, because they are different variants of the same protein
                    # only Q05513 there is one sequence part of the other and the logger version is taken
                    if not uniprot_id in ['Q05513', 'P31641', 'Q15878']:
                        gene_sequence_list.append(gene_sequence)
                        gene_sequence_list.append(dict_targets_info_sequence[uniprot_id]['gene_sequence'])
                    # by Q15878 the other sequence is not mapping correctly in ncbi
                    elif uniprot_id in ['Q05513', 'Q15878']:
                        gene_sequence_list.append(gene_sequence)
                    # by P31641 the sequence from the sequence file is longer
                    else:
                        gene_sequence_list.append(dict_targets_info_sequence[uniprot_id]['gene_sequence'])
                    # print(uniprot_id)
                    # print('gene seq')
                    # print(name)
                    # print(dict_targets_info_sequence[uniprot_id]['gene_sequence'])
                    # print(gene_sequence)
                    # i=0
                    # for letter in dict_targets_info_sequence[uniprot_id]['gene_sequence']:
                    #     if letter != gene_sequence[i]:
                    #         print(i+1)
                    #         print(letter)
                    #         print(gene_sequence[i])
                    #     i+=1
                    # sys.exit('gene sequence is not the same:' + uniprot_id)
                if amino_acid_sequence != dict_targets_info_sequence[uniprot_id]['amino_acid_sequence']:
                    print(uniprot_id)
                    print('protein seq')
                    print(dict_targets_info_sequence[uniprot_id]['amino_acid_sequence'])
                    print(amino_acid_sequence)
                    i = 0
                    # for letter in dict_targets_info_sequence[uniprot_id]['amino_acid_sequence']:
                    #     if letter != amino_acid_sequence[i]:
                    #         print(i+1)
                    #         print(letter)
                    #         print(amino_acid_sequence[i])
                    #     i += 1
                    sys.exit('protein sequence is not the same:' + uniprot_id)
                if name != dict_targets_info_sequence[uniprot_id]['name']:
                    ### think about adding them to synonyms
                    print(uniprot_id)
                    print(name)
                    print(dict_targets_info_sequence[uniprot_id]['name'])
                    # sys.exit('name in sequence is not the same:' + uniprot_id)
            #
            xrefs = {}
            if uniprot_id in dict_targets_info_identifier:
                if row['xrefs'] != '':
                    for xref_source_value in row['xrefs'].split('||'):
                        # print(xref_source_value)
                        source = xref_source_value.split('::')[0]
                        value = xref_source_value.split('::')[1]
                        if source in xrefs:
                            xrefs[source].append(value)
                        else:
                            xrefs[source] = [value]

                for property, values in dict_targets_info_identifier[uniprot_id].items():
                    if property in dict_target_change_xrefs_name:
                        property = dict_target_change_xrefs_name[property]
                    if property in ['Gene Name', 'Uniprot Title']:
                        for value in values:
                            if value not in synonyms or value == name:
                                synonyms.append((value))
                                # print(uniprot_id)
                                # print(value)
                                # sys.exit('not in synonyms:' + property + ' ' + ';'.join(value) + '(' + uniprot_id)
                    elif property not in ['ID', 'Name', 'Species']:
                        if property in xrefs:
                            for value in values:
                                if value not in xrefs[property]:
                                    print(dict_targets_info_identifier[uniprot_id])
                                    print(property)
                                    print(value)
                                    sys.exit('value are not the same:' + uniprot_id)
                        elif values == [] or property == 'UniProtKB':
                            continue
                        elif property == 'PDB ID':
                            xrefs[property] = values
                            # print(uniprot_id)
                            # print(values)
                            # print('PDB ID to xref')
                        else:
                            print(dict_targets_info_identifier[uniprot_id])
                            print(property)
                            print(values)
                            sys.exit('xref property is not there:' + uniprot_id)

            list_properties = []
            identifier = uniprot_id
            for head in header:
                if head not in ['synonyms', 'xrefs', 'gene_sequence']:
                    if head == 'id' and row[head] == '':
                        list_properties.append(row['drugbank_id'])
                        identifier = row['drugbank_id']
                    else:
                        list_properties.append(row[head])
                elif head == 'synonyms':
                    string_synonyms = '||'.join(synonyms)
                    list_properties.append(string_synonyms)
                elif head == 'gene_sequence':
                    if len(gene_sequence_list) > 1:
                        combined_sequences = '||'.join(gene_sequence_list)
                        list_properties.append(combined_sequences)
                    else:
                        list_properties.append(row[head])
                else:
                    string_xref = '||'.join([xref + '::' + ';'.join(values) for xref, values in xrefs.items()])
                    list_properties.append(string_xref)

            if not identifier in dict_target_properties:
                dict_target_properties[identifier] = [list_properties, [neo4j_label]]
            else:
                before_properties, label_list = dict_target_properties[identifier]
                i = 0
                counter_same_id_different_label += 1
                for property in list_properties:
                    if property != before_properties[i]:
                        print(identifier)
                        print(before_properties)
                        print(list_properties)
                        print(label_list)
                        print(neo4j_label)
                        # sys.exit('ohje')
                        if property[0:2] == 'BE':
                            before_properties[i] += '||' + property
                        else:
                            sys.exit('another property is not the same')
                        counter_same_id_different_label_not_same_properties += 1
                    i += 1

                dict_target_properties[identifier][1].append(neo4j_label)

            writer_output.writerow(list_properties)

        print('same id different label:' + str(counter_same_id_different_label))
        print('same id different label different property:' + str(counter_same_id_different_label_not_same_properties))
        print('total number of nodes:' + str(counter_total_number_of_nodes))
        not_in_xml = set([])
        for uniprot_id in dict_targets_info_external.keys():
            if not uniprot_id in list_of_all_used_uniprot_ids:
                print(dict_targets_info_external[uniprot_id])
                print(uniprot_id + ' is not included in xml')
                not_in_xml.add(uniprot_id)
                # sys.exit(uniprot_id+' is not included in xml')
        print(len(not_in_xml))
        counter = 0
        for uniprot_id in dict_targets_info_identifier.keys():
            if not uniprot_id in list_of_all_used_uniprot_ids:  # and not uniprot_id in not_in_xml:
                print(dict_targets_info_external[uniprot_id])
                print(uniprot_id + ' is not included in xml')
                counter += 1
        print(counter)
        for uniprot_id in dict_targets_info_sequence.keys():
            if not uniprot_id in list_of_all_used_uniprot_ids:  # and not uniprot_id in not_in_xml:
                print(dict_targets_info_external[uniprot_id])
                print(uniprot_id + ' is not included in xml')
                counter += 1
        print(counter)
        return header_new


dict_label_to_file = {}


'''
generate combineded file for carrier, target, transporter and enzyme but with different label number
'''


def generate_combined_csv_files(header_new, neo4j_general_label, special_label_list):
    global import_string
    general_file_start = 'output/drugbank_'
    general_file_end = '.tsv'

    tool_path='output/neo4j_import/carrier_enzyme_target_transporter.tsv'
    output_file = open(tool_path, 'w')
    import_string += ' --nodes ' + tool_path
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    list_properties=['go_classifiers', 'pfams', 'gene_sequence', 'amino_acid_sequence', 'synonyms', 'xrefs']

    sub_query = ''
    header_import_tool=[]
    for head in header_new:
        # if head == 'drugbank_id':
        #     query += '''identifier:line.''' + head + ', '
        # if head == 'labels':
        #     continue
        if head == 'id':
            sub_query += '''identifier:line.''' + head + ', '
            header_import_tool.append('identifier:ID')
        elif head in list_properties:
            sub_query += head + ':split(line.' + head + ''', '||'), '''
            header_import_tool.append(head+':string[]')
        else:
            sub_query += head + ':line.' + head + ', '
            header_import_tool.append(head)

    sub_query = sub_query + '''license:"''' + drugbank_license + '''"});\n'''
    header_import_tool.append('license')
    header_import_tool.append(':LABEL')
    writer.writerow(header_import_tool)

    for identifier, [property, label_list] in dict_target_properties.items():
        label_string = '_'.join(label_list)
        # generate for every different label combination a new file and cypher query
        if label_string in dict_label_to_file:
            dict_label_to_file[label_string].writerow(property)
        else:
            file_path = general_file_start + label_string + general_file_end
            output_file_csv = open(file_path, 'w')
            writer_output = csv.writer(output_file_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            dict_label_to_file[label_string] = writer_output
            writer_output.writerow(header_new)
            writer_output.writerow(property)
            query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + file_path + '''" As line FIELDTERMINATOR '\\t' Create (b'''
            for neo4j_label in label_list:
                query += ''':''' + neo4j_label + ' '
            query += ''':''' + neo4j_general_label + '''{ '''
            query += sub_query
            cypher_file.write(query)
        new_entry=[]
        counter=0
        for head in header_new:
            if head in list_properties:
                list_information= property[counter].split('||')
                new_list=[]
                for part_info in list_information:
                    part_info=part_info.replace(';',',')
                    new_list.append(part_info)
                new_list=';'.join(new_list)
                new_entry.append(new_list)
            else:
                new_entry.append(property[counter])
            counter+=1
        label_list.append(neo4j_general_label)
        label_list=';'.join(label_list)
        new_entry.append(drugbank_license)
        new_entry.append(label_list)
        writer.writerow(new_entry)

    # for neo4j_label in special_label_list:
    cypher_file.write(':begin\n')
    cypher_file.write('Create Constraint On (node:' + neo4j_general_label + ') Assert node.identifier Is Unique;\n')
    cypher_file.write(':commit\n')


dict_all_target_drug_pairs = {}

'''
check the information from the different csv for the target-drug pairs files with the from the xml
the parmacologically active id known-action in xml ('yes') 
'''


def check_and_maybe_generate_a_new_drug_target_file(file, dict_drug_targets_external, dict_drug_targets_sequence,
                                                    dict_drug_targets_identifier,
                                                    dict_drug_targets_pharmacologically_active_identifier,
                                                    neo4j_label_drug, neo4j_label_target, short_form_label,first):
    global import_string
    dict_drug_targe_pairs_xml = {}
    output_file = open('output/' + file.split('/')[1], 'w')
    writer_output = csv.writer(output_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/output/''' + \
            file.split('/')[1] + '''" As line FIELDTERMINATOR '\\t' Match (c:''' + neo4j_label_drug \
            + '''{ identifier: line.drugbank_id}), (g:''' + neo4j_label_target + '''{ identifier:line.targets_id })  Create (c)-[a:associate_with_Caw''' + short_form_label + '''{ '''

    tool_path = 'output/neo4j_import/drug_target.tsv'
    output_import_tool = open(tool_path, 'a')
    writer_tool=csv.writer(output_import_tool,delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    header_tool=[]
    list_properties = ['actions', 'ref_article', 'ref_links', 'ref_textbooks']

    with open(file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        header_new = []

        for head in header:
            # if '-' in head:
            #     head = head.replace('-', '_')
            if head=='targets_id_drugbank':
                continue
            header_new.append(head)
            if head not in ['drugbank_id', 'targets_id']:
                if head in list_properties:
                    query+=head+':split(line.'+head+',"||"), '
                    header_tool.append(head+':string[]')
                else:
                    query += head + ':line.' + head + ', '
                    header_tool.append(head)
            elif head=='drugbank_id':
                header_tool.append(':START_ID')
            else:
                header_tool.append(':END_ID')

        header_tool.append('license')
        header_tool.append(':TYPE')
        if first:
            writer_tool.writerow(header_tool)
            import_string += ' --relationships ' + tool_path
        query += '''license:"''' + drugbank_license + '''"}]->(g) ;\n'''
        cypher_rela_file.write(query)

        writer_output.writerow(header_new)
        for row in reader:
            drugbank_id = row['drugbank_id']
            uniprot_id = row['targets_id']
            target_db_id = row['targets_id_drugbank']
            if uniprot_id != '':
                target_id = uniprot_id
            else:
                target_id = target_db_id

            if not (drugbank_id, target_id) in dict_drug_targe_pairs_xml:
                dict_drug_targe_pairs_xml[(drugbank_id, target_id)] = [{}]
                for property_name, value in row.items():
                    if property_name == 'targets_id' and value == '':
                        dict_drug_targe_pairs_xml[(drugbank_id, target_id)][0][property_name] = target_db_id
                    else:
                        dict_drug_targe_pairs_xml[(drugbank_id, target_id)][0][property_name] = value

                if (drugbank_id, target_id) in dict_all_target_drug_pairs:
                    print('multi in different')
                    print(dict_all_target_drug_pairs[(drugbank_id, target_id)])
                    print(row)
                    list_before = dict_all_target_drug_pairs[(drugbank_id, target_id)]
                    different = False
                    # gather all information and compare the rela information with the other rela from the same pair
                    for property_name, value in row.items():
                        if property_name == 'targets_id' and value == '':
                            for property in list_before:
                                if target_db_id != property[property_name]:
                                    different = True
                        else:
                            for property in list_before:
                                if value != property[property_name]:
                                    different = True
                    # only add the rela with other information
                    if not different:
                        print('the same all types')
                else:
                    dict_all_target_drug_pairs[(drugbank_id, target_id)] = dict_drug_targe_pairs_xml[
                        (drugbank_id, target_id)]
            else:
                print('multi in one')
                print(dict_drug_targe_pairs_xml[(drugbank_id, target_id)])
                print(row)

                dict_drug_targe_pairs_xml_new = {}
                list_before = dict_drug_targe_pairs_xml[(drugbank_id, target_id)]
                different = False
                # gather all information and compare the rela information with the other rela from the same pair
                for property_name, value in row.items():
                    if property_name == 'targets_id' and value == '':
                        dict_drug_targe_pairs_xml_new[property_name] = target_db_id
                        for property in list_before:
                            if target_db_id != property[property_name]:
                                different = True
                    else:
                        dict_drug_targe_pairs_xml_new[property_name] = value
                        for property in list_before:
                            if value != property[property_name]:
                                different = True
                # only add the rela with other information
                if different:
                    dict_drug_targe_pairs_xml[(drugbank_id, target_id)].append(dict_drug_targe_pairs_xml_new)
                    dict_all_target_drug_pairs[(drugbank_id, target_id)] = dict_drug_targe_pairs_xml[
                        (drugbank_id, target_id)]
                else:
                    sys.exit('the same')

    counter_not = 0
    for (drug, uniprot_id) in dict_drug_targets_sequence.keys():
        if not (drug, uniprot_id) in dict_drug_targe_pairs_xml:
            print('sequence pair not in xml:' + drug + ' ' + uniprot_id)
            counter_not += 1
            # sys.exit('sequence pair not in xml:'+drug+' '+uniprot_id)
    print(counter_not)
    counter_not = 0
    for (drug, uniprot_id) in dict_drug_targets_pharmacologically_active_identifier.keys():
        if not (drug, uniprot_id) in dict_drug_targe_pairs_xml:
            print('pharmacologically pair not in xml:' + drug + ' ' + uniprot_id)
            counter_not += 1
        else:
            for properties in dict_drug_targe_pairs_xml[(drug, uniprot_id)]:
                if properties['known_action'] != 'yes' and \
                        dict_drug_targets_pharmacologically_active_identifier[(drug, uniprot_id)] != \
                        properties['organism']:
                    sys.exit('actions')
                # sys.exit('sequence pair not in xml:'+drug+' '+uniprot_id)
    print(counter_not)
    counter_not = 0
    for (drug, uniprot_id) in dict_drug_targets_identifier.keys():
        if not (drug, uniprot_id) in dict_drug_targe_pairs_xml:
            print('identifier pair not in xml:' + drug + ' ' + uniprot_id)
            counter_not += 1
            # sys.exit('sequence pair not in xml:'+drug+' '+uniprot_id)
    print(counter_not)
    counter_not = 0
    for (drug, uniprot_id) in dict_drug_targets_external.keys():
        if not (drug, uniprot_id) in dict_drug_targe_pairs_xml:
            print('external pair not in xml:' + drug + ' ' + uniprot_id)
            counter_not += 1
            # sys.exit('sequence pair not in xml:'+drug+' '+uniprot_id)
    print(counter_not)

    counter_total_relationships = 0
    for (drug, target_id), properties in dict_drug_targe_pairs_xml.items():
        for property in properties:
            output_list = []
            counter_total_relationships += 1
            output_tool=[]
            for head in header:
                if head == 'targets_id_drugbank':
                    continue
                if head in list_properties:
                    splitted_property= property[head].split('||')
                    string_property=''
                    for part_property in splitted_property:
                        part_property=part_property.replace(';',',')
                        string_property+=part_property+';'
                    output_tool.append(string_property[0:-1])
                else:
                    output_tool.append(property[head])
                output_list.append(property[head])
            output_tool.append(drugbank_license)
            output_tool.append('associate_with_Caw' + short_form_label)
            writer_output.writerow(output_list)
            writer_tool.writerow(output_tool)
    print('total number of relationships:' + str(counter_total_relationships))
    output_file.close()


def gather_and_combine_carrier_information(uniprot_links, drugbank_all_polypeptide_sequences_fasta,
                                           drugbank_all_polypeptide_ids_csv, drugbank_target_tsv,
                                           drugbank_target_output_tsv, drugbank_drug_target_tsv, neo4j_label,
                                           neo4j_label_drug, short_form_label, neo4j_general_label,first):
    # check for carrier

    # file external links carrier

    dict_drug_target_external = {}
    dict_target_info_external = {}

    print (datetime.datetime.utcnow())
    print('gather  information from uniprot_links')

    # this take all information from drug links.csv
    external_links_for_all_drug_targets(uniprot_links, dict_drug_target_external, dict_target_info_external)

    print('number of drug-target pairs:' + str(len(dict_drug_target_external)))
    print('number of targets:' + str(len(dict_target_info_external)))

    # file sequences target

    dict_drug_target_sequence = {}
    dict_target_info_sequence = {}

    print (datetime.datetime.utcnow())
    print('gather  information from polypeptide sequence')

    # this take all information from drug links.csv
    sequences_for_all_targets(path_to_target_sequence + drugbank_all_polypeptide_sequences_fasta,
                              dict_drug_target_sequence, dict_target_info_sequence)

    # print(dict_drug_target_sequence)
    print('number of drug-target pairs:' + str(len(dict_drug_target_sequence)))
    print('number of targets:' + str(len(dict_target_info_sequence)))

    # file sequences target

    dict_drug_target_identifier = {}
    dict_drug_target_pharmacologically_active_identifier = {}
    dict_target_info_identifier = {}

    print (datetime.datetime.utcnow())
    print('gather  information from polypeptide_ids')

    # this take all information from drug links.csv
    identifier_for_all_targets(path_to_protein_identifier + drugbank_all_polypeptide_ids_csv,
                               dict_drug_target_identifier, dict_target_info_identifier,
                               dict_drug_target_pharmacologically_active_identifier)

    print('number of drug-target pairs:' + str(len(dict_drug_target_identifier)))
    print('number of drug-target pharmacologically active pairs:' + str(
        len(dict_drug_target_pharmacologically_active_identifier)))
    print('number of targets:' + str(len(dict_target_info_identifier)))

    print (datetime.datetime.utcnow())
    print('compare and generate new target file')

    # check and if necessary generate a combined new file
    header_new = check_and_maybe_generate_a_new_target_file('drugbank/' + drugbank_target_tsv,
                                                            dict_target_info_external,
                                                            dict_target_info_sequence, dict_target_info_identifier,
                                                            'output/' + drugbank_target_output_tsv, neo4j_label,
                                                            neo4j_general_label)

    print (datetime.datetime.utcnow())
    print('compare and generate new drug-target file')

    # check and if necessary generate combined file for rela drug-target
    check_and_maybe_generate_a_new_drug_target_file('drugbank/' + drugbank_drug_target_tsv, dict_drug_target_external,
                                                    dict_drug_target_sequence, dict_drug_target_identifier,
                                                    dict_drug_target_pharmacologically_active_identifier,
                                                    neo4j_label_drug, neo4j_label, short_form_label,first)

    return header_new


#########################################################################################################

# dictionary with all metabolites from the reaction file
dict_with_all_metabolite_from_reactions = {}

'''
this go through the reaction file and take all metabolite ids
'''


def load_reaction_file_in(neo4j_label_metabolite, neo4j_label_drug):
    with open('drugbank/drugbank_reactions.tsv') as csvfile:
        global import_string
        spamreader = csv.DictReader(csvfile, delimiter='\t')
        header = spamreader.fieldnames

        file_path_drug_drug = 'output/drugbank_reaction_compound_compound.tsv'
        file_path_drug_meta = 'output/drugbank_reaction_compound_metabolites.tsv'
        file_path_meta_drug = 'output/drugbank_reaction_metabolites_compound.tsv'
        file_path_meta_meta = 'output/drugbank_reaction_metabolites_metabolites.tsv'

        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + file_path_meta_meta + '''" As line FIELDTERMINATOR '\\t' Match (c:''' + neo4j_label_metabolite \
                + '''{ identifier: line.left_element_drugbank_id}), (g:''' + neo4j_label_metabolite + '''{ identifier:line.right_element_drugbank_id })  Create (c)-[a:reacts_with_MrwM{sequence:line.sequence, enzymes:split(line.enzymes,'||'),license:"''' + drugbank_license + '''"}]->(g) ;\n'''
        cypher_rela_file.write(query)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + file_path_meta_drug + '''" As line FIELDTERMINATOR '\\t' Match (c:''' + neo4j_label_metabolite \
                + '''{ identifier: line.left_element_drugbank_id}), (g:''' + neo4j_label_drug + '''{ identifier:line.right_element_drugbank_id })  Create (c)-[a:reacts_with_MrwC{sequence:line.sequence, enzymes:split(line.enzymes,'||'),license:"''' + drugbank_license + '''"}]->(g) ;\n'''
        cypher_rela_file.write(query)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + file_path_drug_drug + '''" As line FIELDTERMINATOR '\\t' Match (c:''' + neo4j_label_drug \
                + '''{ identifier: line.left_element_drugbank_id}), (g:''' + neo4j_label_drug + '''{ identifier:line.right_element_drugbank_id })  Create (c)-[a:reacts_with_CrwC{sequence:line.sequence, enzymes:split(line.enzymes,'||'),license:"''' + drugbank_license + '''"}]->(g) ;\n'''
        cypher_rela_file.write(query)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + file_path_drug_meta + '''" As line FIELDTERMINATOR '\\t' Match (c:''' + neo4j_label_drug \
                + '''{ identifier: line.left_element_drugbank_id}), (g:''' + neo4j_label_metabolite + '''{ identifier:line.right_element_drugbank_id })  Create (c)-[a:reacts_with_CrwM{sequence:line.sequence, enzymes:split(line.enzymes,'||'),license:"''' + drugbank_license + '''"}]->(g) ;\n'''
        cypher_rela_file.write(query)

        output_file_drug_drug = open(file_path_drug_drug, 'w')
        writer_drug_drug = csv.writer(output_file_drug_drug, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_file_drug_meta = open(file_path_drug_meta, 'w')
        writer_drug_meta = csv.writer(output_file_drug_meta, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_file_meta_meta = open(file_path_meta_meta, 'w')
        writer_meta_meta = csv.writer(output_file_meta_meta, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        output_file_meta_drug = open(file_path_meta_drug, 'w')
        writer_meta_drug = csv.writer(output_file_meta_drug, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        header = list(header)
        writer_drug_drug.writerow(header)
        writer_drug_meta.writerow(header)
        writer_meta_meta.writerow(header)
        writer_meta_drug.writerow(header)

        header_tool=[]
        for head in header:
            if head=='left_element_drugbank_id':
                header_tool.append(':START_ID')
            elif head=='right_element_drugbank_id':
                header_tool.append(':END_ID')
            else:
                header_tool.append(head+':string[]')
        header_tool.append('license')
        header_tool.append(':TYPE')

        tool_path='output/neo4j_import/drugbank_reactions.tsv'
        csv_tool=open(tool_path,'w')
        import_string += ' --relationships ' + tool_path
        writer_tool= csv.writer(csv_tool, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer_tool.writerow(header_tool)
        dict_reactions = {}

        for row in spamreader:
            left_id = row['left_element_drugbank_id']
            right_id = row['right_element_drugbank_id']
            # if left_id[0:5] == 'DBMET':
            #     if not left_id in dict_with_all_metabolite_from_reactions:
            #         dict_with_all_metabolite_from_reactions[left_id] = ''
            # if right_id[0:5] == 'DBMET':
            #     if not right_id in dict_with_all_metabolite_from_reactions:
            #         dict_with_all_metabolite_from_reactions[right_id] = ''
            line_information = []
            enzymes_list = row['enzymes']
            if (left_id, right_id) in dict_reactions:
                dict_reactions[(left_id, right_id)].append({'sequence': row['sequence'], 'enzymes': row['enzymes']})
            else:
                dict_reactions[(left_id, right_id)] = [{'sequence': row['sequence'], 'enzymes': row['enzymes']}]

        dict_counter = {'drug_drug': 0,
                        'drug_meta': 0,
                        'meta_drug': 0,
                        'meta_meta': 0}
        for (left_id, right_id), list_properties in dict_reactions.items():
            sequence_list = set([])
            enzymes_list = set([])
            for dict_property in list_properties:
                sequence_list.add(dict_property['sequence'])
                enzymes_list = enzymes_list.union(dict_property['enzymes'].split('||'))

            sequence_list_tool=';'.join(list(sequence_list))
            enzymes_list_tool = ';'.join(list(enzymes_list))
            sequence_list = '||'.join(list(sequence_list))
            enzymes_list = '||'.join(list(enzymes_list))
            line_information = [sequence_list, left_id, right_id, enzymes_list]
            line_information_tool=[sequence_list_tool, left_id,right_id,enzymes_list_tool,drugbank_license]

            if left_id[0:5] != 'DBMET' and right_id[0:5] == 'DBMET':
                writer_drug_meta.writerow(line_information)
                line_information_tool.append('reacts_with_CrwM')
                if left_id in dict_drugbank_drug_ids:
                    writer_tool.writerow(line_information_tool)
                dict_counter['drug_meta'] += 1
            elif left_id[0:5] != 'DBMET' and right_id[0:5] != 'DBMET':
                writer_drug_drug.writerow(line_information)
                line_information_tool.append('reacts_with_CrwC')
                if left_id in dict_drugbank_drug_ids and right_id in dict_drugbank_drug_ids:
                    writer_tool.writerow(line_information_tool)
                dict_counter['drug_drug'] += 1
            elif left_id[0:5] == 'DBMET' and right_id[0:5] == 'DBMET':
                writer_meta_meta.writerow(line_information)
                line_information_tool.append('reacts_with_MrwM')
                writer_tool.writerow(line_information_tool)
                dict_counter['meta_meta'] += 1
            else:
                writer_meta_drug.writerow(line_information)
                line_information_tool.append('reacts_with_MrwC')
                if right_id in dict_drugbank_drug_ids:
                    writer_tool.writerow(line_information_tool)
                dict_counter['meta_drug'] += 1

        print(dict_counter)

    with open('drugbank/drugbank_metabolites.tsv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter='\t')
        for row in spamreader:
            dict_with_all_metabolite_from_reactions[row['drugbank_id']] = row['name']

    print('number of metabolites in reaction file:' + str(len(dict_with_all_metabolite_from_reactions)))


'''
this go through the reaction file and take all metabolite ids
'''


def gather_all_metabolite_information_and_generate_a_new_file(neo4j_label):
    output_file_drug = open('output/drugbank_metabolites.tsv', 'w')
    writer_drug = csv.writer(output_file_drug, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    with open('sdf/metabolite_structure_combined.csv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',')
        header = reader.fieldnames
        header_new = header[:]
        header_new.remove('')
        header_new.remove('ID')
        header_new.remove('Molecule')
        header_new.remove('DATABASE_NAME')
        header_new.remove('DATABASE_ID')
        header_new.remove('DRUGBANK_ID')

        header_new.insert(0, 'DRUGBANK_ID')
        header_new = [x.lower() for x in header_new]
        writer_drug.writerow(header_new)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/output/drugbank_metabolites.tsv" As line FIELDTERMINATOR '\\t' Create (b:''' + neo4j_label + '''{ '''
        for head in header_new:
            if head == 'drugbank_id':
                query += '''identifier:line.''' + head + ', '
            else:
                query += head + ':line.' + head + ', '

        query = query + '''license:"''' + drugbank_license + '''"});\n'''
        cypher_file.write(query)
        cypher_file.write(':begin\n')
        cypher_file.write('Create Constraint On (node:Metabolite_DrugBank) Assert node.identifier Is Unique;\n')
        cypher_file.write(':commit\n')
        header_new = [x.upper() for x in header_new]
        counter_not_in = 0
        dict_sfd_metabolite_ids = {}
        for row in reader:

            drugbank_metabolite_id = row['DRUGBANK_ID']

            dict_sfd_metabolite_ids[drugbank_metabolite_id] = ''
            if drugbank_metabolite_id not in dict_with_all_metabolite_from_reactions:
                print(drugbank_metabolite_id)
                counter_not_in += 1
            else:
                if dict_with_all_metabolite_from_reactions[drugbank_metabolite_id] != row['NAME']:
                    print(drugbank_metabolite_id)
                    name = dict_with_all_metabolite_from_reactions[drugbank_metabolite_id]
                    print(dict_with_all_metabolite_from_reactions[drugbank_metabolite_id])
                    print(row['NAME'])
                    # sys.exit('not the same name')
            entries = []
            for head in header_new:
                entries.append(row[head])
            writer_drug.writerow(entries)

        print(';):)++++++++++++++++++')
        counter_metabolites_in_xml_and_not_in_sdf = 0
        for db_metabolite_id in dict_with_all_metabolite_from_reactions.keys():
            if not db_metabolite_id in dict_sfd_metabolite_ids:
                counter_metabolites_in_xml_and_not_in_sdf += 1
                print(db_metabolite_id)
                entries = []

                for head in header_new:
                    if head not in ['DRUGBANK_ID', 'NAME']:
                        entries.append('')
                    elif head == 'DRUGBANK_ID':
                        entries.append(db_metabolite_id)
                    else:
                        entries.append(dict_with_all_metabolite_from_reactions[db_metabolite_id])

                writer_drug.writerow(entries)

        print('number of metabolite which are not in the reaction file:' + str(counter_not_in))
        print('number of metabolites which are not in the sdf file:' + str(counter_metabolites_in_xml_and_not_in_sdf))

    output_file_drug.close()
    print('metabolite')
    import_tool_preparation_node('output/drugbank_metabolites.tsv','drugbank_id',neo4j_label)


'''
add the load files for the files which do not need a update into cypher file
'''


def add_general_to_cypher_node(path, label, special_name):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + path + '''" As line FIELDTERMINATOR '\\t' Create (b:''' + label + '''{ '''
        for head in header:
            if head == special_name:
                query += 'identifier: line.' + head + ', '
            else:
                query += head + ':line.' + head + ', '

        query = query + '''license:"''' + drugbank_license + '''"});\n'''
        cypher_file.write(query)
        cypher_file.write(':begin\n')
        cypher_file.write('Create Constraint On (node:' + label + ') Assert node.identifier Is Unique;\n')
        cypher_file.write(':commit\n')


'''
add to cypher rela file the relationships without pre-preparation  
'''


def add_rela_to_cypher(path, label_left, label_right, id_name_left, id_name_right, rela_label):
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames

        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/''' + path + '''" As line FIELDTERMINATOR '\\t' Match (b:''' + label_left + '''{ identifier: line.''' + id_name_left + '''}),'''
        query += '''(c:''' + label_right + '''{ identifier: line.''' + id_name_right + '''}) Create (b)-[:''' + rela_label + '''{'''
        for head in header:
            if head not in [id_name_right, id_name_left]:
                query += head + ':line.' + head + ', '

        query = query + '''license:"''' + drugbank_license + '''"}]->(c);\n'''
        cypher_rela_file.write(query)


'''
prepare the import file for nodes
'''


def import_tool_preparation_node(file_path, id_name, labels):
    global import_string
    output_file = open('output/neo4j_import/' + file_path.split('/')[1], 'w')
    import_string += ' --nodes ' + 'output/neo4j_import/' + file_path.split('/')[1]
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header = reader.fieldnames
        new_header = []
        for head in header:
            if head == id_name:
                new_header.append('identifier:ID')
            else:
                new_header.append(head)
        new_header.append('license')
        new_header.append(':LABEL')
        writer.writerow(new_header)
        if type(labels)==list:
            labels = ';'.join(labels)
        row_counter=0
        for row in reader:
            row_counter+=1
            new_entry = []
            for head in header:
                new_entry.append(row[head])

            new_entry.append(drugbank_license)
            new_entry.append(labels)
            writer.writerow(new_entry)
        print('number of rows:'+str(row_counter))


'''
prepare the import file for nodes and generate the a new connect target to mutated gene/protein
'''


def import_tool_preparation_new_generated_rela(file_path, labels, label_targer, label_mutated_gene_protein):
    global import_string
    file_name='drugbank_target_mutated.tsv'
    output_file = open('output/neo4j_import/'+file_name, 'w')

    import_string += ' --relationships ' + 'output/neo4j_import/' + file_name

    header_name_target='target_id'
    header_name_mutated='mutated_id'
    writer_tool = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    output_file_cypher = open('output/' + file_name, 'w')
    writer = csv.writer(output_file_cypher, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([header_name_target, header_name_mutated])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/drugbank/output/''' + file_name + '''" As line FIELDTERMINATOR '\\t' Match (b:''' + label_targer + '''{ identifier: line.''' + header_name_target + '''}),'''
    query += '''(c:''' + label_mutated_gene_protein + '''{ identifier: line.''' + header_name_mutated + '''}) Create (b)-[:''' + labels + ''']->(c);\n'''
    cypher_rela_file.write(query)

    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer_tool.writerow([':START_ID',':END_ID',':TYPE'])

        for row in reader:
            uniprot_id=row['uniprot_id']
            if uniprot_id in dict_all_targets:
                connection_id=row['connection_id']
                writer_tool.writerow([uniprot_id,connection_id,labels])
                writer.writerow([uniprot_id, connection_id])



'''
generate cypher file to integrate all DrugBank entries into Neo4j
'''


def add_the_other_node_to_cypher(pathway_label, product_label, salt_label, mutated_enzyme_gene_label,general_target_label,rela_target_muta_label):
    path_pathway = 'drugbank/drugbank_pathway.tsv'
    import_tool_preparation_node(path_pathway,'pathway_id',pathway_label)
    add_general_to_cypher_node(path_pathway, pathway_label, 'pathway_id')

    path_salt = 'drugbank/drugbank_salt.tsv'
    import_tool_preparation_node(path_salt, 'id', salt_label)
    add_general_to_cypher_node(path_salt, salt_label, 'id')

    path_product = 'drugbank/drugbank_products.tsv'
    import_tool_preparation_node(path_product, 'id', product_label)
    add_general_to_cypher_node(path_product, product_label, 'id')

    path_mutated_gene_enzyme = 'drugbank/drugbank_mutated_gene_enzyme.tsv'
    import_tool_preparation_node(path_mutated_gene_enzyme, 'connection_id', mutated_enzyme_gene_label)
    add_general_to_cypher_node(path_mutated_gene_enzyme, mutated_enzyme_gene_label, 'connection_id')
    import_tool_preparation_new_generated_rela(path_mutated_gene_enzyme,  rela_target_muta_label,general_target_label, mutated_enzyme_gene_label)

'''
generate files for import tool for rela
'''
def generation_of_files_for_import_tool(left_label,right_label, input_path,neo4j_label):
    global import_string
    output_file = open('output/neo4j_import/' + input_path.split('/')[1], 'w')
    import_string += ' --relationships ' + 'output/neo4j_import/' + input_path.split('/')[1]
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    with open(input_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header = reader.fieldnames
        new_header = []
        for head in header:
            if head == left_label:
                new_header.append(':START_ID')
            elif head==right_label:
                new_header.append(':END_ID')
            else:
                new_header.append(head)
        new_header.append('license')
        new_header.append(':TYPE')
        writer.writerow(new_header)
        row_counter = 0
        for row in reader:
            row_counter += 1
            new_entry = []
            for head in header:
                new_entry.append(row[head])

            new_entry.append(drugbank_license)
            new_entry.append(neo4j_label)
            writer.writerow(new_entry)
        print('number of rows:' + str(row_counter))

'''
generate files for import tool for rela for drug drug interaction
'''
def generation_of_files_for_import_tool_interaction(left_label,right_label, input_path,neo4j_label):
    global import_string
    output_file = open('output/neo4j_import/' + input_path.split('/')[1], 'w')
    import_string += ' --relationships ' + 'output/neo4j_import/' + input_path.split('/')[1]
    writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    with open(input_path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        header = reader.fieldnames
        new_header = []
        for head in header:
            if head == left_label:
                new_header.append(':START_ID')
            elif head==right_label:
                new_header.append(':END_ID')
            else:
                new_header.append(head)
        new_header.append('license')
        new_header.append(':TYPE')
        writer.writerow(new_header)
        row_counter = 0
        for row in reader:
            row_counter += 1
            new_entry = []
            db_id1=row[left_label]
            db_id2 = row[right_label]
            if db_id1 not in dict_drugbank_drug_ids or db_id2 not in dict_drugbank_drug_ids:
                continue
            for head in header:
                new_entry.append(row[head])

            new_entry.append(drugbank_license)
            new_entry.append(neo4j_label)
            writer.writerow(new_entry)
        print('number of rows:' + str(row_counter))


dict_not_existing_db = {}

dict_existing_db = {}

'''
generate cypher script for the different relationships, where nothing need to check.
'''


def add_the_other_rela_to_cypher(pathway_label, product_label, salt_label, mutated_enzyme_gene_label, drug_label,
                                 general_label, enzyme_label, header_new):
    global import_string
    # all labe for all rela in neo4j
    label_neo4j_compound_product = 'part_of_CpoP'
    label_neo4j_compound_pathway='associates_with_CawPA'
    label_neo4j_compound_salt='has_ChS'
    label_neo4j_compound_mutaded='combination_causes_adrs_CccaMU'
    label_neo4j_interaction='interacts_CiC'
    label_neo4j_enzyme_pathway='participates_EpPA'
    label_neo4j_target_peptide='has_component_PIhcPI'

    path_drug_pathway = 'drugbank/drugbank_drug_pathway.tsv'
    add_rela_to_cypher(path_drug_pathway, drug_label, pathway_label, 'drugbank_id', 'pathway_id',
                       label_neo4j_compound_pathway)
    generation_of_files_for_import_tool('drugbank_id', 'pathway_id',path_drug_pathway,label_neo4j_compound_pathway)

    path_drug_salt = 'drugbank/drugbank_drug_salt.tsv'
    add_rela_to_cypher(path_drug_salt, drug_label, salt_label, 'drug_id', 'salt_id',
                       label_neo4j_compound_salt)
    generation_of_files_for_import_tool('drug_id', 'salt_id', path_drug_salt, label_neo4j_compound_salt)

    path_drug_product = 'drugbank/drugbank_drug_products.tsv'
    add_rela_to_cypher(path_drug_product, drug_label, product_label, 'drugbank_id', 'partner_id',
                       label_neo4j_compound_product)
    generation_of_files_for_import_tool('drugbank_id', 'partner_id', path_drug_product, label_neo4j_compound_product)

    path_drug_mutated_gen_enzyme = 'drugbank/drugbank_snp_effects.tsv'
    add_rela_to_cypher(path_drug_mutated_gen_enzyme, drug_label, mutated_enzyme_gene_label, 'drugbank_id', 'partner_id',
                       label_neo4j_compound_mutaded)
    generation_of_files_for_import_tool('drugbank_id', 'partner_id', path_drug_mutated_gen_enzyme, label_neo4j_compound_mutaded)

    path_drug_mutated_gen_enzyme = 'drugbank/drugbank_snp_adverse_drug_reaction.tsv'
    add_rela_to_cypher(path_drug_mutated_gen_enzyme, drug_label, mutated_enzyme_gene_label, 'drugbank_id', 'partner_id',
                       label_neo4j_compound_mutaded)
    generation_of_files_for_import_tool('drugbank_id', 'partner_id', path_drug_mutated_gen_enzyme, label_neo4j_compound_mutaded)

    path_drug_drug = 'drugbank/drugbank_interaction.tsv'
    add_rela_to_cypher(path_drug_drug, drug_label, drug_label, 'DB_ID1', 'DB_ID2',
                       label_neo4j_interaction)
    generation_of_files_for_import_tool_interaction('DB_ID1', 'DB_ID2', path_drug_drug,
                                        label_neo4j_interaction)

    path_pathway_enzyme = 'drugbank/drugbank_pathway_enzymes.tsv'
    add_rela_to_cypher(path_pathway_enzyme, general_label, pathway_label, 'uniprot_id', 'pathway_id',
                       label_neo4j_enzyme_pathway)

    csvfile = open('output/drugbank_Enzyme_DrugBank_2.tsv', 'w')
    spamreader = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    tool_path='output/neo4j_import/drugbank_enzyme.tsv'
    file_tool_output=open(tool_path,'w')
    import_string += ' --nodes ' + tool_path
    spamreader_node = csv.writer(file_tool_output, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamreader_node.writerow(['identifier:ID','license',':LABEL'])

    tool_path='output/neo4j_import/drugbank_enzyme_pathway.tsv'
    file_tool_output_rela = open(tool_path, 'w')
    import_string += ' --relationships ' + tool_path
    spamreader_rela = csv.writer(file_tool_output_rela, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    spamreader_rela.writerow([':START_ID',':END_ID','license',':TYPE'])

    count_not_existin_interaction_pairs = 0
    counter_all = 0
    counter_existing = 0
    position_of_id = header_new.index('id')
    length_list = len(header_new)
    with open(path_pathway_enzyme) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            counter_all += 1
            pathway_id = row['pathway_id']
            uniprot_id = row['uniprot_id']
            spamreader_rela.writerow([uniprot_id,pathway_id,drugbank_license,label_neo4j_enzyme_pathway])
            if uniprot_id == ' O49347':
                print('ohm')
                print(uniprot_id)
            if not uniprot_id in dict_all_targets:
                count_not_existin_interaction_pairs += 1
                dict_all_targets[uniprot_id] = 1
                entries = ['' for i in range(length_list)]
                entries[position_of_id] = uniprot_id
                spamreader.writerow(entries)
                spamreader_node.writerow([uniprot_id,drugbank_license,enzyme_label+';'+general_label])
                continue

            counter_existing += 1

    csvfile.close()
    print('all interation rela:' + str(counter_all))
    print('number of not integrated interaction:' + str(count_not_existin_interaction_pairs))
    print('all existing interaction:' + str(counter_existing))

    path_target_peptides = 'drugbank/drugbank_target_peptide_has_component.tsv'
    add_rela_to_cypher(path_target_peptides, general_label, general_label, 'target_id', 'petide_id',
                       label_neo4j_target_peptide)
    generation_of_files_for_import_tool('target_id', 'petide_id', path_target_peptides,
                                        label_neo4j_target_peptide)



'''
organised all steps for metabolites
'''


def get_and_check_on_drugbank_metabolites(neo4j_label_meatbolite, neo4j_label_drug):
    print('load reaction file')
    load_reaction_file_in(neo4j_label_meatbolite, neo4j_label_drug)

    gather_all_metabolite_information_and_generate_a_new_file(neo4j_label_meatbolite)

'''
generate shell script for neo4j-admin import
'''
def generate_shell_script():
    file=open('script_import_tool.sh','w')
    file.write('#!/bin/bash\n\n')
    file.write(import_string)



def main():
    # create_connection_with_neo4j_mysql()
    print (datetime.datetime.utcnow())
    print('drug')

    neo4j_label_drug = 'Compound_DrugBank'

    drugs_combination_and_check(neo4j_label_drug)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('carrier')

    #to open a blank file
    open('output/neo4j_import/drug_target.tsv', 'w')

    neo4j_general_label = 'Protein_DrugBank'
    neo4j_label_carrier = 'Carrier_DrugBank'
    gather_and_combine_carrier_information('uniprot_links_carrier.csv',
                                           'drugbank_all_carrier_polypeptide_sequences.fasta/',
                                           'drugbank_all_carrier_polypeptide_ids.csv/', 'drugbank_carrier.tsv',
                                           'drugbank_carrier.tsv', 'drugbank_drug_carrier.tsv', neo4j_label_carrier,
                                           neo4j_label_drug, 'CA', neo4j_general_label,True)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('enzymes')

    neo4j_label_enzyme = 'Enzyme_DrugBank'
    gather_and_combine_carrier_information('uniprot_links_enzyme.csv',
                                           'drugbank_all_enzyme_polypeptide_sequences.fasta/',
                                           'drugbank_all_enzyme_polypeptide_ids.csv/', 'drugbank_enzymes.tsv',
                                           'drugbank_enzymes.tsv', 'drugbank_drug_enzyme.tsv', neo4j_label_enzyme,
                                           neo4j_label_drug, 'E', neo4j_general_label,False)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('target')

    neo4j_label_target = 'Target_DrugBank'
    gather_and_combine_carrier_information('uniprot_links_target.csv',
                                           'drugbank_all_target_polypeptide_sequences.fasta/',
                                           'drugbank_all_target_polypeptide_ids.csv/', 'drugbank_targets.tsv',
                                           'drugbank_targets.tsv', 'drugbank_drug_target.tsv', neo4j_label_target,
                                           neo4j_label_drug, 'T', neo4j_general_label,False)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('transporter')

    neo4j_label_transporter = 'Transporter_DrugBank'
    header_new = gather_and_combine_carrier_information('uniprot_links_transporter.csv',
                                                        'drugbank_all_transporter_polypeptide_sequences.fasta/',
                                                        'drugbank_all_transporter_polypeptide_ids.csv/',
                                                        'drugbank_transporter.tsv',
                                                        'drugbank_transporter.tsv', 'drugbank_drug_transporter.tsv',
                                                        neo4j_label_transporter, neo4j_label_drug, 'TR',
                                                        neo4j_general_label,False)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('general')
    output = 'output/'
    generate_combined_csv_files(header_new, neo4j_general_label,
                                [neo4j_label_target, neo4j_label_enzyme, neo4j_label_transporter, neo4j_label_carrier])

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('metabolites')

    neo4j_label_metabolite = 'Metabolite_DrugBank'
    get_and_check_on_drugbank_metabolites(neo4j_label_metabolite, neo4j_label_drug)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('other_nodes_without_update')

    neo4j_label_pathway = 'Pathway_DrugBank'
    neo4j_label_product = 'Product_DrugBank'
    neo4j_label_salt = 'Salt_DrugBank'
    neo4j_label_mutated_gene_enzyme = 'Mutated_enzyme_gene_DrugBank'
    neo4j_label_rela_target_mutate='has_PIhMU'

    add_the_other_node_to_cypher(neo4j_label_pathway, neo4j_label_product, neo4j_label_salt,
                                 neo4j_label_mutated_gene_enzyme,neo4j_general_label,neo4j_label_rela_target_mutate)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('other rela without update')

    add_the_other_rela_to_cypher(neo4j_label_pathway, neo4j_label_product, neo4j_label_salt,
                                 neo4j_label_mutated_gene_enzyme, neo4j_label_drug, neo4j_general_label, neo4j_label_enzyme, header_new)

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('generate shell script')

    generate_shell_script()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
