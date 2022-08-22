import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary from type to dictionary with pairs to rela
dict_rela_type_to_dictionary = {}

# dictionary from real rela type to the names in drugbank
dict_real_rela_type_to_list_of_rela_types = {}

# cypher file
cypher_file = open('rela_protein/cypher.cypher', 'w', encoding='utf-8')

# dictionary first letter to rela Letter
dict_first_letter_to_rela_letter = {
    'T': 'Target',
    'C': 'Carrier',
    'CA': 'Carrier',
    'TR': 'Transport',
    'E': 'Enzyme'
}


def load_all_protein_chemical_pairs(direction, from_chemical):
    '''
    load all relationships for one direction for humans and add to dictionary
    :param direction: string
    :param from_chemical: boolean
    :return:
    '''
    query = '''Match (p)--(:Protein_DrugBank)%s(:Compound_DrugBank)--(c:Compound) Where 'Protein' in labels(p) or 'Chemical' in labels(p) and r.organism in ["Humans","Humans and other mammals"] Return labels(p), p.identifier, r, type(r), c.identifier '''
    query = query % (direction)
    results = g.run(query)

    counter = 0
    for labels, identifier1, rela, rela_type, compound_id, in results:
        counter += 1
        rela = dict(rela)
        # take only the rela which have references!
        refs = [x for x in rela.keys() if x.startswith('ref')]
        if len(refs) == 0:
            continue
        rela_type_splitted = rela_type.rsplit('_',1)

        last_part = rela_type_splitted[1]
        if len(last_part) == 3:
            letter = last_part[2]
        elif len(last_part) == 4:
            letter = last_part[2:]
        else:

            print(last_part)
            sys.exit('different length of end of rela in drugbank compound-protein')
        type_of_interaction = dict_first_letter_to_rela_letter[letter]
        rela['interaction_with_form'] = type_of_interaction

        if 'Protein' in labels:
            label = 'Protein'
            short_cut = 'P'
        else:
            label = 'Chemical'
            short_cut = 'CH'
        rela_name = rela_type_splitted[0].upper()
        abbreviaction_rela=''.join([x[0].lower() for x in rela_name.split('_')])
        if from_chemical:
            this_rela_name = rela_name + '_CH' + abbreviaction_rela + short_cut
        else:
            this_rela_name = rela_name + '_' + short_cut + abbreviaction_rela + 'CH'

        # for the connection between real name to names in drugbank
        if not this_rela_name in dict_real_rela_type_to_list_of_rela_types:
            dict_real_rela_type_to_list_of_rela_types[this_rela_name] = set()
        dict_real_rela_type_to_list_of_rela_types[this_rela_name].add(rela_type)

        # build dictionary for pairs
        if not this_rela_name in dict_rela_type_to_dictionary:
            dict_rela_type_to_dictionary[this_rela_name] = {}

        if not (label, from_chemical) in dict_rela_type_to_dictionary[this_rela_name]:
            dict_rela_type_to_dictionary[this_rela_name][(label, from_chemical)] = {}
        dict_pairs = dict_rela_type_to_dictionary[this_rela_name][(label, from_chemical)]

        if not (identifier1, compound_id) in dict_pairs:
            dict_pairs[(identifier1, compound_id)] = [dict(rela)]
        else:
            # print('ohje double pair')
            # print(identifier1)
            # print(labels)
            # print(compound_id)
            dict_pairs[(identifier1, compound_id)].append(dict(rela))
    print('number of edges:', counter)


'''
Create cypher query and the tsv file for the different relationships
'''


def create_cypher_query_and_tsv_file(rela_name, rela_direction, label_from):
    query = 'Match p=(:%s)%s(:Chemical) Return p Limit 1' % (label_from, rela_direction)
    results = g.run(query)
    result = results.evaluate()
    exists = False
    if result:
        exists = True
    # file name
    file_name = rela_name + '_Compound_' + label_from

    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''mapping_and_merging_into_hetionet/drugbank/rela_protein/%s.tsv" As line Fieldterminator '\\t' Match (a:%s{identifier:line.identifier1}),  (c:Chemical{identifier:line.identifier2}) '''
    query_start = query_start % (file_name, label_from)
    query_create = ''
    query_update = ''
    query = '''MATCH (n:Protein_DrugBank)-[p]-(:Compound_DrugBank) Where type(p) in ["%s"] WITH DISTINCT keys(p) AS keys
        UNWIND keys AS keyslisting WITH DISTINCT keyslisting AS allfields
        RETURN allfields;'''
    query = query % ('","'.join(dict_real_rela_type_to_list_of_rela_types[rela_name]),)
    results = g.run(query)
    list_of_properties = ['identifier1', 'identifier2', 'interaction_with_form']
    for property, in results:
        # this is for all similar
        if property in ['organism', 'license']:
            if label_from == 'Chemical' and property == 'organism':
                query_create += property + ':line.' + property + ', '
                query_update += 'r.' + property + '=line.' + property + ', '
                list_of_properties.append(property)
            continue
        if property.startswith('ref') or property in ['actions', 'position', 'known_action']:
            prop_first= property+'s' if property[-1]!='s' else property
            query_create += prop_first + ':split(line.' + property + ',"|"), '
            query_update += 'r.' + prop_first + '=split(line.' + property + ',"|"), '
        else:
            query_create += property + ':line.' + property + ', '
            query_update += 'r.' + property + '=line.' + property + ', '
        list_of_properties.append(property)
    list_of_properties.append('unbiased')

    # create tsv file
    file = open('rela_protein/' + file_name + '.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(list_of_properties)

    query_update += 'r.drugbank="yes", r.unbiased=toBoolean(line.unbiased), '

    if not exists:

        if rela_direction.startswith('<'):
            query_create = "<-[:" + rela_name + ' {' + query_create + ' interaction_with_form:split(line.interaction_with_form,"|"), unbiased:toBoolean(line.unbiased), source:"DrugBank", resource:["DrugBank"], url:"https://go.drugbank.com/drugs/"+line.identifier2, drugbank:"yes", license:"' + license + '"}]-'
        else:
            query_create = "-[:" + rela_name + ' {' + query_create + 'interaction_with_form:split(line.interaction_with_form,"|") , source:"DrugBank", resource:["DrugBank"], drugbank:"yes", url:"https://go.drugbank.com/drugs/"+line.identifier2, license:"' + license + '"}]->'
        query = query_start + " Create (a)" + query_create + '(c);\n'
    else:
        query = query_start + ' Merge (a)' + rela_direction + '(c) On Create Set ' + query_update + ' r.interaction_with_form=split(line.interaction_with_form,"|"), r.source="DrugBank", r.drugbank="yes", r.resource=["DrugBank"], r.url="https://go.drugbank.com/drugs/"+line.identifier2, r.license="' + license + '" On Match Set ' + query_update + ' r.drugbank="yes",  r.resource=r.resource+"DrugBank";\n'

    cypher_file.write(query)
    return csv_writer, list_of_properties


def run_through_dictionary_to_add_to_tsv_and_cypher():
    for rela_name, values in dict_rela_type_to_dictionary.items():
        for (label, from_chemical), dict_pairs in values.items():
            if from_chemical:
                rela_direction = '<-[r:%s]-'
            else:
                rela_direction = '-[r:%s]->'
            rela_direction = rela_direction % (rela_name)
            csv_writer, list_of_properties = create_cypher_query_and_tsv_file(rela_name, rela_direction, label)
            for (identifier1, compound_id), list_rela in dict_pairs.items():
                tsv_list = [identifier1, compound_id]
                if len(list_rela) == 1:
                    rela_infos = list_rela[0]
                    contain_ref = False
                    for property in list_of_properties[2:]:
                        if property in rela_infos:
                            value= rela_infos[property]
                            if property.startswith('ref'):
                                contain_ref = True
                            if type(value)==list:
                                # print(property)
                                value='|'.join(value)
                            tsv_list.append(value)
                        elif property == 'unbiased':
                            tsv_list.append('true') if contain_ref else tsv_list.append('false')
                        else:
                            tsv_list.append('')

                else:
                    contain_ref = False
                    for property in list_of_properties[2:]:
                        if property == 'unbiased':
                            tsv_list.append('true') if contain_ref else tsv_list.append('false')
                            continue
                        set_of_info_for_this_property = set()
                        for rela_infos in list_rela:
                            if property in rela_infos:
                                if property.startswith('ref'):
                                    contain_ref = True
                                if type(rela_infos[property]) == str:
                                    set_of_info_for_this_property.add(rela_infos[property])
                                else:
                                    set_of_info_for_this_property=set_of_info_for_this_property.union(rela_infos[property])
                        if len(set_of_info_for_this_property) > 1:
                            if not (property.startswith('ref') or property in ['actions', 'position', 'known_action',
                                                                               'interaction_with_form']):
                                print('ohje, something which I do not expact to be a list is a list')
                                print(property)
                                print(tsv_list)
                                print(set_of_info_for_this_property)
                            tsv_list.append("|".join(set_of_info_for_this_property))
                        elif len(set_of_info_for_this_property) == 1:
                            tsv_list.append(set_of_info_for_this_property.pop())
                        else:
                            tsv_list.append('')

                csv_writer.writerow(tsv_list)


# path to directory
path_of_directory = ''


def main():
    global path_of_directory
    if len(sys.argv) < 2:
        sys.exit('need license and path to directory')
    global license
    license = sys.argv[1]
    path_of_directory = sys.argv[2]
    print(sys.argv)
    print(path_of_directory)
    print(datetime.datetime.now())
    print('create connection with neo4j')

    create_connection_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all rela and add to dictionary')

    load_all_protein_chemical_pairs('-[r]->', False)
    load_all_protein_chemical_pairs('<-[r]-', True)

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())
    print('load all hetionet compound in dictionary')

    run_through_dictionary_to_add_to_tsv_and_cypher()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
