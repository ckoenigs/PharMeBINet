# load in drugbank and make a new file with all drugbank entries which has at least a chemical fromular or a sequence
drugbank_file = open('data/drugbank_with_synonyms_uniis_extern_ids_molecular_seq_formular.tsv', 'r')
drugbank_file_new = open('data/durgbank_without_entries_which has_no_chemical_formular_or_sequence.tsv', 'w')
head = next(drugbank_file)
drugbank_file_new.write(head)
# write also a file with the drugbank ids which have no chemical information
drug_without_this = open('data/drugbank_without_this_information.tsv', 'w')
drug_without_this.write(head)

'''
properties:
    0:drugbank_id	
    1:name	
    2:type	
    3:groups	
    4:atc_codes	
    5:categories	
    6:inchikey	
    7:inchi	
    8:inchikeys	
    9:synonyms
    10:unii	
    11:uniis	
    12:external_identifiers	
    13:extra_names	
    14:brands	
    15:molecular_forula	
    16:molecular_formular_experimental	
    17:gene_sequence	
    18:amino_acid_sequence	
    19:sequence	
    20:description	
'''
counter_no_extra_information = 0
all_entries = 0
for line in drugbank_file:
    all_entries += 1
    splitted = line.split('\t')
    molecular_forula = splitted[15]
    molecular_formular_experimental = splitted[16]
    gene_sequence = splitted[17]
    amino_acid_sequence = splitted[18]
    sequence = splitted[19]
    # depending on the chemical information the line is written in on of the two files
    if molecular_formular_experimental != '' or molecular_forula != '' or gene_sequence != '' or amino_acid_sequence != '' or sequence != '':
        drugbank_file_new.write(line)
    else:
        counter_no_extra_information += 1
        drug_without_this.write(line)

print('all existining entries in drugbank:' + str(all_entries))
print('number of excluded drugbank ids:' + str(counter_no_extra_information))
drugbank_file.close()
drugbank_file_new.close()
