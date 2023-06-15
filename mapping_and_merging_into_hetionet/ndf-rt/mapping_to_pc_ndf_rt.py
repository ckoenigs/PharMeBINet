import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_to_neo4j():
    # set up authentication parameters and connection
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session()


cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')

# dictionary pc id to resource
dict_pharmacologic_class_id_to_resource = {}
# dictionary name to pc ids
dict_name_to_pharmacologic_class_id = {}


def load_pharmacologic_class_from_database_and_add_to_dict():
    """
    Load all PC information into dicitonaries.
    :return:
    """
    query = "MATCH (n:PharmacologicClass) RETURN n"
    results = g.run(query)
    for record in results:
        node = record.data()['n']
        identifier = node['identifier']
        resource = node['resource']
        name = node['name'].lower()
        pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_pharmacologic_class_id, name, identifier)
        dict_pharmacologic_class_id_to_resource[identifier] = set(resource)


def write_files(path_of_directory, label):
    # file from relationship between gene and variant
    file_name_mapped = 'pharmacologicClass/mapped_' + label + '.tsv'
    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_mapped = csv.writer(file_mapped, delimiter='\t')
    header_mapped = ['id', 'pc_id', 'resource', 'mapped']
    csv_mapped.writerow(header_mapped)

    query = f'''Match (n:{label}{{code:line.id}}) , (v:PharmacologicClass{{identifier:line.pc_id}}) Set v.resource=split(line.resource,"|"), v.ndf_rt="yes" Create (v)-[:equal_to_ndf_rt{{how_mapped:line.mapped}}]->(n)'''

    query = pharmebinetutils.get_query_import(path_of_directory,
                                              f'mapping_and_merging_into_hetionet/ndf-rt/{file_name_mapped}',
                                              query)
    cypher_file.write(query)

    return csv_mapped


def load_all_label_and_map(label, csv_mapped):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_mapped: csv writter
    :param label: string
    :return:
    """
    query = "MATCH (n:%s) RETURN n" % label
    results = g.run(query)
    counter = 0
    counter_mapped = 0
    for record in results:
        counter += 1
        node = record.data()['n']
        identifier = node['code']
        xrefs = set()
        for property in node['properties']:
            if property.startswith('NUI:'):
                id_nui = property.split(':')[1]
            else:
                splitted_prop = property.split(':', 1)
                if not ('name' in splitted_prop[0].lower() or 'synonym' in splitted_prop[0].lower()):
                    xrefs.add(property)

        name = node['name'].lower().split(' [')[0]
        if id_nui in dict_pharmacologic_class_id_to_resource:
            counter_mapped += 1
            csv_mapped.writerow([identifier, id_nui, pharmebinetutils.resource_add_and_prepare(
                dict_pharmacologic_class_id_to_resource[id_nui], 'NDF-RT'), 'ndf_rt_id'])

        elif name in dict_name_to_pharmacologic_class_id:
            counter_mapped += 1
            for pc_id in dict_name_to_pharmacologic_class_id[name]:
                csv_mapped.writerow([identifier, pc_id, pharmebinetutils.resource_add_and_prepare(
                    dict_pharmacologic_class_id_to_resource[pc_id], 'NDF-RT'), 'name'])

    print(label, 'number of nodes', counter)
    print(label, 'number of mapped nodes', counter_mapped)


def map_drug_to_pc(csv_mapped):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH  (n:NDFRT_DRUG_KIND) Where n.name contains \"[EPC]\"  RETURN n"
    results = g.run(query)
    counter = 0
    counter_mapped = 0
    for record in results:
        counter+=1
        node = record.data()['n']
        identifier = node['code']
        name = node['name'].lower().split(' [')[0]

        found_mapping = False
        xrefs = set()
        for property in node['properties']:
            if property.startswith('NUI:'):
                id_nui = property.split(':')[1]
            else:
                splitted_prop = property.split(':', 1)
                if not ('name' in splitted_prop[0].lower() or 'synonym' in splitted_prop[0].lower()):
                    xrefs.add(property)

        if id_nui in dict_pharmacologic_class_id_to_resource:
            counter_mapped += 1
            csv_mapped.writerow([identifier, id_nui, pharmebinetutils.resource_add_and_prepare(
                dict_pharmacologic_class_id_to_resource[id_nui], 'NDF-RT'), 'ndf_rt_id'])




    print('drug number of nodes', counter)
    print('drug number of mapped nodes', counter_mapped)


def main():
    print(datetime.datetime.now())

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path NDF-RT ')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_to_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load pc')

    load_pharmacologic_class_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate files')

    for label in ['NDFRT_MECHANISM_OF_ACTION_KIND', 'NDFRT_PHYSIOLOGIC_EFFECT_KIND', 'NDFRT_PHARMACOKINETICS_KIND',
                  'NDFRT_THERAPEUTIC_CATEGORY_KIND']:
        csv_mapped = write_files(path_of_directory, label)

        print('##########################################################################')

        print(datetime.datetime.now())
        print('Load all label from database')

        load_all_label_and_map(label, csv_mapped)

        print('##########################################################################')

        print(datetime.datetime.now())

    print('map ndf-rt drug epc to pc')

    csv_mapped = write_files(path_of_directory, 'NDFRT_DRUG_KIND')

    print('##########################################################################')

    print(datetime.datetime.now())

    map_drug_to_pc(csv_mapped)

    driver.close()


if __name__ == "__main__":
    # execute only if run as a script
    main()
