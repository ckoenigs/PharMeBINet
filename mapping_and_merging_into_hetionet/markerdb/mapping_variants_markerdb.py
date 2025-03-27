import csv
import datetime
import os
import re, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils
# import create_connection_to_database_metabolite


# dictionary variant id to resource
dict_variant_id_to_resource = {}

# dictionary name to identifier
dict_name_to_id={}

# dictionary dbSNP id to identifier
dbsnp_identifier_map = {}

dict_id_to_name={}

def load_variants_from_database_and_add_to_dict():


    # Define the Cypher query to fetch dbSNP IDs and identifiers
    cypher_query = (
        "MATCH (n:Variant)  RETURN n.identifier AS identifier, n.xrefs as xrefs, n.resource AS resource, n.name as name, n.cytogenetic_location" )
    results = g.run(cypher_query)
    for record in results:
        [identifier, xrefs, resource, name, location] = record.values()
        dict_variant_id_to_resource[identifier] = resource
        if xrefs:
            for xref in xrefs:
                if xref.startswith('dbSNP'):
                    dbsnp_id = xref.split(":")[1]  # Extract dbSNP ID
                    pharmebinetutils.add_entry_to_dict_to_set(dbsnp_identifier_map, dbsnp_id, identifier)

        name=name
        dict_id_to_name[identifier]=name
        if name:
            if len(name.split(':'))>1:
                name=name.split(':')[1]
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_id, name.lower(), (identifier,location))



def generate_files(path_of_directory):
    """
    generate cypher file and tsv file
    :return: tsv file
    """
    # make sure folder exists
    if not os.path.exists(path_of_directory):
        os.mkdir(path_of_directory)

    file_name = 'MarkerDB_variant_to_Variant'
    file_path = os.path.join(path_of_directory, file_name) + '.tsv'
    header = ['MarkerDB_variant_id', 'identifier', 'resource', 'mapping_method']
    # 'w+' creates file, 'w' opens file for writing
    mode = 'w' if os.path.exists(file_path) else 'w+'
    file = open(file_path, mode, encoding='utf-8')
    csv_mapping = csv.writer(file, delimiter='\t')
    csv_mapping.writerow(header)

    file_name_new= 'not_mapped.tsv'
    file_path_new = os.path.join(path_of_directory, file_name_new)
    file_new = open(file_path_new, "w", encoding='utf-8')
    csv_new = csv.writer(file_new, delimiter='\t')
    csv_new.writerow(['MarkerDB_variant_id', 'identifier'])

    if not os.path.exists(source):
        os.mkdir(source)

    cypher_file_path = os.path.join(source, 'cypher.cypher')
    # mapping_and_merging_into_hetionet/MarkerDB/
    query = (f' Match (n:MarkerDB_SequenceVariant{{id:toInteger(line.MarkerDB_variant_id)}}), (v:Variant{{'
             f'identifier:line.identifier}}) Set v.markerdb="yes", v.resource=split(line.resource,"|") Create (v)-['
             f':equal_to_MarkerDB_variant{{mapped_with:line.mapping_method}}]->(n)')
    mode = 'a' if os.path.exists(cypher_file_path) else 'w'
    query = pharmebinetutils.get_query_import(path_of_directory, file_name + '.tsv', query)
    cypher_file = open(cypher_file_path, mode, encoding='utf-8')
    cypher_file.write(query)

    query = f' Match (n:MarkerDB_SequenceVariant{{id:toInteger(line.MarkerDB_variant_id)}}) Merge (p:Variant :GeneVariant{{identifier:line.identifier }}) On Create Set p.cytogenetic_location=n.position , p.resource=["MarkerDB"], p.xrefs=["dbSNP:"+line.identifier], p.markerdb="yes", p.source="dbSNP from MarkerDB", p.license="CC BY-NC 4.0 Deed"  Create (p)-[:equal_to_MarkerDB_variant{{mapped_with:"new"}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              file_name_new,
                                              query)
    cypher_file.write(query)

    return csv_mapping, csv_new

def load_all_MarkerDB_variants_and_finish_the_files(csv_mapping, csv_new):
    """
    Load all variation sort the ids into the right tsv, generate the queries, and add rela to the rela tsv
    """
    #  Where n.variation contains 'rs'
    query = "Match (n:MarkerDB_SequenceVariant) Where not n.reference is null Return n.id, n.variation, n.external_link, n.position"
    results = g.run(query)
    counter_not_mapped = 0
    counter_all = 0
    counter_new=0
    pattern = r'rs\d+'
    for record in results:
        [unique_id, identifier, external_link, position] = record.values()
        if unique_id==34895:
            print('here')
        counter_all += 1
        rs_id=''
        name=''
        if identifier:
            match = re.search(pattern, identifier)
            if match:
                rs_id = match.group()
                if '(' in identifier:
                    name=identifier.split(' (')[0]
            identifier = identifier.lower()
        # mapping
        #if rs_id == "rs368270856":
            #print(rs_id, dict_variant_id_to_resource[rs_id])

        is_mapped=False
        if external_link:
            clinvar_id=external_link.rsplit('/', 1)[-1]
            if clinvar_id in dict_variant_id_to_resource:
                is_mapped=True
                csv_mapping.writerow(
                    [unique_id, clinvar_id,
                     pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[clinvar_id], "MarkerDB"),
                     'external_references'])

        if is_mapped:
            continue

        if rs_id in dict_variant_id_to_resource:
            is_mapped=True
            list_of_names=[]
            if name:
                list_of_names=[x for x in  dbsnp_identifier_map[rs_id] if dict_id_to_name[x] and name in dict_id_to_name[x] ]
            if len(list_of_names)>0:
                for variant_id in list_of_names:
                    csv_mapping.writerow(
                        [unique_id, variant_id,
                         pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[variant_id], "MarkerDB"),
                         'dbSNP_name'])
            else:
                for variant_id in dbsnp_identifier_map[rs_id]:
                    csv_mapping.writerow(
                        [unique_id, variant_id,
                         pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[variant_id], "MarkerDB"),
                         'dbSNP'])
                    
        elif identifier in dict_name_to_id:
            for (variant_id,location) in dict_name_to_id[identifier]:
                if location==position:
                    is_mapped=True
                    csv_mapping.writerow(
                        [unique_id, variant_id,
                         pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[variant_id], "MarkerDB"),
                         'name'])

        if is_mapped:
            continue

        if name in dict_name_to_id:
            for (variant_id,location) in dict_name_to_id[name]:
                if location==position:
                    csv_mapping.writerow(
                        [unique_id, variant_id,
                         pharmebinetutils.resource_add_and_prepare(dict_variant_id_to_resource[variant_id], "MarkerDB"),
                         'name-split'])
        else:
            if rs_id:
                csv_new.writerow([unique_id, rs_id])
                counter_new +=1
                continue
            counter_not_mapped += 1

    print('number of not-mapped variants:', counter_not_mapped)
    print('number of new variants:', counter_new)
    print('number of all variants:', counter_all)

def create_connection_with_neo4j():
    """
    create a connection with neo4j
    """
    # set up authentication parameters and connection
    global g, driver
    # driver = create_connection_to_database_metabolite.database_connection_neo4j_driver()
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

def main():
    global path_of_directory
    global source
    global home

    # path_of_directory = "/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test"
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path')
    home = os.getcwd()
    source = os.path.join(home, 'output')
    path_of_directory = os.path.join(home, 'variant/')


    print('##########################################################################')
    print(datetime.datetime.now())
    print('connection to db')
    create_connection_with_neo4j()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all Variants from database')
    load_variants_from_database_and_add_to_dict()
    print('##########################################################################')

    print(datetime.datetime.now())
    print('Generate cypher and tsv file')
    csv_mapping, csv_new = generate_files(path_of_directory)

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all MarkerDB variants from database')
    load_all_MarkerDB_variants_and_finish_the_files(csv_mapping, csv_new)

    driver.close()


if __name__ == "__main__":
    main()
