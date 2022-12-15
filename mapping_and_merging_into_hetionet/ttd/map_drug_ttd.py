import csv, sys
import datetime

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()



def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped):
    for map_id in mapped_ids:
        csv_writer.writerow([raw_id, map_id, pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[map_id], "TTD"), how_mapped])
        
        
def load_chemical_information():
    """
    Load chemical information into different dictionaries
    :return:
    """
    global dict_chemical_id_to_resource, dict_name_to_chemical_ids, dict_inchikey_to_chemical_ids
    global dict_pubchem_c_ids_to_identifier, dict_smiles_to_chemicals
    dict_chemical_id_to_resource = {}
    dict_name_to_chemical_ids = {}
    dict_inchikey_to_chemical_ids = {}
    dict_smiles_to_chemicals = {}
    dict_pubchem_c_ids_to_identifier={}
    
    query = "MATCH (n:Chemical) RETURN n.identifier, n.xrefs, n.resource, n.name, n.synonyms, n.inchikey, n.smiles"
    result = g.run(query)
    
    for identifier, xref, resource, name, synonyms, inchikey, smiles, in result:
    
        dict_chemical_id_to_resource[identifier] = resource
    
        if xref is not None:
            for x in xref:
                if "PubChem Compound" in x:
                    pubchem_compound=x.split(':',1)[1]
                    pharmebinetutils.add_entry_to_dict_to_set(dict_pubchem_c_ids_to_identifier, pubchem_compound, identifier)

        if inchikey is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_inchikey_to_chemical_ids,inchikey,identifier)

        if name is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids,name.lower(),identifier)
    
        if synonyms is not None:
            for synonym in synonyms:
                pharmebinetutils.add_entry_to_dict_to_set(dict_name_to_chemical_ids,synonym.lower(), identifier)

        if smiles is not None:
            pharmebinetutils.add_entry_to_dict_to_set(dict_smiles_to_chemicals, smiles, identifier)

def compound_ttd_mapping():

    # save the identifier and the Raw_ID in a tsv file
    file_name='drug/drug_mapping.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = [ "node_id","identifier", "resource", "how_mapped", 'inchikey', 'smiles']
        writer.writerow(line)
        query = "MATCH (n:TTD_Drug) RETURN n.id, n.canonical_smiles, n.inchi_key, n.name, n.pubchem_cids"
        result = g.run(query)

        counter=0
        counter_mapped=0
        for node_id, smiles, inchikey,name, pubchem_cids, in result:
            counter+=1
            mapping_found=False
            if inchikey in dict_inchikey_to_chemical_ids:
                counter_mapped+=1
                mapping_found = True
                for identifier in dict_inchikey_to_chemical_ids[inchikey]:
                    writer.writerow([node_id,identifier,pharmebinetutils.resource_add_and_prepare(dict_chemical_id_to_resource[identifier],'TTD'),'inchikey', inchikey,smiles])

            if mapping_found:
                continue

            if smiles is not None:
                if smiles in dict_smiles_to_chemicals:
                    counter_mapped += 1
                    mapping_found = True
                    for identifier in dict_smiles_to_chemicals[smiles]:
                        writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_id_to_resource[identifier],'TTD'), 'smiles', inchikey,smiles])
            if mapping_found:
                continue

            if pubchem_cids is not None:
                if name is None or not( ' + ' in name or 'combination' in name.lower() or '; ' in name or '/ ' in name):
                    for pubchem_cid in pubchem_cids:
                        if pubchem_cid in dict_pubchem_c_ids_to_identifier:
                            mapping_found = True
                            for identifier in dict_pubchem_c_ids_to_identifier[pubchem_cid]:
                                writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
                                    dict_chemical_id_to_resource[identifier],'TTD'), 'pubchem', inchikey,smiles])
            if mapping_found:
                counter_mapped += 1
                continue

            if name is not None:
                name=name.lower()
                if name in dict_name_to_chemical_ids:
                    counter_mapped += 1
                    mapping_found = True
                    for identifier in dict_name_to_chemical_ids[name]:
                        writer.writerow([node_id, identifier, pharmebinetutils.resource_add_and_prepare(
                            dict_chemical_id_to_resource[identifier],'TTD'), 'name', inchikey,smiles])
            if mapping_found:
                continue

    print('number of nodes:',counter)
    print('number of mapped nodes:',counter_mapped)
    print("######### Start: Cypher #########")

    # cypher file
    with open("output/cypher.cypher", "a", encoding="utf-8") as cypher_file:
        query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/ttd/{file_name}" As line fieldterminator "\t" '
        query = query_start + f'Match (p1:TTD_Drug{{id:line.node_id}}),(p2:Chemical{{identifier:line.identifier}}) SET p2.resource = split(line.resource,"|"), p2.ttd="yes" Create (p1)-[:equal_to_ttd_drug{{how_mapped:line.how_mapped }}]->(p2);\n'
        cypher_file.write(query)

        query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/ttd/{file_name}" As line fieldterminator "\t" '
        query = query_start + f'Match (p2:Chemical{{identifier:line.identifier}}) Where exists(line.inchikey) and not exists(p2.inchikey) SET p2.inchikey = line.inchikey;\n'
        cypher_file.write(query)

        query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/ttd/{file_name}" As line fieldterminator "\t" '
        query = query_start + f'Match (p2:Chemical{{identifier:line.identifier}}) Where exists(line.smiles) and not exists(p2.smiles) SET p2.smiles = line.smiles;\n'
        cypher_file.write(query)

    print("######### End: Cypher #########")


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path ttd')

    print(datetime.datetime.now())
    print('create connection')
    create_connection_with_neo4j()

    print('#'*50)
    print(datetime.datetime.now())
    print('load chemical information')
    load_chemical_information()

    print('#'*50)
    print(datetime.datetime.now())
    print('map compound')
    compound_ttd_mapping()

if __name__ == "__main__":
    # execute only if run as a script
    main()
