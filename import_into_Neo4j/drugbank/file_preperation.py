# this file go through all csv,fasta and sdf filed from the DrugBank download site and test  if the information are already
# in the xml file or not. Also if some information are not included then they are combinded withe the other files.

import sys, io
import os, csv
from Bio import SeqIO
from itertools import groupby
import datetime, time

# encoding=utf8
reload(sys)
sys.setdefaultencoding('utf8')

# increase the csv max size
maxInt = sys.maxsize
decrement = True

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

def drugs_combination_and_check():

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

    print (datetime.datetime.utcnow())
    print('missing structure sdf')

    print (datetime.datetime.utcnow())
    print('check and combine the different information source with the xml source in an new file')
    # test if the sequence and the external identifier are the same and when something is not in the xml it is add
    # therefore a new file is generated
    # currently only the uniprot title are add to synonyms
    with open(path_prepared_drugbank_files + '/drugbank_drug.tsv') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        output_file_drug = open('output/drugbank_drug.csv', 'w')
        writer_drug = csv.writer(output_file_drug, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer_drug.writerow(header)
        counter_uniprot_title = 0
        for row in reader:
            drugbank_id = row['\xef\xbb\xbfdrugbank_id']
            name = row['name']
            cas_number = row['cas_number']
            drug_type = row['type'].replace(' ', '')
            external_identifier = row['external_identifiers'].split('|') if row['external_identifiers'] != '' else []
            dict_external = {}
            synonyms = row['synonyms'].split('|') if not row['synonyms'] == '' else []
            for line in external_identifier:
                if line.split(':', 1)[0] in dict_external:
                    dict_external[line.split(':', 1)[0]].append(line.split(':', 1)[1])
                else:
                    dict_external[line.split(':', 1)[0]] = [line.split(':', 1)[1]]
            external_identifier_links = row['external-links_resource_url'].split('|') if row[
                                                                                             'external-links_resource_url'] != '' else []
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
                    synonyms.append(value)
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

            if drugbank_id in dict_drug_structure_links:
                dict_from_drug = dict_drug_structure_links[drugbank_id]
                groups = row['groups'].split('|')
                # experimental-properties_kind_value_source
                dict_experimental_property_value = {}
                experimental_property_value = row['experimental-properties_kind_value_source'].split('|') if row[
                                                                                                                 'experimental-properties_kind_value_source'] != '' else []
                for property_value_source in experimental_property_value:
                    split_prop_value_source = property_value_source.split('::')
                    if split_prop_value_source[0] in dict_experimental_property_value:
                        print('ohje')
                        sys.exit('experimental property')
                    else:
                        dict_experimental_property_value[split_prop_value_source[0]] = split_prop_value_source[1]

                calculated_property_value = row['calculated-properties_kind_value_source'].split('|') if row[
                                                                                                             'calculated-properties_kind_value_source'] != '' else []
                dict_calculated_property_value = {}
                for property_value_source in calculated_property_value:
                    split_prop_value_source = property_value_source.split('::')
                    if split_prop_value_source[0] in dict_calculated_property_value:
                        dict_calculated_property_value[split_prop_value_source[0]].append(split_prop_value_source[1])
                    else:
                        dict_calculated_property_value[split_prop_value_source[0]] = [split_prop_value_source[1]]

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

            # currently no problem with sequences
            if drugbank_id in dict_drug_sequence:
                sequences = row['sequences'].split('|') if row['sequences'] != '' else []
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
            output_list = []
            for head in header:
                if head != 'synonyms':
                    output_list.append(row[head])
                else:
                    string_synonyms = '|'.join(synonyms)
                    output_list.append(string_synonyms)
            writer_drug.writerow(output_list)

        print('number of new synonyms:' + str(counter_uniprot_title))

    # to reduce the memory
    dict_drug_sequence = {}
    dict_drug_external_ids = {}
    dict_drug_structure_links = {}

###################################################################################################################

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
        name = header.split('|')[1].split(' ', 1)[1].rsplit(' (',1)[0]
        db_ids = header.rsplit('(',1)[1].replace(')', '').split('; ')


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
    work_with_target_sequence_fasta(directory, 'gene.fasta', 'gene-sequence', dict_targets, dict_drug_targets)
    work_with_target_sequence_fasta(directory, 'protein.fasta', 'amino-acid-sequence', dict_targets, dict_drug_targets)


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
                if head not in ['ID', 'UniProt ID', 'Drug IDs','Species']:
                    dict_target_info[head] = row[head].split('; ') if row[head] != '' else []
            if uniprot_id not in dict_targets:
                dict_targets[uniprot_id] = dict_target_info
            else:
                for head in header:
                    if head not in ['ID', 'UniProt ID', 'Drug IDs','Species']:
                        values= row[head].split('; ') if row[head] != '' else []
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
dict_target_change_xrefs_name={
    'GenAtlas ID':'GenAtlas',
    'GenBank Gene ID':'GenBank Gene Database',
    'GenBank Protein ID':'GenBank Protein Database',
    'HGNC ID':'HUGO Gene Nomenclature Committee (HGNC)'
}

'''
check the information from the different csv for the target files with the from the xml 
'''


def check_and_maybe_generate_a_new_target_file(file, dict_targets_info_external, dict_targets_info_sequence,
                                               dict_targets_info_identifier,output_file):
    with open(file) as csvfile:
        print(file)
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        output_file_csv=open(output_file,'w')
        writer_output = csv.writer(output_file_csv, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer_output.writerow(header)
        list_of_all_used_uniprot_ids=set([])
        # print(header)
        for row in reader:
            drugbank_id = row['drugbank_id']
            uniprot_id = row['id']
            list_of_all_used_uniprot_ids.add(uniprot_id)
            name = row['name']
            synonyms = row['synonyms'].split('|') if row['synonyms'] != '' else []
            gene_sequence_list = []

            if uniprot_id in dict_targets_info_external:
                if name != dict_targets_info_external[uniprot_id] and dict_targets_info_external[uniprot_id] not in synonyms:
                    print(row)
                    print(name)
                    print(dict_targets_info_external[uniprot_id])
                    print('###############################################################################################################################')
                    # sys.exit('uniprot name not the same ' + uniprot_id)


            if uniprot_id in dict_targets_info_sequence:
                # print(row)
                # print(uniprot_id)
                gene_sequence = row['gene-sequence'].split(' ')[1] if row['gene-sequence']!='' else ''
                amino_acid_sequence = row['amino-acid-sequence'].split(' ')[1] if row['amino-acid-sequence']!='' else ''
                dict_targets_info_sequence[uniprot_id]['gene-sequence']= dict_targets_info_sequence[uniprot_id]['gene-sequence'] if 'gene-sequence' in dict_targets_info_sequence[uniprot_id] else ''
                if dict_targets_info_sequence[uniprot_id]['gene-sequence']!='' and gene_sequence != dict_targets_info_sequence[uniprot_id]['gene-sequence']:
                    # take for the sequences both, because they are different variants of the same protein
                    # only Q05513 there is one sequence part of the other and the logger version is taken
                    if not uniprot_id in ['Q05513','P31641','Q15878']:
                        gene_sequence_list.append(gene_sequence)
                        gene_sequence_list.append(dict_targets_info_sequence[uniprot_id]['gene-sequence'])
                    # by Q15878 the other sequence is not mapping correctly in ncbi
                    elif uniprot_id in ['Q05513','Q15878']:
                        gene_sequence_list.append(gene_sequence)
                    # by P31641 the sequence from the sequence file is longer
                    else:
                        gene_sequence_list.append(dict_targets_info_sequence[uniprot_id]['gene-sequence'])
                    # print(uniprot_id)
                    # print('gene seq')
                    # print(name)
                    # print(dict_targets_info_sequence[uniprot_id]['gene-sequence'])
                    # print(gene_sequence)
                    # i=0
                    # for letter in dict_targets_info_sequence[uniprot_id]['gene-sequence']:
                    #     if letter != gene_sequence[i]:
                    #         print(i+1)
                    #         print(letter)
                    #         print(gene_sequence[i])
                    #     i+=1
                    # sys.exit('gene sequence is not the same:' + uniprot_id)
                if amino_acid_sequence != dict_targets_info_sequence[uniprot_id]['amino-acid-sequence']:
                    print(uniprot_id)
                    print('protein seq')
                    print(dict_targets_info_sequence[uniprot_id]['amino-acid-sequence'])
                    print(amino_acid_sequence)
                    i = 0
                    # for letter in dict_targets_info_sequence[uniprot_id]['amino-acid-sequence']:
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
                    for xref_source_value in row['xrefs'].split('|'):
                        # print(xref_source_value)
                        source = xref_source_value.split('::')[0]
                        value = xref_source_value.split('::')[1]
                        if source in xrefs:
                            xrefs[source].append(value)
                        else:
                            xrefs[source] = [value]



                for property, values in dict_targets_info_identifier[uniprot_id].items():
                    if property in dict_target_change_xrefs_name:
                        property=dict_target_change_xrefs_name[property]
                    if property in ['Gene Name', 'Uniprot Title']:
                        for value in values:
                            if value not in synonyms or value==name:
                                synonyms.append((value))
                                # print(uniprot_id)
                                # print(value)
                                # sys.exit('not in synonyms:' + property + ' ' + ';'.join(value) + '(' + uniprot_id)
                    elif property not in ['ID', 'Name','Species']:
                        if property in xrefs:
                            for value in values:
                                if value not in  xrefs[property]:
                                    print(dict_targets_info_identifier[uniprot_id])
                                    print(property)
                                    print(value)
                                    sys.exit('value are not the same:' + uniprot_id)
                        elif values == [] or property=='UniProtKB':
                            continue
                        elif property=='PDB ID':
                            xrefs[property]=values
                            # print(uniprot_id)
                            # print(values)
                            # print('PDB ID to xref')
                        else:
                            print(dict_targets_info_identifier[uniprot_id])
                            print(property)
                            print(values)
                            sys.exit('xref property is not there:' + uniprot_id)

            list_properties=[]
            for head in header:
                if head not in ['synonyms','xrefs','gene-sequence']:
                    list_properties.append(row[head])
                elif head=='synonyms':
                    string_synonyms='|'.join(synonyms)
                    list_properties.append(string_synonyms)
                elif head=='gene-sequence':
                    if len(gene_sequence_list)>1:
                        combined_sequences='|'.join(gene_sequence_list)
                        list_properties.append(combined_sequences)
                    else:
                        list_properties.append(row[head])
                else:
                    string_xref='|'.join([xref+'::'+';'.join(values) for xref,values in xrefs.items()])
                    list_properties.append(string_xref)


            writer_output.writerow(list_properties)

        not_in_xml=set([])
        for uniprot_id in dict_targets_info_external.keys():
            if not uniprot_id in list_of_all_used_uniprot_ids:
                print(dict_targets_info_external[uniprot_id])
                print(uniprot_id+' is not included in xml')
                not_in_xml.add(uniprot_id)
                # sys.exit(uniprot_id+' is not included in xml')
        print(len(not_in_xml))
        counter=0
        for uniprot_id in dict_targets_info_identifier.keys():
            if not uniprot_id in list_of_all_used_uniprot_ids:# and not uniprot_id in not_in_xml:
                print(dict_targets_info_external[uniprot_id])
                print(uniprot_id + ' is not included in xml')
                counter+=1
        print(counter)
        for uniprot_id in dict_targets_info_sequence.keys():
            if not uniprot_id in list_of_all_used_uniprot_ids:# and not uniprot_id in not_in_xml:
                print(dict_targets_info_external[uniprot_id])
                print(uniprot_id + ' is not included in xml')
                counter+=1
        print(counter)



'''
check the information from the different csv for the target-drug pairs files with the from the xml
the parmacologically active id known-action in xml ('yes') 
'''


def check_and_maybe_generate_a_new_drug_target_file(file, dict_drug_targets_external, dict_drug_targets_sequence,
                                                    dict_drug_targets_identifier,
                                                    dict_drug_targets_pharmacologically_active_identifier):
    dict_drug_targe_pairs_xml={}
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        header = reader.fieldnames
        for row in reader:
            drugbank_id = row['drugbank_id']
            uniprot_id= row['targets_id']
            known_action= row['known-action']
            organism=row['organism']
            if not (drugbank_id,uniprot_id) in dict_drug_targe_pairs_xml:
                dict_drug_targe_pairs_xml[(drugbank_id,uniprot_id)]={'known-action':known_action,'organism':organism}

    counter_not=0
    for (drug,uniprot_id) in dict_drug_targets_sequence.keys():
        if not (drug,uniprot_id) in dict_drug_targe_pairs_xml:
            print('sequence pair not in xml:'+drug+' '+uniprot_id)
            counter_not+=1
            # sys.exit('sequence pair not in xml:'+drug+' '+uniprot_id)
    print(counter_not)
    counter_not = 0
    for (drug, uniprot_id) in dict_drug_targets_pharmacologically_active_identifier.keys():
        if not (drug, uniprot_id) in dict_drug_targe_pairs_xml:
            print('pharmacologically pair not in xml:' + drug + ' ' + uniprot_id)
            counter_not += 1
        else:
            if dict_drug_targe_pairs_xml[(drug,uniprot_id)]['known-action']!='yes' and dict_drug_targets_pharmacologically_active_identifier[(drug,uniprot_id)]!=dict_drug_targe_pairs_xml[(drug,uniprot_id)]['organism']:
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


def gather_and_combine_carrier_information(uniprot_links,drugbank_all_polypeptide_sequences_fasta,drugbank_all_polypeptide_ids_csv,drugbank_target_tsv,drugbank_target_output_tsv,drugbank_drug_target_tsv):
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
    check_and_maybe_generate_a_new_target_file('drugbank/'+drugbank_target_tsv, dict_target_info_external,
                                               dict_target_info_sequence, dict_target_info_identifier,'output/'+drugbank_target_output_tsv)

    print (datetime.datetime.utcnow())
    print('compare and generate new drug-target file')

    #check and if nessecarry generate combined file for rela drug-target
    check_and_maybe_generate_a_new_drug_target_file('drugbank/'+drugbank_drug_target_tsv,dict_drug_target_external, dict_drug_target_sequence, dict_drug_target_identifier,dict_drug_target_pharmacologically_active_identifier)




def main():
    print (datetime.datetime.utcnow())
    print('drug')

    drugs_combination_and_check()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('carrier')

    gather_and_combine_carrier_information('uniprot_links_carrier.csv','drugbank_all_carrier_polypeptide_sequences.fasta/','drugbank_all_carrier_polypeptide_ids.csv/','drugbank_carrier.tsv','drugbank_carrier.tsv','drugbank_drug_carrier.tsv')

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('enzymes')

    gather_and_combine_carrier_information('uniprot_links_enzyme.csv','drugbank_all_enzyme_polypeptide_sequences.fasta/','drugbank_all_enzyme_polypeptide_ids.csv/','drugbank_enzymes.tsv','drugbank_enzymes.tsv','drugbank_drug_enzyme.tsv')

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('target')

    gather_and_combine_carrier_information('uniprot_links_target.csv','drugbank_all_target_polypeptide_sequences.fasta/','drugbank_all_target_polypeptide_ids.csv/','drugbank_targets.tsv','drugbank_targets.tsv','drugbank_drug_target.tsv')

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('transporter')

    gather_and_combine_carrier_information('uniprot_links_transporter.csv','drugbank_all_transporter_polypeptide_sequences.fasta/','drugbank_all_transporter_polypeptide_ids.csv/','drugbank_transporter.tsv','drugbank_transporter.tsv','drugbank_drug_transporter.tsv')


    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
