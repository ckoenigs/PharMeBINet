import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

def create_connection_with_neo4j():
    # create connection to neo4j
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')


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


def find_all_compound_SE_pairs_of_sider():
    # find all connection drug-se from sider for every compound-Se in pharmebinet and save all the information in a
    # dictionary
    query = '''Match (a:Chemical)--(:drug_Sider)-[l:Causes]->(:se_Sider)--(b:SideEffect) Return a.identifier, l, b.identifier'''
    results = g.run(query)
    for record in results:
        [chemical_id, connection, umlsId] = record.values()
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


def integrate_relationship_from_sider_into_pharmebinet():
    """
    integration of relationship from sider into pharmebinet for the sider drugs which are mapped to drugbank id
    :return:
    """
    # counter of the new compound-se connection
    number_of_new_connection = 0
    # counter of updated connection
    number_of_update_connection = 0
    # number of possible new connection
    number_of_in_new_connection = 0

    # cypher file
    cypher_file = open('output/cypher_rela.cypher', 'w', encoding='utf-8')
    query_start = ''' Match (a:Chemical{identifier:line.chemical_id})'''

    query = query_start + ''', (b:SideEffect{identifier:line.se_id}) Create (a)-[r:CAUSES_CHcSE{upperFrequency:line.upperFrequency, placebo:line.placebo, avg_frequency:line.avg_frequency, lowerFrequency:line.lowerFrequency, placeboAvgFrequency: line.placeboAvgFrequency, resource:["SIDER"] , placeboLowerFrequency: line.placeboLowerFrequency, placeboUpperFrequency: line.placeboUpperFrequency, url:"http://sideeffects.embl.de/se/"+ line.se_id , source:"SIDER",   sider:"yes", license:"CC BY-NC-SA 4.0"}]->(b) '''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/sider/output/new_rela_se.tsv',
                                              query)
    cypher_file.write(query)
    cypher_file.close()

    header = ['chemical_id', 'se_id', 'upperFrequency', 'placebo', 'avg_frequency', 'lowerFrequency',
              'placeboAvgFrequency', 'placeboLowerFrequency', 'placeboUpperFrequency']

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

        csv_writer_new.writerow(
            [chemical_id, umlsId, upperFreq, placebo, freq, lowerFreq, placeboFreq, placeboLowerFreq, placeboUpperFreq])

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

    print(datetime.datetime.now())
    print('Generate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Merge the edge information')

    find_all_compound_SE_pairs_of_sider()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('Integrate sider connection into database')

    integrate_relationship_from_sider_into_pharmebinet()
    driver.close()

    print(
        '###########################################################################################################################')
    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
