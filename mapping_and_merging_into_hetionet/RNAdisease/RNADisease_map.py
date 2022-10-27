import csv, sys

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils

# cypher file
cypher_file=open("output/cypher.cypher","w",encoding="utf-8")

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()

    return g

def write_infos_into_file(csv_writer, raw_id, mapped_ids, how_mapped, dic):
    for map_id in mapped_ids:
        csv_writer.writerow([raw_id, map_id, pharmebinetutils.resource_add_and_prepare(dic[map_id], "RNADisease"), how_mapped])


def disease_RNAdisease():
    '''
    Mapping between Disease and disease_RNADisease
    '''

    print("######### load_from_database ##################")
    global Disease
    Disease= {}
    DiseaseXref={}
    DiseaseIds={}
    DiseaseName={}

    query = "MATCH (n:Disease) RETURN n.identifier, n.alternative_ids, n.xrefs, n.resource, n.name, n.synonyms"
    result = g.run(query)

    for id, ids, xrefs, resource, name, synonym, in result:
        Disease[id]=resource

        if xrefs is not None:
            for x in xrefs:
                if "MESH:" in x:
                    pubid = x[5:]
                    if pubid not in DiseaseXref:
                        DiseaseXref[pubid] = [id]
                    elif id not in DiseaseXref[pubid]:
                        DiseaseXref[pubid].append(id)
        if ids is not None:
            for y in ids:
                if y not in DiseaseIds:
                    DiseaseIds[y] = [id]
                elif id not in DiseaseIds[y]:
                    DiseaseIds[y].append(id)
        if name is not None:
            if name.lower() not in DiseaseName:
                DiseaseName[name.lower()]=[id]
            elif id not in DiseaseName[name.lower()]:
                DiseaseName[name.lower()].append(id)
        if synonym is not None:
            for syn in synonym:
                syn_name = pharmebinetutils.prepare_obo_synonyms(syn)
                if syn_name.lower() not in DiseaseName:
                    DiseaseName[syn_name.lower()]=[id]
                elif id not in DiseaseName[syn_name.lower()]:
                    DiseaseName[syn_name.lower()].append(id)




    global Symptom
    Symptom= {}
    SymptomName={}

    query = "MATCH (n:Symptom) RETURN n.identifier, n.resource, n.name, n.synonyms"
    result = g.run(query)

    for id, resource, name, synonym, in result:
        Symptom[id]=resource

        if name is not None:
            if name.lower() not in SymptomName:
                SymptomName[name.lower()]=[id]
            elif id not in SymptomName[name.lower()]:
                SymptomName[name.lower()].append(id)
        if synonym is not None:
            for syn in synonym:
                if syn.lower() not in SymptomName:
                    SymptomName[syn.lower()]=[id]
                elif id not in SymptomName[syn.lower()]:
                    SymptomName[syn.lower()].append(id)

    file_name = 'disease/disease_RNADiseaseedges.tsv'
    file_name_symptom='disease/disease_Symptom_edges.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        with open(file_name_symptom, 'w', newline='') as tsv_file1:
            writer = csv.writer(tsv_file, delimiter='\t')
            writer1 = csv.writer(tsv_file1, delimiter='\t')
            line = ["id1", "id2", "resource", "how_mapped"]
            writer.writerow(line)
            writer1.writerow(line)

            query = "MATCH (n:disease_RNADisease) RETURN n.DO_ID, n.MeSH_ID, n.Disease_Name"
            result = g.run(query)
            for doid, mesh, name, in result:
                map = False

                if name.lower() in DiseaseName:
                    map = True
                    write_infos_into_file(writer,name, DiseaseName[name.lower()],"Disease_Name-Name/Synonyms",Disease)
                elif name.lower() in SymptomName:
                    map = True
                    write_infos_into_file(writer1, name, SymptomName[name.lower()], "Disease_Name-Symptom Name/Synonyms",Symptom)
                # not good mapping ids
                if name.lower() in ['inflammation']:
                    continue
                if map == False and mesh is not None:
                    for y in mesh:
                        if y in DiseaseXref:
                            map = True
                            write_infos_into_file(writer, name, DiseaseXref[y], 'Mesh_Id-Diseasexrefs', Disease)
                if map == False and  doid is not None:
                    for x in doid:
                        if x in DiseaseIds:
                            write_infos_into_file(writer, name, DiseaseIds[x], 'DO_ID-alternativeids', Disease)


        tsv_file.close()

    print("######### Start: Cypher #########")
    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAdisease/{file_name}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:disease_RNADisease{{Disease_Name:line.id1}}),(p2:Disease{{identifier:line.id2}}) SET p2.resource = split(line.resource,"|"), p2.rnadisease = "yes" Create (p1)-[:associateRNADisease_disease{{how_mapped:line.how_mapped}}]->(p2);\n'
    cypher_file.write(query)

    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAdisease/{file_name_symptom}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:disease_RNADisease{{Disease_Name:line.id1}}),(p2:Symptom{{identifier:line.id2}}) SET p2.resource = split(line.resource,"|"), p2.rnadisease = "yes" Create (p1)-[:associateRNADisease_Symptom{{how_mapped:line.how_mapped}}]->(p2);\n'
    cypher_file.write(query)
    print("######### End: Cypher #########")

def rna_RNAdisease():
    '''
    Mapping between RNA and rna_RNADisease
    '''

    print("######### load_from_database #########")
    global RNA
    RNA= {}
    RNAXref={}
    RNAname={}

    query = "MATCH (n:RNA) RETURN n.identifier, n.geneName, n.xrefs, n.resource"
    result = g.run(query)

    for id, name, xrefs, resource, in result:
        RNA[id]=resource

        if xrefs is not None:
            for x in xrefs:
                result = x.split(":")[1]
                pharmebinetutils.add_entry_to_dict_to_set(RNAXref,result, id)
        if name is not None:
            for n in name:
                pharmebinetutils.add_entry_to_dict_to_set(RNAname,n, id)

    file_name='rna/rna_RNADiseaseedges.tsv'
    with open(file_name, 'w', newline='') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        line = ["id1", "id2", "resource", "how_mapped"]
        writer.writerow(line)

        query = "MATCH (n:rna_RNADisease) RETURN n.RNA_Symbol"
        result = g.run(query)
        for symbol, in result:
            if symbol in RNAname:
                write_infos_into_file(writer, symbol, RNAname[symbol], 'Symbol-Gene_Name',RNA)
            elif symbol in RNAXref:
                # the AC identifier mapping is not good
                if symbol.startswith('AC'):
                    continue
                write_infos_into_file(writer, symbol, RNAXref[symbol], 'Symbol-Xrefs', RNA)


        tsv_file.close()

    print("######### Start: Cypher #########")
    query_start = f'Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:{path_of_directory}mapping_and_merging_into_hetionet/RNAdisease/{file_name}" As line fieldterminator "\t" '
    query = query_start + f'Match (p1:rna_RNADisease{{RNA_Symbol:line.id1}}),(p2:RNA{{identifier:line.id2}}) SET p2.resource = split(line.resource,"|"), p2.rnadisease = "yes" Create (p1)-[:associateRNADisease_rna{{how_mapped:line.how_mapped}}]->(p2);\n'
    cypher_file.write(query)
    print("######### End: Cypher #########")

def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path rnadisease')

    create_connection_with_neo4j()
    disease_RNAdisease()
    rna_RNAdisease()

if __name__ == "__main__":
    # execute only if run as a script
    main()