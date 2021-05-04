import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create connection to neo4j
'''


def create_connection_with_neo4j():
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# set of chemical side effect pairs
set_chemical_side_effect_pair = set()

'''
load all existing chemical-side effect relas in set
'''


def get_all_chemical_side_effect_pairs():
    query = '''Match (a:Chemical)-[r]-(b:SideEffect) Return Distinct a.identifier, b.identifier'''
    results = g.run(query)
    for chemical_id, side_effect_id, in results:
        set_chemical_side_effect_pair.add((chemical_id, side_effect_id))


'''
dictionary with compound-Se as key and value is a list of all different information
information :
    0:lowerFreq
    1:freq
    2:placebo
    3:upperfreq
    4:placebolowerfreq
    5:placebofreq
    6:placeboupperfreq
'''
dict_compound_SE_connection_informations = {}

'''
find all connection drug-se from sider for every compound-Se in hetionet and save all the information in a dictionary
'''


def find_all_compound_SE_pairs_of_sider():
    query = '''Match (a:Chemical)--(:drug_Sider)-[l:Causes]->(:se_Sider)--(b:SideEffect) Return a.identifier, l, b.identifier'''
    results = g.run(query)
    for chemical_id, connection, umlsId, in results:
        lowerFreq = connection['lowerFreq'] if not connection['lowerFreq'] is None else ''
        freq = connection['freq'] if not connection['freq'] is None else ''
        placebo = connection['placebo'] if not connection['placebo'] is None else ''
        upperFreq = connection['upperFreq'] if not connection['upperFreq'] is None else ''

        placeboLowerFreq = connection['placeboLowerFreq'] if not connection[
                                                                     'placeboLowerFreq'] is None else ''
        placeboFreq = connection['placeboFreq'] if not connection['placeboFreq'] is None else ''
        placeboUpperFreq = connection['placeboUpperFreq'] if not connection[
                                                                     'placeboUpperFreq'] is None else ''

        if not (chemical_id, umlsId) in dict_compound_SE_connection_informations:
            dict_compound_SE_connection_informations[(chemical_id, umlsId)] = [[lowerFreq], [freq],
                                                                               [placebo], [upperFreq],
                                                                               [placeboLowerFreq],
                                                                               [placeboFreq],
                                                                               [placeboUpperFreq]]
        else:
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][0].append(lowerFreq)
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][1].append(freq)
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][2].append(placebo)
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][3].append(upperFreq)
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][4].append(placeboLowerFreq)
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][5].append(placeboFreq)
            dict_compound_SE_connection_informations[(chemical_id, umlsId)][6].append(placeboUpperFreq)


# list of compound side effect tuple which create a new connection
list_tuple_compound_SE = []

'''
integration of relationship from sider into hetionet for the sider drugs which are mapped to drugbank id
'''


def integrate_relationship_from_sider_into_hetionet():
    # counter of the new compound-se connection
    number_of_new_connection = 0
    # counter of updated connection
    number_of_update_connection = 0
    # number of possible new connection
    number_of_in_new_connection = 0

    # cypher file
    cypher_file = open('output/cypher_rela.cypher', 'w', encoding='utf-8')
    query_start = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_directory + '''master_database_change/mapping_and_merging_into_hetionet/sider/output/%s.tsv" As line FIELDTERMINATOR '\t' Match (a:Chemical{identifier:line.chemical_id})'''
    query = query_start + '''-[r:CAUSES_CcSE]->(b:SideEffect{identifier:line.se_id}) Set r.upperFrequency=line.upperFrequency, r.placebo=line.placebo, r.avg_frequency=line.avg_frequency, r.lowerFrequency=line.lowerFrequency, r.placeboAvgFrequency= line.placeboAvgFrequency, r.resource=r.resource+"SIDER" , r.placeboLowerFrequency= line.placeboLowerFrequency, r.placeboUpperFrequency= line.placeboUpperFrequency,  r.sider="yes"; \n'''
    query = query % 'mapped_rela_se'
    cypher_file.write(query)

    query = query_start + ''', (b:SideEffect{identifier:line.se_id}) Create (a)-[r:CAUSES_CcSE{upperFrequency:line.upperFrequency, placebo:line.placebo, avg_frequency:line.avg_frequency, lowerFrequency:line.lowerFrequency, placeboAvgFrequency: line.placeboAvgFrequency, resource:["SIDER"] , placeboLowerFrequency: line.placeboLowerFrequency, placeboUpperFrequency: line.placeboUpperFrequency, url:"http://sideeffects.embl.de/se/"+ line.se_id ,  sider:"yes", license:"CC BY-NC-SA 4.0"}]->(b) ; \n'''
    query = query % 'new_rela_se'
    cypher_file.write(query)
    cypher_file.close()

    header = ['chemical_id', 'se_id', 'upperFrequency', 'placebo', 'avg_frequency', 'lowerFrequency',
              'placeboAvgFrequency', 'placeboLowerFrequency', 'placeboUpperFrequency']
    file = open('output/mapped_rela_se.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(header)

    file_new = open('output/new_rela_se.tsv', 'w', encoding='utf-8')
    csv_writer_new = csv.writer(file_new, delimiter='\t')
    csv_writer_new.writerow(header)
    counter = 0
    for (chemical_id, umlsId), list_of_information in dict_compound_SE_connection_informations.items():
        counter += 1
        # lowest frequency
        lowerFreq = str(min(list_of_information[0]))
        # all frequencies
        freqs = list_of_information[1]
        freqs_word = ''
        freqs_value = 0
        # count the number of frequencies with floats
        counter_values = 0
        for freq in freqs:
            # it is a word
            if '<' in freq:
                freqs_word = freq
            # is a float
            elif '%' in freq:
                counter_values += 1
                freq = freq.replace('%', '')
                # is a form .. to .. and take the average
                if '-' in freq:
                    freq = freq.split('-')
                    freq = (float(freq[0]) + float(freq[1])) / 2
                elif 'to' in freq:
                    freq = freq.split('to')
                    freq = (float(freq[0]) + float(freq[1])) / 2
                # only a number
                else:
                    freq = float(freq)
                freqs_value += freq
            else:
                freqs_word = freq
        # if at least on is a float take the average of all float frequencies
        if counter_values > 0:
            freq = str(freqs_value / counter_values) + '%'
        # take the word
        else:
            freq = freqs_word

        # maximal frequency
        upperFreq = str(max(list_of_information[3]))

        # placebo

        placebo = 'placebo' if 'placebo' in list_of_information[2] else ''

        # same as see above
        placeboFreqs = list_of_information[5]
        placeboFreqs_word = ''
        placeboFreqs_value = 0
        counter_values = 0
        for pfreq in placeboFreqs:
            if '<' in pfreq:
                placeboFreqs_word = pfreq
            elif '%' in pfreq:
                counter_values += 1
                pfreq = pfreq.replace('%', '')
                #                print(freq)
                if '-' in pfreq:
                    pfreq = pfreq.split('-')
                    pfreq = (float(pfreq[0]) + float(pfreq[1])) / 2
                elif 'to' in pfreq:
                    pfreq = pfreq.split('to')
                    pfreq = (float(pfreq[0]) + float(pfreq[1])) / 2
                else:
                    pfreq = float(pfreq)
                placeboFreqs_value += pfreq
            else:
                placeboFreqs_word = pfreq
        if counter_values > 0:
            placeboFreq = str(placeboFreqs_value / counter_values) + '%'
        else:
            placeboFreq = placeboFreqs_word

        placeboLowerFreq = str(min(list_of_information[4]))
        placeboUpperFreq = str(max(list_of_information[6]))

        if (chemical_id, umlsId) in set_chemical_side_effect_pair:
            number_of_update_connection += 1
            csv_writer.writerow([chemical_id, umlsId, upperFreq, placebo, freq, lowerFreq,
                                 placeboFreq,
                                 placeboLowerFreq, placeboUpperFreq])
        else:
            number_of_new_connection += 1
            csv_writer_new.writerow([chemical_id, umlsId, upperFreq, placebo, freq, lowerFreq,
                                     placeboFreq,
                                     placeboLowerFreq, placeboUpperFreq])

    print('Number of possible new connection:' + str(number_of_in_new_connection))
    print('Number of new connection:' + str(number_of_new_connection))
    print('Number of update connection:' + str(number_of_update_connection))
    print(('number of connections', counter))


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')

    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Load all pairs in a set')

    get_all_chemical_side_effect_pairs()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Merge the edge information')

    find_all_compound_SE_pairs_of_sider()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.utcnow())
    print('Integrate sider connection into hetionet')

    integrate_relationship_from_sider_into_hetionet()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
