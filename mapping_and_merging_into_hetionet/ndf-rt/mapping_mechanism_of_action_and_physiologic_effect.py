import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j_and_mysql():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()


# dictionary pharmacologic class id to name
dict_pharmacologic_class_id_to_name = {}

# dictionary pharmacologic class id to resource
dict_pharmacologic_class_id_to_resource = {}

'''
Load all PharmacologicClass from my database  and add them into a dictionary
'''


def load_pharmacologic_class_from_database_and_add_to_dict():
    query = "MATCH (n:PharmacologicClass) RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']
        resource = node['resource']
        name = node['name'].lower()
        dict_pharmacologic_class_id_to_name[identifier] = name
        dict_pharmacologic_class_id_to_resource[identifier] = set(resource)


cypher_file = open('output/cypher.cypher', 'a', encoding='utf-8')


def write_files(path_of_directory, addition_name, label):
    # file from relationship between gene and variant
    file_name_mapped = 'pharmacologicClass/mapping_' + addition_name + '.tsv'
    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_mapped = csv.writer(file_mapped, delimiter='\t')
    header_mapped = ['code', 'id', 'resource', 'xrefs', 'synonyms']
    csv_mapped.writerow(header_mapped)

    file_name_new = 'pharmacologicClass/new_' + addition_name + '.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header_new = ['code', 'id', 'xrefs', 'synonyms']
    csv_new.writerow(header_new)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
            Match (n:%s{code:line.code}), (v:PharmacologicClass{identifier:line.id}) Set v.ndf_rt='yes', v.xrefs=split(line.xrefs,'|'), v.synonyms=split(line.synonyms,'|'), v.resource=split(line.resource,'|') Create (v)-[:equal_to_%s_ndf_rt{how_mapped:'ndf-rt id'}]->(n);\n'''
    query = query % (path_of_directory, file_name_mapped, label, addition_name)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
                Match (n:%s{code:line.code}) Create (v:PharmacologicClass{identifier:line.id, ndf_rt:'yes', xrefs:split(line.xrefs,'|'), synonyms:split(line.synonyms,'|'), resource:['NDF-RT'], source:'NDF-RT', url:'http://purl.bioontology.org/ontology/NDFRT/'+line.id, name:split(n.name," [")[0], license:'UMLS license, available at https://uts.nlm.nih.gov/license.html', class_type:"%s"}) Create (v)-[:equal_to_ndf_rt{how_mapped:'new'}]->(n);\n'''
    query = query % (path_of_directory, file_name_new, label,
                     addition_name.replace('_', ' ').replace(' kind', '').title().replace('Of', 'of'))
    cypher_file.write(query)

    return csv_mapped, csv_new


# dictionary name to id from new pc nodes
dict_name_to_new_pc_nodes = {}


def load_all_label_and_map(label, csv_map, csv_new):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH (n:%s) RETURN n" % (label)
    results = g.run(query)
    for node, in results:
        identifier = node['code']
        name = node['name'].lower()
        name= name.split(' [')[0]

        found_mapping = False
        xrefs = set()
        synonyms = set()
        for property in node['properties']:
            if property.startswith('NUI:'):
                id_nui = property.split(':')[1]
                if id_nui in dict_pharmacologic_class_id_to_name:
                    found_mapping = True
            else:
                splitted_prop = property.split(':', 1)
                if 'name' in splitted_prop[0].lower() or 'synonym' in splitted_prop[0].lower():
                    synonyms.add(splitted_prop[1])
                else:
                    xrefs.add(property)

        # generate a dictionary of the new pc names to identifier
        if name not in dict_name_to_new_pc_nodes:
            dict_name_to_new_pc_nodes[name]=set()
        dict_name_to_new_pc_nodes[name].add(id_nui)

        if found_mapping:
            resource = dict_pharmacologic_class_id_to_resource[id_nui]
            resource.add('NDF-RT')
            csv_map.writerow([identifier, id_nui, '|'.join(sorted(resource)), '|'.join(xrefs), '|'.join(synonyms)])
        else:
            csv_new.writerow([identifier, id_nui, '|'.join(xrefs), '|'.join(synonyms)])

def write_files_drug(path_of_directory, addition_name, label):
    # file from relationship between gene and variant
    file_name_mapped = 'pharmacologicClass/mapping_' + addition_name + '.tsv'
    file_mapped = open(file_name_mapped, 'w', encoding='utf-8')
    csv_mapped = csv.writer(file_mapped, delimiter='\t')
    header_mapped = ['code', 'id', 'resource', 'xrefs', 'synonyms']
    csv_mapped.writerow(header_mapped)

    file_name_new = 'pharmacologicClass/new_' + addition_name + '.tsv'
    file_new = open(file_name_new, 'w', encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    header_new = ['code', 'id', 'xrefs', 'synonyms']
    csv_new.writerow(header_new)

    file_name_other = 'pharmacologicClass/other_' + addition_name + '.tsv'
    file_other = open(file_name_other, 'w', encoding='utf-8')
    csv_other = csv.writer(file_other, delimiter='\t')
    header_other = ['code', 'id']
    csv_other.writerow(header_other)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
            Match (n:%s{code:line.code}), (v:PharmacologicClass{identifier:line.id}) Set v.ndf_rt='yes', v.xrefs=split(line.xrefs,'|'), v.synonyms=split(line.synonyms,'|'), v.resource=split(line.resource,'|') Create (v)-[:equal_to_%s_ndf_rt{how_mapped:'ndf-rt id'}]->(n);\n'''
    query = query % (path_of_directory, file_name_mapped, label, addition_name)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
                Match (n:%s{code:line.code}), (v:PharmacologicClass{identifier:line.id})  Create (v)-[:equal_to_%s_ndf_rt{how_mapped:'ndf-rt id'}]->(n);\n'''
    query = query % (path_of_directory, file_name_other, label, addition_name)
    cypher_file.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/ndf-rt/%s" As line FIELDTERMINATOR '\\t' 
                Match (n:%s{code:line.code}) Create (v:PharmacologicClass{identifier:line.id, ndf_rt:'yes', xrefs:split(line.xrefs,'|'), synonyms:split(line.synonyms,'|'), resource:['NDF-RT'], source:'NDF-RT', url:'http://purl.bioontology.org/ontology/NDFRT/'+line.id, name:split(n.name," [")[0], license:'UMLS license, available at https://uts.nlm.nih.gov/license.html', class_type:"Established Pharmacologic Class"}) Create (v)-[:equal_to_%s_ndf_rt{how_mapped:'new'}]->(n);\n'''
    query = query % (path_of_directory, file_name_new, label,
                     addition_name)
    cypher_file.write(query)

    return csv_mapped, csv_new, csv_other


def load_all_label_and_map_drug_to_pc(csv_map, csv_new, csv_other):
    """
    Load all ingredients from neo4j and ma them with xrefs of ingredient and name
    :param csv_map: csv writter
    :return:
    """
    query = "MATCH  (n:NDF_RT_DRUG_KIND) Where n.name contains \"[EPC]\"  RETURN n"
    results = g.run(query)
    for node, in results:
        identifier = node['code']
        name = node['name'].lower().split(' [')[0]

        found_mapping = False
        xrefs = set()
        synonyms = set()
        for property in node['properties']:
            if property.startswith('NUI:'):
                id_nui = property.split(':')[1]
                if id_nui in dict_pharmacologic_class_id_to_name:
                    found_mapping = True
            else:
                splitted_prop = property.split(':', 1)
                if 'name' in splitted_prop[0].lower() or 'synonym' in splitted_prop[0].lower():
                    synonyms.add(splitted_prop[1])
                else:
                    xrefs.add(property)

        if found_mapping:
            resource = dict_pharmacologic_class_id_to_resource[id_nui]
            resource.add('NDF-RT')
            csv_map.writerow([identifier, id_nui, '|'.join(sorted(resource)), '|'.join(xrefs), '|'.join(synonyms)])
        elif name in dict_name_to_new_pc_nodes:
            for id_nui in dict_name_to_new_pc_nodes[name]:
                csv_other.writerow([identifier,id_nui])

        else:
            csv_new.writerow([identifier, id_nui, '|'.join(xrefs), '|'.join(synonyms)])


def main():
    print(datetime.datetime.utcnow())

    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path NDF-RT ')

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')

    create_connection_with_neo4j_and_mysql()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all Pharmacologic classes from database')

    load_pharmacologic_class_from_database_and_add_to_dict()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Generate files')

    for label in ['NDF_RT_MECHANISM_OF_ACTION_KIND', 'NDF_RT_PHYSIOLOGIC_EFFECT_KIND', 'NDF_RT_PHARMACOKINETICS_KIND',
                  'NDF_RT_THERAPEUTIC_CATEGORY_KIND']:
        name_without_ndf_and_lowercase = label.replace('NDF_RT_', '').lower()

        csv_mapper, csv_new = write_files(path_of_directory, name_without_ndf_and_lowercase, label)

        print('##########################################################################')

        print(datetime.datetime.utcnow())
        print('Load all label from database')

        load_all_label_and_map(label, csv_mapper, csv_new)

        print('##########################################################################')

        print(datetime.datetime.utcnow())

    label ='NDF_RT_DRUG_KIND'
    name_without_ndf_and_lowercase = label.replace('NDF_RT_', '').lower()
    csv_mapper, csv_new, csv_other = write_files_drug(path_of_directory, name_without_ndf_and_lowercase, label)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('Load all label from database for drug to pc')

    load_all_label_and_map_drug_to_pc( csv_mapper, csv_new, csv_other)

if __name__ == "__main__":
    # execute only if run as a script
    main()
