import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

sys.path.append("..")
from change_xref_source_name_to_a_specifice_form import go_through_xrefs_and_change_if_needed_source_name

'''
create a connection with neo4j
'''


def create_connection_to_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')
cypher_file.write('Match (n:PharmacologicClass) Detach Delete n;\n')


def write_files(path_of_directory, addition_name, label):
    """
    Prepare for each label a csv file and prepare integration query.
    :param path_of_directory:
    :param addition_name:
    :param label:
    :return:
    """
    file_name_new = 'pharmacological_class/new_' + addition_name + '.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header_new = ['med_id', 'id', 'xrefs']
    csv_new.writerow(header_new)

    query = '''Match (n:%s{id:line.med_id}) Create (v:PharmacologicClass{identifier:line.id, med_rt:'yes', xrefs:split(line.xrefs,'|'), synonyms:n.synonyms, resource:['MED-RT'], source:'MED-RT', url:'http://purl.bioontology.org/ontology/NDFRT/'+line.id, name:n.name, license:'UMLS license, available at https://uts.nlm.nih.gov/license.html', class_type:["%s"]}) Create (v)-[:equal_to_med_rt{how_mapped:'new'}]->(n)'''
    query = query % (label, addition_name.replace('_', ' ').title().replace('Of', 'of'))
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/med_rt/{file_name_new}',
                                              query)
    cypher_file.write(query)

    return csv_new


# dictionary name to id from new pc nodes
dict_name_to_new_pc_nodes = {}


def load_all_label_and_map(label, csv_new):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH (n:%s) RETURN n" % (label)
    results = g.run(query)
    set_properties=set()
    for record in results:
        node = record.data()['n']
        identifier = node['id']
        name = node['name'].lower()

        found_mapping = False
        xrefs = set()
        for property in node['properties']:
            if property.startswith('MED-RT:NUI:'):
                id_nui = property.split(':')[2]
                xrefs.add(id_nui)
            else:
                property_part=property.split(':')[0]
                if property_part not in set_properties:
                    print(property, label)
                    set_properties.add(property_part)



        # generate a dictionary of the new pc names to identifier
        if name not in dict_name_to_new_pc_nodes:
            dict_name_to_new_pc_nodes[name] = set()
        else:
            print(name, dict_name_to_new_pc_nodes[name], identifier)
            print('double name by ndf-rt pc')
        dict_name_to_new_pc_nodes[name].add(id_nui)

        csv_new.writerow([identifier, identifier,
                          '|'.join(go_through_xrefs_and_change_if_needed_source_name(xrefs, 'pharmacological class'))])


cypher_edge=open('output/cypher_edge.cypher','w', encoding='utf-8')

def write_files_edge(path_of_directory,  label1, label2):
    """
    Praper for a relationship a csv file and the fitting query is added to cypher file.
    :param path_of_directory:
    :param label1:
    :param label2:
    :return:
    """
    # file from relationship between gene and variant
    file_name_new = f'pharmacological_class/new_{label1}_{label2}.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header_new = ['id_1', 'id_2']
    csv_new.writerow(header_new)

    query = '''Match (v1:PharmacologicClass{identifier:line.id_1}), (v2:PharmacologicClass{identifier:line.id_2}) Create (v1)-[:PARENT_OF_PCpoPC{med_rt:"yes", source:"MED-RT", resource:["MED-RT"], license:"UMLS license, available at https://uts.nlm.nih.gov/license.html", url:"check"}]->(v2)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/med_rt/{file_name_new}',
                                              query)
    cypher_edge.write(query)

    return csv_new

pc_labels=['Additional_Pharmacologic_Classes_MEDRT','FDA_Established_Pharmacologic_Classes_MEDRT', 'Mechanisms_of_Action_MEDRT',
                  'Physiologic_Effects_MEDRT', 'Pharmacokinetics_MEDRT', 'Therapeutic_Categories_MEDRT']

def prepare_parent_of_files(label, index, path_of_directory):
    """
    For each label combination prepare the csv file and the cypher query.
    :param label:
    :param index:
    :param path_of_directory:
    :return:
    """
    for other_pc_label in pc_labels[index:]:
        csv_writer= write_files_edge(path_of_directory,label,other_pc_label)
        query= f'Match (n:{label})-[:Parent_Of]->(m:{other_pc_label}) Return n.id, m.id'
        results= g.run(query)
        for result in results:
            [id1, id2] = result.values()
            csv_writer.writerow([id1,id2])


def main():
    print(datetime.datetime.now())

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path MED-RT ')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_to_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate files')

    counter=0

    for label in pc_labels:
        name_without_med_and_lowercase = label.replace('_MEDRT','').lower()

        csv_new = write_files(path_of_directory, name_without_med_and_lowercase, label)

        print('##########################################################################')

        print(datetime.datetime.now())
        print('Load all label from database')

        load_all_label_and_map(label, csv_new)

        print('##########################################################################')

        print(datetime.datetime.now())
        print('Prepare parent edges')

        prepare_parent_of_files(label, counter, path_of_directory)

        print('##########################################################################')

        print(datetime.datetime.now())
        counter+=1


    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
