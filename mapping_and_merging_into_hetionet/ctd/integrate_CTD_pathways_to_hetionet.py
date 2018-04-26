# -*- coding: utf-8 -*-
"""
Created on Wed Apr 18 12:41:20 2018

@author: ckoenigs
"""

from py2neo import Graph, authenticate
import datetime
import csv
import sys

'''
create connection to neo4j 
'''


def create_connection_with_neo4j_mysql():
    # create connection with neo4j
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# dictionary with hetionet pathways with identifier as key and value the name
dict_pathway_hetionet = {}

'''
load in all pathways from hetionet in a dictionary
'''


def load_hetionet_pathways_in():
    query = '''MATCH (n:Pathway) RETURN n.identifier,n.name'''
    results = g.run(query)

    for identifier, name, in results:
        dict_pathway_hetionet[identifier] = name

    print('number of pathway nodes in hetionet:' + str(len(dict_pathway_hetionet)))


# dictionary of pathways which are not in hetionet with they properties: name
dict_ctd_pathway_not_in_hetionet = {}

# dictionary of ctd pathways which are in hetionet with properties: name
dict_ctd_pathway_in_hetionet = {}

# dictionary with all pathways which are mapped to pc or wp with propertie wp, pc id and propertie pathway identifier, name, source
dict_ctd_pathway_mapped_to_pc_or_wp = {}

# dictionary with all pathways which are not mapped to pc or wp with pathway identifier and properties name, source
dict_ctd_pathways_not_mapped = {}

# dictionary pathway name from pathway list an the identifier plus the source
dict_name_to_pc_or_wp_identifier = {}

# dictionary transform the named source in ctd to the one in pathway himmelstein
dict_source_ctd_to_source_pc_or_wp = {
    "REACT": 'reactome',
    "KEGG": 'kegg'
}


'''
load in all pathway with the way himmelstein construct the identifier
https://github.com/dhimmel/pathways
properties:
    0: identifier	
    1:name	
    2:url	
    3:n_genes	
    4:n_coding_genes	
    5:source	
    6:license	
    7:genes	
    -/8:own id
    8/9:coding_genes
all with / is the second for pathwaycommons version9
'''


def load_in_all_pathways_from_himmelsteins_construction():
    with open('pathways_hetionet_data/pathways.tsv') as tsvfile:
        print()
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            identifier = row[0]
            name = row[1]
            source = row[5]
            if name in dict_name_to_pc_or_wp_identifier:
                # print(identifier)
                # print(source)
                # print(name)
                # print(dict_name_to_pc_or_wp_identifier[name])
                dict_name_to_pc_or_wp_identifier[name].append([identifier, source])
            else:
                dict_name_to_pc_or_wp_identifier[name] = [[identifier, source]]
    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))

# dictionary with own id from pc to name, pcid and source
dict_own_id_to_pcid_and_other={}

# pc maximal number for pc id
pc_maximal_number_for_id=999

'''
load in all pathway with the way himmelstein construct of the identifier but for version 9
https://github.com/dhimmel/pathways
properties:
    0: identifier	
    1:name	
    2:url	
    3:n_genes	
    4:n_coding_genes	
    5:source	
    6:license	
    7:genes	
    8:own id
    9:coding_genes
'''


def load_in_all_pathways_from_himmelsteins_construction_version9():
    with open('pathways_hetionet_data/pathways_v9.tsv') as tsvfile:
        print()
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            identifier = row[0]
            name = row[1]
            source = row[5]
            own_id=row[8]
            if name in dict_name_to_pc_or_wp_identifier:
                dict_name_to_pc_or_wp_identifier[name].append([identifier, source])
            else:
                dict_name_to_pc_or_wp_identifier[name] = [[identifier, source]]
            if own_id in dict_own_id_to_pcid_and_other and own_id!="":
                dict_own_id_to_pcid_and_other[own_id].append([identifier,source, name])
            elif own_id in dict_own_id_to_pcid_and_other :
                dict_own_id_to_pcid_and_other[identifier] = [[identifier, source, name]]
            else:
                dict_own_id_to_pcid_and_other[own_id]=[[identifier, source, name]]
    print('number of different pathway names:' + str(len(dict_name_to_pc_or_wp_identifier)))
    print('number of different pathway ids:'+str(len(dict_own_id_to_pcid_and_other)))

# dictionary which is mapped to which source
dict_mapped_source={}

# file for mapped or not mapped identifier
file_not_mapped_pathways = open('pathway/not_mapped_pathways.tsv', 'w')
file_not_mapped_pathways.write('id\tname\tsource\n')

file_mapped_pathways = open('pathway/mapped_pathways.tsv', 'w')
file_mapped_pathways.write('id\tname\tsource\tid_hetionet\tsource_himmelstein\tmapping_method\n')

file_multiple_mapped_pathways = open('pathway/multiple_mapped_pathways.tsv', 'w')
file_multiple_mapped_pathways.write('id_s\tname\tsource_sources\tid_hetionet\tsource_himmelstein\n')

'''
load all ctd pathways and check if they are in hetionet or not
'''


def load_ctd_pathways_in():
    query = '''MATCH (n:CTDpathway) RETURN n'''
    results = g.run(query)

    counter_map_with_id=0
    counter_map_with_name=0
    for pathways_node, in results:
        pathways_id = pathways_node['pathway_id']
        pathways_name = pathways_node['name']
        pathways_id_type = pathways_node['id_type']

        if pathways_id in dict_own_id_to_pcid_and_other:
            counter_map_with_id+=1
            pc_or_wp_id = dict_own_id_to_pcid_and_other[pathways_id][0][0]
            pc_or_wp_source = dict_own_id_to_pcid_and_other[pathways_id][0][1]
            if pc_or_wp_id in dict_ctd_pathway_mapped_to_pc_or_wp:

                dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id].append(
                    [pathways_id, pathways_name, pathways_id_type,
                     pc_or_wp_source])
                pathways_ids = \
                    dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                        0] + '|' + pathways_id
                pathways_id_types = \
                    dict_ctd_pathway_mapped_to_pc_or_wp[dict_own_id_to_pcid_and_other[pathways_id][0][0]][0][
                        3] + '|' + pathways_id_type
                file_multiple_mapped_pathways.write(
                    pathways_ids + '\t' + pathways_name + '\t' + pathways_id_types + '\t' +
                    pc_or_wp_id + '\t' +
                    pc_or_wp_source + '\n')
            else:
                dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id] = [
                    [pathways_id, pathways_name, pathways_id_type,
                     pc_or_wp_source]]
                file_mapped_pathways.write(
                    pathways_id + '\t' + pathways_name + '\t' + pathways_id_type + '\t' +
                    pc_or_wp_id + '\t' +
                    pc_or_wp_source+ '\t id \n')
            if pc_or_wp_source in dict_mapped_source:
                dict_mapped_source[pc_or_wp_source].append(pathways_id_type)
            else:
                dict_mapped_source[pc_or_wp_source] = [pathways_id_type]

        elif pathways_name in dict_name_to_pc_or_wp_identifier:
            counter_map_with_name+=1
            pc_or_wp_id = dict_name_to_pc_or_wp_identifier[pathways_name][0][0]
            pc_or_wp_source = dict_name_to_pc_or_wp_identifier[pathways_name][0][1]

            if len(dict_name_to_pc_or_wp_identifier[pathways_name]) == 1:
                if pc_or_wp_id in dict_ctd_pathway_mapped_to_pc_or_wp:
                    dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id].append(
                        [pathways_id, pathways_name, pathways_id_type,
                         pc_or_wp_source])
                    pathways_ids = \
                    dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                        0] + '|' + pathways_id
                    pathways_id_types = \
                    dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                        3] + '|' + pathways_id_type
                    file_multiple_mapped_pathways.write(
                        pathways_ids + '\t' + pathways_name + '\t' + pathways_id_types + '\t' +
                        pc_or_wp_id +'\t'+
                        pc_or_wp_source + '\n')
                else:
                    dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id] = [
                        [pathways_id, pathways_name, pathways_id_type,
                         pc_or_wp_source]]
                    file_mapped_pathways.write(
                        pathways_id + '\t' + pathways_name + '\t' + pathways_id_type + '\t' +
                        pc_or_wp_id + '\t' +
                        pc_or_wp_source + '\tname\n')
                if pc_or_wp_source  in dict_mapped_source:
                    dict_mapped_source[pc_or_wp_source].append(pathways_id_type)
                else:
                    dict_mapped_source[pc_or_wp_source]=[pathways_id_type]

            else:
                found_with_same_source = False
                for [pc_or_wp_id, source] in dict_name_to_pc_or_wp_identifier[pathways_name]:
                    if dict_source_ctd_to_source_pc_or_wp[pathways_id_type] == source:
                        if pc_or_wp_id in dict_ctd_pathway_mapped_to_pc_or_wp:
                            dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id].append(
                                [pathways_id, pathways_name, pathways_id_type, source])
                            pathways_ids = \
                                dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][
                                    0][0] + '|' + pathways_id
                            pathways_id_types = \
                                dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                                    3] + '|' + pathways_id_type
                            file_multiple_mapped_pathways.write(
                                pathways_ids + '\t' + pathways_name + '\t' + pathways_id_types + '\t' +
                                pc_or_wp_id + '\t' +
                                pc_or_wp_source + '\n')
                        else:
                            dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id] = [
                                [pathways_id, pathways_name, pathways_id_type, source]]
                            file_mapped_pathways.write(
                                pathways_id + '\t' + pathways_name + '\t' + pathways_id_type + '\t' +
                                pc_or_wp_id + '\t' +
                                pc_or_wp_source + '\tname\n')
                        found_with_same_source = True
                        if pc_or_wp_source in dict_mapped_source:
                            dict_mapped_source[pc_or_wp_source].append(
                                pathways_id_type)
                        else:
                            dict_mapped_source[pc_or_wp_source] = [
                                pathways_id_type]
                if not found_with_same_source:

                    if pc_or_wp_id in dict_ctd_pathway_mapped_to_pc_or_wp:
                        dict_ctd_pathway_mapped_to_pc_or_wp[
                            pc_or_wp_id].append(
                            [pathways_id, pathways_name, pathways_id_type,
                             pc_or_wp_source])
                        pathways_ids=pc_or_wp_id+ '|' + pathways_id
                        pathways_id_types = \
                            dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id][0][
                                3] + '|' + pathways_id_type
                        file_multiple_mapped_pathways.write(
                            pathways_ids + '\t' + pathways_name + '\t' + pathways_id_types + '\t' +
                            pc_or_wp_id + '\t' +
                            pc_or_wp_source + '\n')
                    else:
                        dict_ctd_pathway_mapped_to_pc_or_wp[pc_or_wp_id] = [
                            [pathways_id, pathways_name, pathways_id_type,
                             pc_or_wp_source]]
                        file_mapped_pathways.write(
                            pathways_id + '\t' + pathways_name + '\t' + pathways_id_type + '\t' +
                            pc_or_wp_id + '\t' +
                            pc_or_wp_source + '\tname\n')
                    if pc_or_wp_source in dict_mapped_source:
                        dict_mapped_source[pc_or_wp_source].append(
                            pathways_id_type)
                    else:
                        dict_mapped_source[pc_or_wp_source] = [pathways_id_type]

        else:
            dict_ctd_pathways_not_mapped[pathways_id] = [pathways_name, pathways_id_type]
            # file_not_mapped_pathways.write(pathways_id+ '\t' +pathways_name+ '\t' + pathways_id_type+ '\n' )

    print('number of mapped nodes:' + str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))
    print('number of not existing nodes:' + str(len(dict_ctd_pathways_not_mapped)))
    print('number of mapping with name:'+str(counter_map_with_name))
    print('number of mapping with id:' + str(counter_map_with_id))
    print(dict_mapped_source)

own_identifier=1



# dictionary with all human pathways
dict_human_pathways_reactom={}

'''
Generate reactome list of all human pathways 
'''
def add_all_human_pathway_into_dictionary():
    reactome_pathways=open('pathways_hetionet_data/all_reactoms_human_pathway_ids.txt','r')
    for reactom_id in reactome_pathways:
        reactom_id=reactom_id.replace('\n','')
        dict_human_pathways_reactom[reactom_id]='human'

    print('number of reactome human pathways:'+str(len(dict_human_pathways_reactom)))

# list_of all not_mapped identifer
list_not_mapped_identifer=[]

'''
check all reactome identifier if the pathways are in humans and give them an own identifier
'''
def check_if_reactome_identifier_is_part_of_human_pathway():
    global own_identifier
    counter_of_not_mapped_reactome_identifier=0
    for identifier, [name, source] in dict_ctd_pathways_not_mapped.items():
        if source =='REACT':
            if identifier in dict_human_pathways_reactom:
                dict_ctd_pathway_mapped_to_pc_or_wp['own_'+str(own_identifier)] = [
                    [identifier, name, source,
                     '']]
                file_mapped_pathways.write(
                    identifier + '\t' + name + '\t' + source + '\t' +
                    'own_' + str(own_identifier) + '\t' +
                    '' + '\thuman_pathway_reactome\n')
                own_identifier+=1
            else:
                counter_of_not_mapped_reactome_identifier+=1
                list_not_mapped_identifer.append(identifier)
                print(identifier)
                print(name)
        else:
            list_not_mapped_identifer.append(identifier)


    print('number of not mapped:'+str(len(list_not_mapped_identifer)))
    print('number of not mapped reactome identifer:'+str(counter_of_not_mapped_reactome_identifier))
    print('number of mapped pathways:'+str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))


'''
try to map the rest of not mapped pathways from ctd with use of the relationship pathway-gene-chemical, because the relationship gene-pathway can say if the gene are from human
'''
def map_with_relationship_pathway_gene_chemical():
    global own_identifier

    # all pathway identifier which are mapped in this function
    delete_map_pathway = []
    for identifier in list_not_mapped_identifer:
        [name, source]= dict_ctd_pathways_not_mapped[identifier]
        query='''Match p=(c:CTDpathway{pathway_id:"%s"})-[:participates_GP]-(:CTDgene)-[:associates_CG{organism_id:'9606'}]-(:CTDchemical) Return p Limit 1'''
        query=query %(identifier)
        results=g.run(query)
        result=results.evaluate()
        if not result is None:
            # if source=='REACT':
            #     print(result)
            dict_ctd_pathway_mapped_to_pc_or_wp['own_' + str(own_identifier)] = [
                [identifier, name, source,
                 '']]
            file_mapped_pathways.write(
                identifier + '\t' + name + '\t' + source + '\t' +
                'own_' + str(own_identifier) + '\t' +
                '' + '\trelationship with human gene\n')
            own_identifier += 1
            delete_map_pathway.append(list_not_mapped_identifer.index(identifier))
        else:
            file_not_mapped_pathways.write(identifier + '\t' + name + '\t' + source + '\n')

    # delete mapped pathway IDs from list with not mapped CTD identifiers
    delete_map_pathway.sort()
    delete_map_pathway = list(reversed(delete_map_pathway))
    for index in delete_map_pathway:
        list_not_mapped_identifer.pop(index)

    print('number of mapped pathways:' + str(len(dict_ctd_pathway_mapped_to_pc_or_wp)))
    print('number of not mapped:' + str(len(list_not_mapped_identifer)))



'''
Generate cypher and csv for generating the new nodes and the realtionships
'''


def generate_files():
    # add the pathways which are not in hetionet in a csv file
    with open('pathways/new_pathwayss.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ['GeneID', 'GeneName', 'altGeneIDs', 'pharmGKBIDs', 'bioGRIDIDs', 'geneSymbol', 'synonyms', 'uniProtIDs'])
        # add the go nodes to cypher file
        # for pathways_id, [name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms,
        #                   uniProtIDs] in dict_ctd_pathway_react_not_in_hetionet.items():
        #     writer.writerow([pathways_id, name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms, uniProtIDs])

    cypher_file = open('pathway/cypher.cypher', 'w')
    cypher_file.write('begin\n')
    cypher_file.write('Match (c:Gene) Set c.hetionet="yes", c.resource=["Hetionet"];\n')
    cypher_file.write('commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/pathways/new_genes.csv" As line Create (c:Gene{ identifier:toInteger(line.GeneID), name:line.GeneName, altGeneIDs:split(line.altGeneIDs,'|'),pharmGKBIDs:split(line.pharmGKBIDs,'|'),bioGRIDIDs:split(line.bioGRIDIDs,'|'),geneSymbol:split(line.geneSymbol,'|'),synonyms:split(line.synonyms,'|'),uniProtIDs:split(line.uniProtIDs,'|') , url_ctd:" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID ,url: "http://identifiers.org/ncbigene/"+line.GeneID, source:"CTD" ,description:"", chromosome:"", license:"© 2002–2012 MDI Biological Laboratory. © 2012–2018 MDI Biological Laboratory & NC State University. All rights reserved.", hetionet:"no", ctd:"yes", resource:["CTD"]});\n'''
    cypher_file.write(query)

    with open('pathways/mapping.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GeneIDCTD', 'GeneIDHetionet'])
        # add the go nodes to cypher file

        # for pathways_id, [name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms,
        #                   uniProtIDs] in dict_ctd_pathway_react_in_hetionet.items():
        #     writer.writerow(
        #         [pathways_id, pathways_id, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms, uniProtIDs])
        #
        # for pathways_id, [name, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms,
        #                   uniProtIDs] in dict_ctd_pathway_react_not_in_hetionet.items():
        #     writer.writerow(
        #         [pathways_id, pathways_id, altGeneIDs, pharmGKBIDs, bioGRIDIDs, geneSymbol, synonyms, uniProtIDs])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ctd/pathways/mapping.csv" As line Match (c:Gene{ identifier:toInteger(line.GeneIDHetionet)}), (n:CTDgene{gene_id:line.GeneIDCTD}) Create (c)-[:equal_to_CTD_gene]->(n) Where c.hetionet="yes" Set c.ctd="yes", c.resource=c.resource+"CTD", c.altGeneIDs=split(line.altGeneIDs,'|'),c.pharmGKBIDs=split(line.pharmGKBIDs,'|'),c.bioGRIDIDs=split(line.bioGRIDIDs,'|'),c.geneSymbol=split(line.geneSymbol,'|'),c.synonyms=split(line.synonyms,'|'),c.uniProtIDs=split(line.uniProtIDs,'|') , c.url_ctd=" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID;\n'''
    cypher_file.write(query)
    cypher_file.close()


def main():
    print (datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j_mysql()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from hetionet into a dictionary')

    load_hetionet_pathways_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all pathways from d. himmelstein into a dictionary')

    # load_in_all_pathways_from_himmelsteins_construction()
    load_in_all_pathways_from_himmelsteins_construction_version9()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load all ctd pathways from neo4j into a dictionary')

    load_ctd_pathways_in()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Check mapping old to new')

    check_old_to_new_version()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Load in human pathways')

    add_all_human_pathway_into_dictionary()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('check all reactome pathway for human pathways')

    check_if_reactome_identifier_is_part_of_human_pathway()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('check all not mapped pathway if they have pathways which has relationship with a human gene')

    map_with_relationship_pathway_gene_chemical()



    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())
    print('Map generate csv and cypher file ')
    sys.exit()
    generate_files()

    print(
        '###########################################################################################################################')

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
