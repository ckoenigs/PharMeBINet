import csv
import datetime
import sys
import glob
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create connection to neo4j 
'''


def create_connection_with_neo4j():
    # create connection with neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


# generate cypher file
cypherfile = open('output/cypher_edge.cypher', 'a', encoding='utf-8')

# the name of the entities in the rela and dictionary
chemical = 'chemical'
gene = 'gene'
protein = 'protein'

# dictionary from interaction type and value to rela name
dict_interaction_type_and_value_to_rela_name = {
    ('activity', 'increases'): 'upregulated',
    ('expression', 'increases'): 'upregulated',
    # ('degradation', 'decreases'): 'upregulated',
    ('activity', 'decreases'): 'downregulated',
    ('expression', 'decreases'): 'downregulated',
    # ('degradation', 'increases'): 'downregulated',
}

# dictionary specific action cases get addional label for the group
dict_specific_cases = {}

# specific considered actions
list_of_specific_action = ['activity', 'expression']

# dictionary from activity name to interaction text name
dict_activate_name_text_action_name = {
    'metabolic processing': 'metabolism',
    'cotreatment': 'co-treated',
    'ethylation': ['methylation', 'ethylation'],
    'response to substance': 'susceptibility',
    'binding': 'binds'

}

# grouped actions to rela name
dict_file_action_group_to_edge_name = {
    'chemical_gene/action_to_rela/metabolic_processing_action.tsv': 'metabolic_processing',
    'chemical_gene/action_to_rela/degradation.tsv': 'degeneration',
    'chemical_gene/action_to_rela/general.tsv': 'association',
    'chemical_gene/action_to_rela/cellular_level.tsv': 'cellular_actions',
    'chemical_gene/action_to_rela/binding.tsv': 'binding',
    'chemical_gene/action_to_rela/protein_level.tsv': 'protein_actions',
    'chemical_gene/action_to_rela/DNA_level.tsv': 'actions_on_DNA'
}

# rela TSV header
columns = ['ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMed_ids', 'interactions_actions', 'unbiased']

# list of rela names
set_of_rela_names = set(['upregulated', 'downregulated'])

# list_of_actions
list_of_actions = ['decreases', 'increases', 'affects']

# rela from ctd to rela in database
dict_xtd_rela_to_database_rela_name = {
    'upregulated': 'UPREGULATES',
    'downregulated': 'DOWNREGULATES',
    'association': 'ASSOCIATES',
    'binding': 'BINDS',
    'metabolic_processing': 'IS_ACTIVE_IN_METABOLISM',
    'cellular_actions': 'IS_ACTIVE_ON_CELLULAR_LEVEL',
    'protein_actions': 'IS_ACTIVE_ON_POLYPEPTIDE_LEVEL',
    'actions_on_DNA': 'IS_ACTIVE_ON_DNA_OR_RNA_LEVEL'
}

# prepare the action type to rela name
files = glob.glob("chemical_gene/action_to_rela/*.tsv")
for file in files:
    if file in dict_file_action_group_to_edge_name:
        rela_name = dict_file_action_group_to_edge_name[file]
        open_file = open(file, 'r')
        csv_reader = csv.reader(open_file, delimiter='\t')
        for line in csv_reader:
            action_type = line[0]
            if 'degeneration' == rela_name:
                list_of_specific_action.append(action_type)
                for verb_action in list_of_actions:
                    set_of_rela_names.add(verb_action + '_' + rela_name)
                    dict_interaction_type_and_value_to_rela_name[
                        (action_type, verb_action)] = verb_action + '_' + rela_name
                    dict_xtd_rela_to_database_rela_name[
                        verb_action + '_' + rela_name] = verb_action.upper() + '_' + rela_name.upper()
            else:
                if action_type not in list_of_specific_action:
                    if action_type in dict_activate_name_text_action_name:
                        action_type = dict_activate_name_text_action_name[action_type]
                    if type(action_type) == str:
                        dict_interaction_type_and_value_to_rela_name[(action_type, '')] = rela_name
                        set_of_rela_names.add(rela_name)
                    else:
                        for action in action_type:
                            dict_interaction_type_and_value_to_rela_name[(action, '')] = rela_name
                            set_of_rela_names.add(rela_name)
                else:
                    dict_specific_cases[action_type] = rela_name
                    for verb_action in list_of_actions:
                        if not (action_type, verb_action) in dict_interaction_type_and_value_to_rela_name:
                            dict_interaction_type_and_value_to_rela_name[(action_type, verb_action)] = rela_name
                            set_of_rela_names.add(rela_name)
    else:
        sys.exit('file ' + file + ' has no rela!')

# dictionary with rela name to drug-gene/protein pair
dict_rela_to_drug_gene_protein_pair = {}

# dictionary from file name to rela name in neo4j
dict_file_name_to_rela_name = {}


def prepare_rela_small(rela, label1, label2):
    return rela + '_' + label1 + '_' + label2


def prepare_rela_great(rela, label1, label2):
    if label1 == 'chemical':
        letter_1 = 'CH'
        letter_2 = label2.upper()[0]
    else:
        letter_1 = label1.upper()[0]
        letter_2 = 'CH'
    return rela + '_' + letter_1 + ''.join([x.lower()[0] for x in rela.split('_')]) + letter_2


for label_gene_or_protein in [gene, protein]:
    for small_rela, greate_rela in dict_xtd_rela_to_database_rela_name.items():
        dict_file_name_to_rela_name[
            prepare_rela_small(small_rela, chemical, label_gene_or_protein)] = prepare_rela_great(greate_rela,
                                                                                                  chemical,
                                                                                                  label_gene_or_protein)
        dict_file_name_to_rela_name[
            prepare_rela_small(small_rela, label_gene_or_protein, chemical)] = prepare_rela_great(greate_rela,
                                                                                                  label_gene_or_protein,
                                                                                                  chemical)

dict_rela_to_file = {}

'''
generate tsv file with the columns fo a path
'''


def generate_csv(path):
    csvfile = open(path, 'w', encoding='utf-8')
    writer = csv.writer(csvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns)
    return writer


# dictionary from rela name to tuples to pubmeds
dict_rela_name_to_tuples_to_pubmeds = defaultdict(dict)

'''
generate the path to tsv and generate the tsv, add tsv to dictionary
also generate cypher query
'''


def path_to_rela_and_add_to_dict(rela, first, second):
    rela_full = rela + '_' + first + '_' + second
    path = 'chemical_gene/relationships_' + rela_full + '.tsv'
    writer = generate_csv(path)
    dict_rela_to_file[rela_full] = writer

    query_to_check_if_this_rela_exist_in_pharmebinet = '''Match p=(b:Chemical)'''

    query_first_part = ''' Match (b:Chemical{identifier:line.ChemicalID}), '''
    if first == 'gene' or second == 'gene':
        query_middle_1 = ''' (n:Gene{identifier:line.GeneID})'''
        part = '''(n:Gene)'''
    else:
        query_middle_1 = ''' (g:Gene{identifier:line.GeneID})-[:PRODUCES_GpP]->(n:Protein)'''
        part = '''(n:Protein)'''

    if first == 'chemical':
        query_middle_2 = ''' Merge (b)-[r:%s]->(n)'''
        query_to_check_if_this_rela_exist_in_pharmebinet += '-[r:%s]->' + part + ' Return b.identifier, n.identifier, r.pubMed_ids'
    else:
        query_middle_2 = ''' Merge (b)<-[r:%s]-(n)'''
        query_to_check_if_this_rela_exist_in_pharmebinet += '<-[r:%s]-' + part + ' Return p Limit 1'

    query_to_check_if_this_rela_exist_in_pharmebinet = query_to_check_if_this_rela_exist_in_pharmebinet % (
        dict_file_name_to_rela_name[rela_full])
    results = g.run(query_to_check_if_this_rela_exist_in_pharmebinet)
    result = results.single()
    # if this relationship exists currently only merge is used maybe I will change this to match and create
    # however, for the relationships which already exists in the general file new queries are added to say which are not in ctd
    if result:

        query_last_part = ''' On Create Set  r.ctd='yes', r.source="CTD", r.url="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , r.resource=["CTD"], r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2021 NC State University. All rights reserved.", r.unbiased=toBoolean(line.unbiased), r.interaction_texts=split(line.interaction_text,'|'), r.gene_forms=split(line.gene_forms,'|'), r.pubMed_ids=split(line.pubMed_ids,'|'), r.interactions_actions=split(line.interactions_actions,'|') On Match SET r.ctd='yes', r.url_ctd="http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID, r.resource=["CTD","Hetionet"], r.license="© 2002–2012 MDI Biological Laboratory. © 2012–2021 NC State University. All rights reserved.", r.unbiased=toBoolean(line.unbiased), r.interaction_texts=split(line.interaction_text,'|'), r.gene_forms=split(line.gene_forms,'|'), r.pubMed_ids=split(line.pubMed_ids,'|'), r.interactions_actions=split(line.interactions_actions,'|') '''
        query = query_first_part + query_middle_1 + query_middle_2 + query_last_part

        dict_tuples_to_pubmeds = dict_rela_name_to_tuples_to_pubmeds[rela_full]
        for chemical_id, node_id, pubMed_ids, in results:
            # if pubMed_ids is None:
            #     print('huhuh')
            dict_tuples_to_pubmeds[(chemical_id, node_id)] = pubMed_ids if pubMed_ids is not None else []


    else:

        query_middle_2_parts = query_middle_2.split(']')

        query_last_part = '''{ ctd:'yes', url:"http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , url_ctd:"http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID ,source:"CTD", resource:["CTD"], license:"© 2002–2012 MDI Biological Laboratory. © 2012–2021 NC State University. All rights reserved.", unbiased:toBoolean(line.unbiased), interaction_texts:split(line.interaction_text,'|'), gene_forms:split(line.gene_forms,'|'), pubMed_ids:split(line.pubMed_ids,'|'), interactions_actions:split(line.interactions_actions,'|')}]'''
        query = query_first_part + query_middle_1 + query_middle_2_parts[0].replace('Merge',
                                                                                    'Create') + query_last_part + \
                query_middle_2_parts[1] + ''

    query = query % (dict_file_name_to_rela_name[rela_full])
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ctd/{path}',
                                              query)
    cypherfile.write(query)


'''
generate dictionary for every possible rela combination
'''


def generate_tsv_file_for_different_rela_types():
    for rela in set_of_rela_names:
        path_to_rela_and_add_to_dict(rela, chemical, gene)
        path_to_rela_and_add_to_dict(rela, gene, chemical)
        path_to_rela_and_add_to_dict(rela, chemical, protein)
        path_to_rela_and_add_to_dict(rela, protein, chemical)


'''
search for chemical
'''


def search_for_chemical(chemical_name, chemical_synonyms, interaction_text):
    found_chemical = False
    found_chemical_synonym = ''
    # check also the  name
    if not chemical_name is None and chemical_name != '':
        chemical_synonyms.insert(0, chemical_name)

    # find the used name of the chemical
    for chemical_synonym in chemical_synonyms:
        found_chemical, found_chemical_synonym = search_for_name_in_string(interaction_text, chemical_synonym)
        if found_chemical:
            break
    if not found_chemical:
        print('chemical name not found')
        print(chemical_name)
    found_chemical_synonym = found_chemical_synonym if found_chemical else chemical_name
    return found_chemical_synonym


'''
search for a name in a string and gib back if found and the value
'''


def search_for_name_in_string(interaction_text, name):
    found_name_value = ''
    found_name = False
    interaction_text = interaction_text.lower()
    name = name.lower()
    possible_position = interaction_text.find(name)
    if possible_position != -1:
        found_name_value = name
        found_name = True
    return found_name, found_name_value


'''
find used name for gene for text mining
'''


def find_text_name_for_gene(gene_name, gene_symbol, interaction_text, gene_id):
    found_gene = False

    found_gene_synonym = ''

    found_gene, found_gene_synonym = search_for_name_in_string(interaction_text, gene_symbol)
    if not found_gene:
        print(gene_id)
        print(gene_name)
        print(gene_symbol)
        print(interaction_text)
        print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')

        query = '''Match (s:Gene{identifier:%s}) Return s.synonyms''' % (gene_id)
        results = g.run(query)
        for record in results:
            [synonyms] = record.values()
            for synonym in synonyms:
                found_gene, found_gene_synonym = search_for_name_in_string(interaction_text, synonym)
                if found_gene:
                    break
    if not found_gene:
        print(gene_id)
        print(gene_name)
        print(gene_symbol)
        print(interaction_text)
        print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
    found_gene_synonym = found_gene_synonym if found_gene else gene_name

    return found_gene_synonym


# dictionary of chemical id to chemical name used in the interaction text
dict_chemical_id_to_used_name = {}

# dictionary of gene id to gene name used in the interaction text
dict_gene_id_to_used_name = {}

# dictionary from interaction typ value to interaction text value
dict_interaction_type_value_to_interaction_text_value = {
    'increases': 'increased',
    'decreases': 'decreased'
}

'''
sort the information into the right dictionary and add the infomation
'''


def sort_into_dictionary_and_add(dict_action, chemical_id, gene_id, interaction_text, gene_forms, pubMedIds,
                                 interactions_actions):
    if (chemical_id, gene_id) in dict_action:
        dict_action[(chemical_id, gene_id)][0].append(interaction_text)
        dict_action[(chemical_id, gene_id)][1].append(gene_forms)
        dict_action[(chemical_id, gene_id)][2].extend(pubMedIds)
        dict_action[(chemical_id, gene_id)][2] = list(
            set(dict_action[(chemical_id, gene_id)][2]))
        dict_action[(chemical_id, gene_id)][3].append(interactions_actions)
    else:
        dict_action[(chemical_id, gene_id)] = [[interaction_text], [gene_forms], pubMedIds,
                                               [interactions_actions]]


'''
get the right rela name
'''


def get_right_rela_name(position_chemical, position_gene, contains_protein, word, action_value):
    if not (word, action_value) in dict_interaction_type_and_value_to_rela_name:
        return ''
    # ge the full name of the rela
    if position_chemical < position_gene and contains_protein:
        rela_full = dict_interaction_type_and_value_to_rela_name[(word, action_value)] + '_' + chemical + '_' + protein
    elif position_chemical < position_gene:
        rela_full = dict_interaction_type_and_value_to_rela_name[(
            word, action_value)] + '_' + chemical + '_' + gene
    elif contains_protein:
        rela_full = dict_interaction_type_and_value_to_rela_name[(
            word, action_value)] + '_' + protein + '_' + chemical
    else:
        rela_full = dict_interaction_type_and_value_to_rela_name[(
            word, action_value)] + '_' + gene + '_' + chemical
    return rela_full


'''
generate for new rela  a dictionary entry with a dictionary for all chemical-gene pairs
all information of the pair are add into the dictionary
'''


def add_pair_to_dict(chemical_id, drugbank_ids, gene_id, interaction_text, interactions_actions, gene_forms, pubMedIds,
                     rela_full):
    # generate for every rela a dictionary with their own drug-gene pair
    if not rela_full in dict_rela_to_drug_gene_protein_pair:
        dict_rela_to_drug_gene_protein_pair[rela_full] = defaultdict(dict)

    # add all chemical-gene pair into the right dictionary
    if drugbank_ids:
        for drugbank_id in drugbank_ids:
            sort_into_dictionary_and_add(dict_rela_to_drug_gene_protein_pair[rela_full],
                                         drugbank_id, gene_id, interaction_text, gene_forms,
                                         pubMedIds, interactions_actions)
    else:
        sort_into_dictionary_and_add(dict_rela_to_drug_gene_protein_pair[rela_full],
                                     chemical_id, gene_id, interaction_text, gene_forms,
                                     pubMedIds, interactions_actions)


'''
get all relationships between gene and chemical, take the pharmebinet identifier an save all important information in a tsv
also generate a cypher file to integrate this information 
'''


def take_all_relationships_of_gene_chemical():
    counter_all_rela = 0

    # {gene_id:'1'} Where chemical.chemical_id='D000117' and gene.gene_id='2219'; Where chemical.chemical_id='C057693' and gene.gene_id='4128' Where chemical.chemical_id='D001564' and gene.gene_id='9429'  Where chemical.chemical_id='D004976' and gene.gene_id='2950' Where chemical.chemical_id='D015741' and gene.gene_id='367'
    query = '''MATCH (chemical:CTD_chemical)-[r:associates_CG{organism_id:'9606'}]->(gene:CTD_gene) Where (gene)-[:equal_to_CTD_gene]-(:Gene) and r.pubMed_ids is not NULL RETURN gene.gene_id, gene.name, gene.geneSymbol, r, chemical.chemical_id, chemical.name, chemical.synonyms, chemical.drugBankIDs'''
    results = g.run(query)

    for record in results:
        [gene_id, gene_name, gene_symbol, rela, chemical_id, chemical_name, chemical_synonyms,
         drugbank_ids] = record.values()
        counter_all_rela += 1
        interaction_text = rela['interaction_text'] if 'interaction_text' in rela else ''
        gene_forms = rela['gene_forms'] if 'gene_forms' in rela else []
        pubMedIds = rela['pubMed_ids'] if 'pubMed_ids' in rela else []
        interactions_actions = rela['interactions_actions'] if 'interactions_actions' in rela else []
        drugbank_ids = drugbank_ids if not drugbank_ids is None else []
        if len(pubMedIds) == 0:
            print(gene_id, drugbank_ids, chemical_id)
            print(pubMedIds, rela)
            sys.exit('entry without pubmed ids')

        chemical_synonyms = chemical_synonyms if not chemical_synonyms is None else []
        chemical_synonyms = list(filter(None, chemical_synonyms))

        # for searching in the interaction text if gene and chemical are in the same []
        if gene_id in dict_gene_id_to_used_name:
            found_gene_synonym = dict_gene_id_to_used_name[gene_id]
        else:
            found_gene_synonym = find_text_name_for_gene(gene_name, gene_symbol, interaction_text, gene_id)

            dict_gene_id_to_used_name[gene_id] = found_gene_synonym

        if chemical_id in dict_chemical_id_to_used_name:
            found_chemical_synonym = dict_chemical_id_to_used_name[chemical_id]
        else:
            found_chemical_synonym = search_for_chemical(chemical_name, chemical_synonyms, interaction_text)
            dict_chemical_id_to_used_name[chemical_id] = found_chemical_synonym

        # check if it is the protein form of the gene or not
        contains_protein = False
        if 'protein' in gene_forms:
            possible_position = interaction_text.lower().find(found_gene_synonym + ' protein')
            if possible_position != -1:
                contains_protein = True

        # dictionary for word which appears in the interaction text with the value like increase/decrease
        dict_interaction_word_to_value = {}

        # prepare the dictionary of action words that can appear in a interact_text part
        for interaction in interactions_actions:
            splitter = interaction.split('^')
            action_type = splitter[1]
            if action_type in list_of_specific_action:
                if action_type not in dict_interaction_word_to_value:
                    dict_interaction_word_to_value[action_type] = [splitter[0]]
                else:
                    dict_interaction_word_to_value[action_type].append(splitter[0])
                # print(interactions_actions)
            elif (action_type, '') in dict_interaction_type_and_value_to_rela_name:

                if len(action_type.split(' ')) > 1:
                    action_type = action_type.split(' ')[0]

                if action_type not in dict_interaction_word_to_value:
                    dict_interaction_word_to_value[action_type] = ['']
            elif action_type in dict_activate_name_text_action_name:
                if type(dict_activate_name_text_action_name[action_type]) == str:
                    action_type = dict_activate_name_text_action_name[action_type]
                else:
                    counter = 0
                    last = len(dict_activate_name_text_action_name[action_type]) - 1
                    for part in dict_activate_name_text_action_name[action_type]:
                        if counter == last:
                            action_type = part
                        else:
                            if (part, '') in dict_interaction_type_and_value_to_rela_name:
                                if part not in dict_interaction_word_to_value:
                                    dict_interaction_word_to_value[part] = ['']
                            else:
                                sys.exit(part + 'is not in rela')
                        counter += 1
                if (action_type, '') in dict_interaction_type_and_value_to_rela_name:
                    if action_type not in dict_interaction_word_to_value:
                        dict_interaction_word_to_value[action_type] = ['']
            else:
                sys.exit('the interaction ' + action_type + ' has no rela')

        # if no other rela type is found then the pair are add to association
        found_a_interaction_type = False

        # to find the exact words and to avoid that not a space is in front or in the end spaces are add
        interaction_text_with_spaces = ' ' + interaction_text.replace('[', '[ ') + ' '
        interaction_text_with_spaces = interaction_text_with_spaces.replace(']', ' ]')

        for part in interaction_text_with_spaces.split('['):
            for smaller_part in part.split(']'):
                # find take every time the first time when the substring appeares, so some times the chemcial appears multiple
                # time so the order for the sub action need to be new classified
                smaller_part = smaller_part.lower()
                position_chemical_new = smaller_part.find(' ' + found_chemical_synonym + ' ')
                position_gene_new = smaller_part.find(' ' + found_gene_synonym + ' ')
                if position_chemical_new != -1 and position_gene_new != -1:
                    for word in smaller_part.split(' '):
                        if word in dict_interaction_word_to_value:
                            found_a_interaction_type = True
                            if len(dict_interaction_word_to_value[word]) == 1:
                                action_value = dict_interaction_word_to_value[word][0]
                                rela_full = get_right_rela_name(position_chemical_new, position_gene_new,
                                                                contains_protein,
                                                                word, action_value)
                                if rela_full == '':
                                    found_a_interaction_type = False
                                    continue
                                add_pair_to_dict(chemical_id, drugbank_ids, gene_id, interaction_text,
                                                 interactions_actions, gene_forms, pubMedIds, rela_full)


                            elif len(dict_interaction_word_to_value[word]) > 1:
                                found_the_action_value = False
                                for action_value in dict_interaction_word_to_value[word]:
                                    if action_value in dict_interaction_type_value_to_interaction_text_value:
                                        position_action_value = smaller_part.find(
                                            dict_interaction_type_value_to_interaction_text_value[action_value])
                                        if position_action_value != -1:
                                            found_the_action_value = True
                                            rela_full = get_right_rela_name(position_chemical_new, position_gene_new,
                                                                            contains_protein, word, action_value)
                                            if rela_full == '':
                                                found_a_interaction_type = False
                                                continue
                                            add_pair_to_dict(chemical_id, drugbank_ids, gene_id, interaction_text,
                                                             interactions_actions, gene_forms, pubMedIds, rela_full)

                                if not found_the_action_value:
                                    found_a_interaction_type = False

                            else:
                                print(interaction_text)
                                print(word)
                                sys.exit('crazy')

        if not found_a_interaction_type:
            if contains_protein:
                rela_full = 'association_' + chemical + '_' + protein
            else:
                rela_full = 'association_' + chemical + '_' + gene
            add_pair_to_dict(chemical_id, drugbank_ids, gene_id, interaction_text,
                             interactions_actions, gene_forms, pubMedIds, rela_full)

    print('number of all rela in human organism:' + str(counter_all_rela))


'''
find the shortest string in a list 
'''


def find_shortest_string_and_index(list_string):
    shortest_string = min(list_string, key=len)
    index = list_string.index(shortest_string)
    return index, shortest_string


'''
find the shortest list and all list with the same length but different value
'''


def find_shortest_list_and_indeces(list_of_lists):
    shortest = min(list_of_lists, key=len)
    all_with_the_same_length = [shortest]
    shortest_length = len(shortest)
    indices = [list_of_lists.index(shortest)]
    counter = 0
    for list_of_list in list_of_lists:
        if len(list_of_list) == shortest_length:
            if not list_of_list in all_with_the_same_length:
                all_with_the_same_length.append(list_of_list)
                indices.append(counter)
        counter += 1

    return indices, all_with_the_same_length


'''
now go through all rela types and add every pair to the right tsv
but only take the shortest interaction text and the associated intereaction actions and gene forms
'ChemicalID', 'GeneID', 'interaction_text', 'gene_forms', 'pubMedIds', 'interactions_actions', 'unbiased'
'''


def fill_the_tsv_files():
    for rela_full, dict_chemical_gene_pair in dict_rela_to_drug_gene_protein_pair.items():
        for (chemical_id, gene_id), list_of_information in dict_chemical_gene_pair.items():
            pubMedIds = list_of_information[2]
            if len(pubMedIds) == 0:
                print(chemical_id, gene_id, rela_full)
                print(list_of_information)
                sys.exit('second pubmed check!')

            if rela_full in dict_rela_name_to_tuples_to_pubmeds and (chemical_id, gene_id) in \
                    dict_rela_name_to_tuples_to_pubmeds[rela_full]:
                pubMedIds = set(pubMedIds).union(dict_rela_name_to_tuples_to_pubmeds[rela_full][(chemical_id, gene_id)])
            pubMedIds = '|'.join(pubMedIds)
            interactions_actions = list_of_information[3]
            indices, shortest_interaction_actions = find_shortest_list_and_indeces(interactions_actions)
            shortest_interaction_actions = [';'.join(x) for x in shortest_interaction_actions]
            shortest_interaction_actions = '|'.join(shortest_interaction_actions)

            interaction_texts = list_of_information[0]
            shortest_interaction_text = [interaction_texts[x] for x in indices]
            gene_forms = list_of_information[1]
            shortest_gene_forms = [gene_forms[x] for x in indices]
            shortest_gene_forms = [';'.join(x) for x in shortest_gene_forms]
            shortest_gene_forms = '|'.join(set(shortest_gene_forms))

            unbiased = True if len(pubMedIds) > 0 else False
            shortest_interaction_text = '|'.join(shortest_interaction_text)
            if len(pubMedIds) == 0:
                print(chemical_id, gene_id, rela_full)
                print(list_of_information)
                sys.exit('third pubmed check!')
            if chemical_id == 'DB00313' and gene_id == '1':
                print(rela_full)
                print(pubMedIds)
                print([chemical_id, gene_id, shortest_interaction_text, shortest_gene_forms, pubMedIds,
                       shortest_interaction_actions
                          , unbiased])

            dict_rela_to_file[rela_full].writerow(
                [chemical_id, gene_id, shortest_interaction_text, shortest_gene_forms, pubMedIds,
                 shortest_interaction_actions
                    , unbiased])


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.now())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print(' generate tsv and cypher file')

    generate_tsv_file_for_different_rela_types()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Take all gene-chemical relationships and generate tsv and cypher file')

    take_all_relationships_of_gene_chemical()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('write into tsv files')

    fill_the_tsv_files()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
