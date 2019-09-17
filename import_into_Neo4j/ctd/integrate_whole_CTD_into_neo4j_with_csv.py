from py2neo import Graph, authenticate
import sys
import datetime
import csv


# connect with the neo4j database
def database_connection():
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")


# node cypher file number
node_file_number = 1

# edges cypher file number
edges_file_number = 1

# cypher file for all nodes
cypher_file_nodes = open('cypher/nodes_' + str(node_file_number) + '.cypher', 'w')

# cypher file for all relationships
cypher_file_edges = open('cypher/edges_' + str(edges_file_number) + '.cypher', 'w')

# count the number of queries of node generation
counter_nodes_queries = 0
# count the number of queries of node generation
counter_edges_queries = 0
# number of queries in a commit block
constraint_number = 20000
# number of queries in a cypher file
max_queries_for_a_file = 300000

'''
load ctd chemical file and generate cypher file for the nodes with properties:
    0:ChemicalName
    1:ChemicalID
    2:CasRN
    3:Definition
    4:ParentIDs
    5:TreeNumbers
    6:ParentTreeNumbers
    7:Synonyms
    8:DrugBankID
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_chemicals_and_add_to_cypher_file():
    global counter_nodes_queries, cypher_file_nodes, node_file_number
    # say if in neo4j already ctd chemicals exists
    exists_ctd_chemicals_already_in_neo4j = False

    # chck if chemicals are already in neo4j
    query = '''MATCH (n:CTDchemical) RETURN n LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    cypher_file_nodes.write('begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        query = ''' Match (c:CTDchemical) Set c.old_version=True, c.newer_version=False;\n '''
        cypher_file_nodes.write(query)
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chemicals.csv" As line Merge (c:CTDchemical{ chemical_id:split(line.ChemicalID,':')[1]}) On Create Set c.newer_version=True, c.casRN=line.CasRN, c.synonyms=split(line.Synonyms,'|'), c.drugBankIDs=split(line.DrugBankIDs,'|'), c.parentIDs=split(line.ParentIDs,'|'), c.parentTreeNumbers=split(line.ParentTreeNumbers,'|'), c.treeNumbers=split(line.TreeNumbers,'|'), c.definition=line.Definition, c.name=line.ChemicalName On Match Set c.newer_version=True, c.casRN=line.CasRN, c.synonyms=split(line.Synonyms,'|'), c.drugBankIDs=split(line.DrugBankIDs,'|'), c.parentIDs=split(line.ParentIDs,'|'), c.parentTreeNumbers=split(line.ParentTreeNumbers,'|'), c.treeNumbers=split(line.TreeNumbers,'|'), c.definition=line.Definition, c.name=line.ChemicalName;\n '''

    else:
        cypher_file_nodes.write('Create Constraint On (node:CTDchemical) Assert node.chemical_id Is Unique;\n')
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chemicals.csv" As line Create (c:CTDchemical{ chemical_id:split(line.ChemicalID,':')[1] , newer_version:True, casRN:line.CasRN, synonyms:split(line.Synonyms,'|'), drugBankIDs:split(line.DrugBankIDs,'|'), parentIDs:split(line.ParentIDs,'|'), parentTreeNumbers:split(line.ParentTreeNumbers,'|'), treeNumbers:split(line.TreeNumbers,'|'), definition:line.Definition, name:line.ChemicalName});\n '''

    cypher_file_nodes.write(query)


'''
load ctd disease file and generate cypher file for the nodes with properties:
    0:DiseaseName
    1:DiseaseID
    2:AltDiseaseIDs
    3:Definition
    4:ParentIDs
    5:TreeNumbers
    6:ParentTreeNumbers
    7:Synonyms
    8:SlimMappings
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_disease_and_add_to_cypher_file():
    global counter_nodes_queries, cypher_file_nodes, node_file_number
    # say if in neo4j already ctd chemicals exists
    exists_ctd_disease_already_in_neo4j = False

    # chck if chemicals are already in neo4j
    query = '''MATCH (n:CTDdisease) RETURN n LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    cypher_file_nodes.write('begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        query = ''' Match (c:CTDdisease) Set c.old_version=True;\n '''
        cypher_file_nodes.write(query)
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_diseases.csv" As line Merge (c:CTDdisease{ disease_id:split(line.DiseaseID,':')[1]}) On Create Set c.newer_version=True, c.altDiseaseIDs=split(line.AltDiseaseIDs,"|"), c.idType=split(line.DiseaseID,':')[0], c.synonyms=split(line.Synonyms,'|'), c.slimMappings=split(line.SlimMappings,'|'), c.parentIDs=split(line.ParentIDs,'|'), c.parentTreeNumbers=split(line.ParentTreeNumbers,'|'), c.treeNumbers=split(line.TreeNumbers,'|'), c.definition=line.Definition, c.name=line.DiseaseName  On Match Set c.newer_version=True,  c.altDiseaseIDs=split(line.AltDiseaseIDs,"|"), c.idType=split(line.DiseaseID,':')[0], c.synonyms=split(line.Synonyms,'|'), c.slimMappings=split(line.SlimMappings,'|'), c.parentIDs=split(line.ParentIDs,'|'), c.parentTreeNumbers=split(line.ParentTreeNumbers,'|'), c.treeNumbers=split(line.TreeNumbers,'|'), c.definition=line.Definition, c.name=line.DiseaseName;\n '''
    else:
        cypher_file_nodes.write('Create Constraint On (node:CTDdisease) Assert node.disease_id Is Unique;\n')
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_diseases.csv" As line Create (c:CTDdisease{ disease_id:split(line.DiseaseID,':')[1], newer_version:True, altDiseaseIDs:split(line.AltDiseaseIDs,"|"), idType:split(line.DiseaseID,':')[0] , synonyms:split(line.Synonyms,'|'), slimMappings:split(line.SlimMappings,'|'), parentIDs:split(line.ParentIDs,'|'), parentTreeNumbers:split(line.ParentTreeNumbers,'|'), treeNumbers:split(line.TreeNumbers,'|'), definition:line.Definition, name:line.DiseaseName}) ;\n '''

    cypher_file_nodes.write(query)


'''
load ctd pathway file and generate cypher file for the nodes with properties:
    0:PathwayName
    1:PathwayID
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_pathway_and_add_to_cypher_file():
    global counter_nodes_queries, cypher_file_nodes, node_file_number
    # say if in neo4j already ctd chemicals exists
    exists_ctd_pathway_already_in_neo4j = False

    # chck if chemicals are already in neo4j
    query = '''MATCH (n:CTDpathway) RETURN n LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    cypher_file_nodes.write('begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        query = ''' Match (c:CTDpathway) Set c.old_version=True;\n '''
        cypher_file_nodes.write(query)
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_pathways.csv" As line Merge (c:CTDpathway{ pathway_id:split(line.PathwayID,":")[1]}) On Create Set c.id_type=split(line.PathwayID,':')[0], c.newer_version=True, c.idType=split(line.PathwayID,":")[0], c.name=line.PathwayName  On Match Set c.newer_version=True, c.idType=split(line.PathwayID,":")[0], c.name=line.PathwayName, c.id_type=split(line.PathwayID,':')[0];\n '''
    else:
        cypher_file_nodes.write('Create Constraint On (node:CTDpathway) Assert node.pathway_id Is Unique;\n')
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_pathways.csv" As line Create (c:CTDpathway{ pathway_id:split(line.PathwayID,':')[1], newer_version:True, name:line.PathwayName, id_type:split(line.PathwayID,':')[0]}) ;\n '''

    cypher_file_nodes.write(query)

    # add the chemical nodes to cypher file


# dictionary for genesymbol to gene id
dict_gene_symbol_to_gene_id = {}

'''
load ctd genes file and generate cypher file for the nodes with properties:
    0:GeneSymbol
    1:GeneName
    2:GeneID: NCBI-ID
    3:AltGeneIDs
    4:Synonyms
    5:BioGRIDIDs
    6:PharmGKBIDs
    7:UniProtIDs
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_gene_and_add_to_cypher_file():
    global counter_nodes_queries, cypher_file_nodes, node_file_number
    # say if in neo4j already ctd chemicals exists
    exists_ctd_gene_already_in_neo4j = False

    # check if chemicals are already in neo4j
    query = '''MATCH (n:CTDgene) RETURN n LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    number_of_genes = 0
    cypher_file_nodes.write('begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        query = ''' Match (c:CTDgene) Set c.old_version=True;\n '''
        cypher_file_nodes.write(query)
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes.csv" As line Merge (c:CTDgene{ gene_id:line.GeneID }) On Create Set c.altGeneIDs=split(line.AltGeneIDs,'|'), c.synonyms=split(line.Synonyms,'|'), c.bioGRIDIDs=split(line.BioGRIDIDs,'|'), c.pharmGKBIDs=split(line.PharmGKBIDs,'|'), c.uniProtIDs=split(line.UniProtIDs,'|'),  c.geneSymbol=line.GeneSymbol, c.name=line.GeneName On Match Set c.altGeneIDs=split(line.AltGeneIDs,'|'), c.synonyms=split(line.Synonyms,'|'), c.bioGRIDIDs=split(line.BioGRIDIDs,'|'), c.pharmGKBIDs=split(line.PharmGKBIDs,'|'), c.uniProtIDs=split(line.UniProtIDs,'|'),  c.geneSymbol=line.GeneSymbol, c.name=line.GeneName ;\n '''
    else:
        cypher_file_nodes.write('Create Constraint On (node:CTDgene) Assert node.gene_id Is Unique;\n')
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes.csv" As line Create (c:CTDgene{ gene_id:line.GeneID, altGeneIDs:split(line.AltGeneIDs,'|'), synonyms:split(line.Synonyms,'|'), bioGRIDIDs:split(line.BioGRIDIDs,'|'), pharmGKBIDs:split(line.PharmGKBIDs,'|'), uniProtIDs:split(line.UniProtIDs,'|'),  geneSymbol:line.GeneSymbol, name:line.GeneName}) ;\n '''

    cypher_file_nodes.write(query)

    ## add the chemical nodes to cypher file
    with open('ctd_data/CTD_genes.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:
            number_of_genes += 1
            gene_symbol = row[0]

            gene_id = row[2]

            dict_gene_symbol_to_gene_id[gene_symbol] = gene_id


# dictionary for GO with values 0:name,  1:ontology, 2:HighestGOLevel
dict_Go_properties = {}

'''
load ctd chemicals-go enriched file:
    0:ChemicalName
    1:ChemicalID
    2:CasRN
    3:Ontology
    4:GOTermName
    5:GOTermID
    6:HighestGOLevel
    7:PValue
    8:CorrectedPValue
    9:TargetMatchQty
    10:TargetTotalQty
    11:BackgroundMatchQty
    12:BackgroundTotalQty
and gather the information
'''


def load_chemical_go_enriched():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_go_enriched.csv" As line Merge (c:CTDchemical{ chemical_id:line.ChemicalID }) On Create Set  c.casRN=line.CasRN, c.name=line.ChemicalName, c.newer_version=True On Match Set c.newer_version=True;\n '''
    cypher_file_nodes.write(query)
    # check if chemicals are already in neo4j
    query = '''MATCH r=(c:CTDchemical)-[a:affects_CGO]->(n:CTDGO) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDchemical)-[a:affects_CGO]->(n:CTDGO) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_go_enriched.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDGO{ go_id:line.GOTermID }) Merge (c)-[a:affects_CGO]->(g) On Create Set a.unbiased=True, a.pValue=line.PValue, a.correctedPValue=line.CorrectedPValue, a.targetMatchQty=line.TargetMatchQty, a.targetTotalQty=line.TargetTotalQty, a.backgroundMatchQty=line.BackgroundMatchQty, a.backgroundTotalQty=line.BackgroundTotalQty On Match Set a.unbiased=True, a.pValue=line.PValue, a.correctedPValue=line.CorrectedPValue, a.targetMatchQty=line.TargetMatchQty, a.targetTotalQty=line.TargetTotalQty, a.backgroundMatchQty=line.BackgroundMatchQty, a.backgroundTotalQty=line.BackgroundTotalQty;\n '''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_go_enriched.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDGO{ go_id:line.GOTermID }) Create (c)-[a:affects_CGO{unbiased:True, pValue:line.PValue, correctedPValue:line.CorrectedPValue, targetMatchQty:line.TargetMatchQty, targetTotalQty:line.TargetTotalQty, backgroundMatchQty:line.BackgroundMatchQty, backgroundTotalQty:line.BackgroundTotalQty}]->(g);\n '''

    cypher_file_edges.write(query)

    dict_counter_go={}

    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_chem_go_enriched.csv') as csvfile:
        reader = csv.reader(csvfile,  quotechar='"')
        i = 0
        for row in reader:

            if i > 0:
                ontology = row[3]
                goTermName = row[4]
                goTermId = row[5]
                highestGOLevel = row[6]
                # if ontology in ['Molecular Function','Biological Process','Cellular Component']:
                if ontology in dict_counter_go:
                    dict_counter_go[ontology]+=1
                else:
                    dict_counter_go[ontology] = 1

                if not goTermId in dict_Go_properties:
                    dict_Go_properties[goTermId] = [goTermName, ontology, highestGOLevel]

            i += 1

    print(len(dict_Go_properties))
    print(dict_counter_go)
    result=sum(dict_counter_go[x] for x in dict_counter_go.keys())
    print(result)

    # sys.exit()

'''
load ctd chemicals-go enriched file:
    0:chemicalname											
    1:chemicalid
    2:casrn
    3:phenotypename
    4:phenotypeid
    5:comentionedterms
    6:organism
    7:organismid
    8:interaction
    9:interactionactions
    10:anatomyterms
    11:inferencegenesymbols
    12:pubmedids
and gather the information
'''


def load_chemical_phenotype():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_pheno_term_ixns.csv" As line Merge (c:CTDchemical{ chemical_id:line.ChemicalID }) On Create Set  c.casRN=line.CasRN, c.name=line.ChemicalName, c.newer_version=True On Match Set c.newer_version=True;\n '''
    cypher_file_nodes.write(query)
    # check if chemicals are already in neo4j
    query = '''MATCH r=(c:CTDchemical)-[a:phenotype]->(n:CTDGO) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDchemical)-[a:phenotype]->(n:CTDGO) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_pheno_term_ixns.csv" As line Match (c:CTDchemical{ chemical_id:line.chemicalid }), (g:CTDGO{ go_id:line.phenotypeid }) Where line.organismid='9606' Merge (c)-[a:phenotype]->(g) On Create Set a.organismid=line.organismid, a.unbiased=True, a.comentionedterms=line.comentionedterms, a.interaction=line.interaction, a.interactionactions=line.interactionactions, a.anatomyterms=line.anatomyterms, a.inferencegenesymbols=line.inferencegenesymbols, a.pubmedids=line.pubmedids On Match Set a.organismid=line.organismid, a.unbiased=True, a.comentionedterms=line.comentionedterms, a.interaction=line.interaction, a.interactionactions=line.interactionactions, a.anatomyterms=line.anatomyterms, a.inferencegenesymbols=line.inferencegenesymbols, a.pubmedids=line.pubmedids;\n '''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_pheno_term_ixns.csv" As line Match (c:CTDchemical{ chemical_id:line.chemicalid }), (g:CTDGO{ go_id:line.phenotypeid }) Where line.organismid='9606' Create (c)-[a:phenotype{unbiased:True, organismid:line.organismid, comentionedterms:line.comentionedterms, interaction:line.interaction, interactionactions:line.interactionactions, anatomyterms:line.anatomyterms, pubmedids:line.pubmedids, inferencegenesymbols:line.inferencegenesymbols}]->(g);\n '''

    cypher_file_edges.write(query)

    dict_counter_go={}

    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_pheno_term_ixns.csv') as csvfile:
        reader = csv.reader(csvfile,  quotechar='"')
        i = 0
        for row in reader:

            if i > 0:
                ontology = ''
                goTermName = row[3]
                goTermId = row[4]
                organism_id=row[7]
                if organism_id!='9606':
                    continue
                # if ontology in ['Molecular Function','Biological Process','Cellular Component']:
                if ontology in dict_counter_go:
                    dict_counter_go[ontology]+=1
                else:
                    dict_counter_go[ontology] = 1

                if not goTermId in dict_Go_properties:
                    dict_Go_properties[goTermId] = [goTermName, ontology,'']

            i += 1

    print(len(dict_Go_properties))
    print(dict_counter_go)
    result=sum(dict_counter_go[x] for x in dict_counter_go.keys())
    print(result)


# dictionary with (disease_id, go_id) and properties as value inferenceGeneSymbol, inference GeneQty
dict_disease_go = {}

# list of gene-go pairs
dict_gene_go = {}

'''
gather information from disease-go inference
load ctd disease-go enriched files for biological process, molecular function and cellular componenet
    0:DiseaseName
    1:DiseaseID
    2:GOName
    3:GOID
    4:InferenceGeneQty
    5:InferenceGeneSymbols
'''


def gather_information_from_disease_go_inferencen(file, ontology):
    # check if chemicals are already in neo4j
    query = '''MATCH r=(c:CTDdisease)-[a:affects_DGO]->(n:CTDGO) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin\n')
        query = ''' Match (c:CTDdisease)-[a:affects_DGO]->(n:CTDGO) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/''' + file + '''" As line Match (d:CTDdisease{ disease_id:line.DiseaseID}), (g:CTDGO{ go_id:line.GOID }) Merge (d)-[a:affects_DGO]->(g) On Create Set a.unbiased=True, a.inferenceGeneSymbols=line.InferenceGeneSymbols, a.inferenceGeneQty=line.InferenceGeneQty On Match Set a.unbiased=True, a.inferenceGeneSymbols=line.InferenceGeneSymbols, a.inferenceGeneQty=line.InferenceGeneQty;\n '''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/''' + file + '''" As line Match (d:CTDdisease{ disease_id:line.DiseaseID}), (g:CTDGO{ go_id:line.GOID }) Create (d)-[a:affects_DGO{unbiased:True, inferenceGeneSymbols:line.InferenceGeneSymbols, inferenceGeneQty:line.InferenceGeneQty}]->(g);\n'''

    cypher_file_edges.write(query)

    with open('ctd_data/' + file) as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:

            if i > 0:
                disease_id = row[1]
                goName = row[2]
                goId = row[3]
                inferenceGeneQty = row[4]
                inferenceGeneSymbols = row[5].split('|')

                if not goId in dict_Go_properties:
                    dict_Go_properties[goId] = [goName, ontology, '']

                dict_disease_go[(disease_id, goId)] = [inferenceGeneSymbols, inferenceGeneQty]

                for gene_symbol in inferenceGeneSymbols:
                    gene_id = dict_gene_symbol_to_gene_id[gene_symbol]
                    if (gene_id, goId) not in dict_gene_go:
                        dict_gene_go[(gene_id, goId)] = [gene_symbol]
                if i % 20000 == 0:
                    print(i)

            i += 1

    print('number of gene-go pairs:' + str(len(dict_gene_go)))
    print('number of disease-go pairs:' + str(len(dict_disease_go)))


'''
gather information from phenotyp disease-go inference

    0:GOName
    1:GOID (GO identifer)
    2:DiseaseName
    3:DiseaseID (MeSH or OMIM identifier)
    4:InferenceChemicalQty
    5:InferenceChemicalNames ('|' delimited list)
    6:InferenceGeneQty
    7:InferenceGeneSymbols ('|' delimited list)

'''


def gather_information_from_disease_phenotyp_go_inference(file, ontology):
    # check if chemicals are already in neo4j
    query = '''MATCH r=(c:CTDdisease)-[a:affects_DGO]->(n:CTDGO) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDdisease)-[a:affects_DGO]->(n:CTDGO) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/''' + file + '''" As line Match (d:CTDdisease{ disease_id:split(line.DiseaseID,':')[1]}), (g:CTDGO{ go_id:line.GOID }) Merge (d)-[a:affects_DGO]->(g) On Create Set a.unbiased=True, a.inferenceGeneSymbols=line.InferenceGeneSymbols, a.inferenceGeneQty=line.InferenceGeneQty On Match Set a.unbiased=True, a.inferenceGeneSymbols=line.InferenceGeneSymbols, a.inferenceGeneQty=line.InferenceGeneQty;\n '''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/''' + file + '''" As line Match (d:CTDdisease{ disease_id:split(line.DiseaseID,':')[1]}), (g:CTDGO{ go_id:line.GOID }) Create (d)-[a:affects_DGO{unbiased:True, inferenceGeneSymbols:line.InferenceGeneSymbols, inferenceGeneQty:line.InferenceGeneQty}]->(g);\n'''

    cypher_file_edges.write(query)

    with open('ctd_data/' + file) as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:

            if i > 0:
                disease_id = row[3]
                goName = row[0]
                goId = row[1]
                inferenceGeneQty = row[6]
                inferenceGeneSymbols = row[7].split('|')
                inferenceChemicalQty = row[4]
                inferenceChemicalNames = row[5].split('|')

                if not goId in dict_Go_properties:
                    dict_Go_properties[goId] = [goName, ontology, '']

                dict_disease_go[(disease_id, goId)] = [inferenceGeneSymbols, inferenceGeneQty,inferenceChemicalNames,inferenceChemicalQty]

                for gene_symbol in inferenceGeneSymbols:
                    if gene_symbol=='':
                        continue
                    # if all thing should be integrated this should not be happening
                    if gene_symbol not in dict_gene_symbol_to_gene_id:
                        print('should not happend gene_symbol not in ctd gene')
                        continue
                    gene_id = dict_gene_symbol_to_gene_id[gene_symbol]
                    if (gene_id, goId) not in dict_gene_go:
                        dict_gene_go[(gene_id, goId)] = [gene_symbol]
                if i % 20000 == 0:
                    print(i)

            i += 1

    print('number of gene-go pairs:' + str(len(dict_gene_go)))
    print('number of disease-go pairs:' + str(len(dict_disease_go)))

'''

gather the information from  the different go files to get all go information
'''


def load_disease_go_inference(file_d_cc, file_d_mf, file_d_bp, old):
    if old:
        print('start Cellular Component')
        print(datetime.datetime.utcnow())
        gather_information_from_disease_go_inferencen(file_d_cc,
                                                      'Cellular Component')
        print('start Molecular Function')
        print(datetime.datetime.utcnow())
        gather_information_from_disease_go_inferencen(file_d_mf,
                                                      'Molecular Function')
        print('start Biological Process')
        print(datetime.datetime.utcnow())
        gather_information_from_disease_go_inferencen(file_d_bp,
                                                      'Biological Process')
    else:

        print('start Cellular Component')
        print(datetime.datetime.utcnow())
        gather_information_from_disease_phenotyp_go_inference(file_d_cc,
                                                      'Cellular Component')
        print('start Molecular Function')
        print(datetime.datetime.utcnow())
        gather_information_from_disease_phenotyp_go_inference(file_d_mf,
                                                      'Molecular Function')
        print('start Biological Process')
        print(datetime.datetime.utcnow())
        gather_information_from_disease_phenotyp_go_inference(file_d_bp,
                                                      'Biological Process')
    print(len(dict_Go_properties))


'''
Add GO to the node cypher file
'''


def add_go_to_cypher_file():
    global counter_nodes_queries, cypher_file_nodes, node_file_number
    # say if in neo4j already ctd chemicals exists
    exists_ctd_go_already_in_neo4j = False

    # check if chemicals are already in neo4j
    query = '''MATCH (n:CTDGO) RETURN n LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    cypher_file_nodes.write('begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created
    if not result is None:
        query = ''' Match (c:CTDGO) Set c.old_version=True;\n '''
        cypher_file_nodes.write(query)
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_GO.csv" As line Merge (c:CTDGO{ go_id:line.GOID }) On Create Set c.ontology=line.Ontology, c.highestGOLevel=line.HighestGOLevel, c.name=line.GOName On Match Set c.ontology=line.Ontology, c.highestGOLevel=line.HighestGOLevel, c.name=line.GOName;\n '''
    else:
        cypher_file_nodes.write('Create Constraint On (node:CTDGO) Assert node.go_id Is Unique;\n')
        cypher_file_nodes.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_GO.csv" As line Create (c:CTDGO{ go_id:line.GOID, ontology:line.Ontology, highestGOLevel:line.HighestGOLevel, name:line.GOName});\n'''

    cypher_file_nodes.write(query)

    with open('ctd_data/CTD_GO.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GOID', 'GOName', 'Ontology', 'HighestGOLevel'])
        # add the go nodes to cypher file
        for go_id, [name, ontology, highestGOLevel] in dict_Go_properties.items():
            writer.writerow([go_id, name, ontology, highestGOLevel])


'''
add gene-go relationship to cypher file
'''


def gene_go_into_cypher_file():
    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDgene)-[a:associates_GGO]->(n:CTDGO) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDgene)-[a:associates_GGO]->(n:CTDGO) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_Gene_GO.csv" As line Match (c:CTDgene{ gene_id:line.GeneID }), (g:CTDGO{ go_id:line.GOID }) Merge (c)-[a:associates_GGO{unbiases:False}]->(g) ;\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_Gene_GO.csv" As line Match (c:CTDgene{ gene_id:line.GeneID }), (g:CTDGO{ go_id:line.GOID }) Create (c)-[a:associates_GGO{unbiases:False}]->(g) ;\n'''

    cypher_file_edges.write(query)

    with open('ctd_data/CTD_Gene_GO.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GeneID', 'GOID', 'GeneSymbol'])
        # add the go nodes to cypher file
        for (gene_id, go_id), genesymbol in dict_gene_go.items():
            writer.writerow([gene_id, go_id, genesymbol])


'''
load ctd gene-pathway file:
    0:GeneSymbol
    1:GeneID
    2:PathwayName
    3:PathwayID
and gather the information
'''


def load_gene_pathway():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_pathways.csv" As line Merge (c:CTDgene{ gene_id:line.GeneID }) On Create Set  c.geneSymbol=line.GeneSymbol, c.newer_version=True ;\n'''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_pathways.csv" As line Merge (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] }) On Create Set g.name=line.PathwayName, g.newer_version=True ;\n'''
    cypher_file_nodes.write(query)

    global counter_edges_queries, cypher_file_edges, edges_file_number

    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDgene)-[:participates_GP]->(n:CTDpathway) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDgene)-[a:participates_GP]->(n:CTDpathway) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_pathways.csv" As line Match (c:CTDgene{ gene_id:line.GeneID }), (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] }) Merge (c)-[a:participates_GP{unbiases:False}]->(g) ;\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_pathways.csv" As line Match (c:CTDgene{ gene_id:line.GeneID }), (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] }) Create (c)-[a:participates_GP{unbiases:False}]->(g) ;\n'''

    cypher_file_edges.write(query)


'''
load ctd gene-pathway file:
    0:DiseaseName
    1:DiseaseID
    2:PathwayName
    3:PathwayID
    4:InferenceGeneSymbol
and gather the information
'''


def load_disease_pathway():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_diseases_pathways.csv" As line Merge (c:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }) On Create Set  c.name=line.DiseaseName, c.newer_version=True;\n'''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_diseases_pathways.csv" As line Merge  (g:CTDpathway{ pathway_id:line.PathwayID })  On Create Set g.name=line.PathwayName, g.newer_version=True;\n'''
    cypher_file_nodes.write(query)
    global counter_edges_queries, cypher_file_edges, edges_file_number

    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDdisease)-[:associates_DP]->(n:CTDpathway) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDdisease)-[a:associates_DP]->(n:CTDpathway) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_diseases_pathways.csv" As line Match (c:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }), (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] })  Merge (c)-[a:associates_DP]->(g) On Match Set a.inferenceGeneSymbol=line.InferenceGeneSymbol On Create Set a.inferenceGeneSymbol=line.InferenceGeneSymbol;\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_diseases_pathways.csv" As line Match (c:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }), (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] })  Create (c)-[:associates_DP{inferenceGeneSymbol:line.InferenceGeneSymbol}]->(g);\n'''

    cypher_file_edges.write(query)


'''
load ctd gene-pathway file:
    0:ChemicalName                        
    1:ChemicalID
    2:CasRN
    3:GeneSymbol
    4:GeneID
    5:GeneForms
    6:Organism
    7:OrganismID
    8:Interaction
    9:InteractionActions: action_degree^type
    action_degree = increases/decreases/affects
    10:PubMedIDs
and gather the information
'''


def load_chemical_gene():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_gene_ixns.csv" As line Merge (c:CTDchemical{ chemical_id:line.ChemicalID }) On Create Set c.casRN=line.CasRN, c.name=line.ChemicalName, c.newer_version=True On Match Set c.newer_version=True;\n'''
    cypher_file_nodes.write(query)

    global counter_edges_queries, cypher_file_edges, edges_file_number

    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDchemical)-[:associates_CG]->(n:CTDgene) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDchemical)-[a:associates_CG]->(n:CTDgene) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_gene_ixns.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDgene{ gene_id:line.GeneID }) Merge (c)-[a:associates_CG]->(g) On Create Set a.unbiased=False, a.gene_forms=split(line.GeneForms,'|'), a.organism=line.Organism, a.organism_id=line.OrganismID, a.interaction_text=line.Interaction, a.interactions_actions=split(line.InteractionActions,'|'), a.pubMedIds=split(line.PubMedIDs,'|') On Match Set a.unbiased=False, a.gene_forms=split(line.GeneForms,'|'), a.organism=line.Organism, a.organism_id=line.OrganismID, a.interaction_text=line.Interaction, a.interactions_actions=split(line.InteractionActions,'|'), a.pubMedIds=split(line.PubMedIDs,'|');\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_gene_ixns.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDgene{ gene_id:line.GeneID }) Create (c)-[:associates_CG{unbiased:False, gene_forms:split(line.GeneForms,'|'), organism:line.Organism, organism_id:line.OrganismID, interaction_text:line.Interaction, interactions_actions:split(line.InteractionActions,'|'), pubMedIds:split(line.PubMedIDs,'|') }]->(g);\n'''

    cypher_file_edges.write(query)


# ChemicalName	ChemicalID	CasRN	PathwayName	PathwayID	PValue	CorrectedPValue	TargetMatchQty	TargetTotalQty	BackgroundMatchQty	BackgroundTotalQty

'''
load ctd chemical-pathway file:
    0:ChemicalName                        
    1:ChemicalID
    2:CasRN
    3:PathwayName
    4:PathwayID
    5:PValue
    6:CorrectedPValue
    7:TargetMatchQty
    8:TargetTotalQty
    9:BackgroundMatchQty
    10:BackgroundTotalQty
and gather the information
'''


def load_chemical_pathway_enriched():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_pathways_enriched.csv" As line Merge (c:CTDchemical{ chemical_id:line.ChemicalID }) On Create Set c.casRN=line.CasRN, c.name=line.ChemicalName, c.newer_version=True On Match Set c.newer_version=True;\n'''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_pathways_enriched.csv" As line Merge (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] }) On Create Set g.name=line.PathwayName, g.newer_version=True;\n'''
    cypher_file_nodes.write(query)

    global counter_edges_queries, cypher_file_edges, edges_file_number

    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDchemical)-[:associates_CP]->(n:CTDpathway) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDchemical)-[a:associates_CP]->(n:CTDpathway) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_pathways_enriched.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1] }) Merge (c)-[a:associates_CP]->(g) On Create Set a.unbiased=True, a.pValue=line.PValue, a.correctedPValue=line.CorrectedPValue, a.targetMatchQty=line.TargetMatchQty, a.targetTotalQty=line.TargetTotalQty, a.backgroundMatchQty=line.BackgroundMatchQty, a.backgroundTotalQty=line.BackgroundTotalQty On Match Set a.unbiased=True, a.pValue=line.PValue, a.correctedPValue=line.CorrectedPValue, a.targetMatchQty=line.TargetMatchQty, a.targetTotalQty=line.TargetTotalQty, a.backgroundMatchQty=line.BackgroundMatchQty, a.backgroundTotalQty=line.BackgroundTotalQty;\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chem_pathways_enriched.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDpathway{ pathway_id:split(line.PathwayID,':')[1]}) Create (c)-[:associates_CP{unbiased:True, pValue:line.PValue, correctedPValue:line.CorrectedPValue, targetMatchQty:line.TargetMatchQty, targetTotalQty:line.TargetTotalQty, backgroundMatchQty:line.BackgroundMatchQty, backgroundTotalQty:line.BackgroundTotalQty }]->(g);\n'''

    cypher_file_edges.write(query)


'''
load ctd chemical-disease file:
    0:ChemicalName                   
    1:ChemicalID
    2:CasRN
    3:DiseaseName
    4:DiseaseID
    5:DirectEvidence
    6:InferenceGeneSymbol
    7:InferenceScore
    8:OmimIDs
    9:PubMedIDs
and gather the information
'''


def load_chemical_disease():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chemicals_diseases.csv" As line Merge (c:CTDchemical{ chemical_id:line.ChemicalID }) On Create  Set  c.casRN=line.CasRN, c.name=line.ChemicalName, c.newer_version=True On Match Set c.newer_version=True;\n'''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chemicals_diseases.csv" As line Merge (g:CTDdisease{ disease_id:split(line.DiseaseID,':')[1]}) On Create Set  g.name=line.DiseaseName, g.newer_version=True;\n'''
    cypher_file_nodes.write(query)

    global counter_edges_queries, cypher_file_edges, edges_file_number

    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDchemical)-[:associates_CD]->(n:CTDdisease) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDchemical)-[a:associates_CD]->(n:CTDdisease) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chemicals_diseases.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDdisease{ disease_id:split(line.DiseaseID,':')[1]}) Merge (c)-[a:associates_CD ]->(g) On Create Set a.directEvidence=line.DirectEvidence, a.inferenceGeneSymbol=line.InferenceGeneSymbol, a.inferenceScore=line.InferenceScore, a.omimIDs=split(line.OmimIDs,'|'), a.pubMedIDs=split(line.PubMedIDs,'|') On Match Set a.directEvidence=line.DirectEvidence, a.inferenceGeneSymbol=line.InferenceGeneSymbol, a.inferenceScore=line.InferenceScore, a.omimIDs=split(line.OmimIDs,'|'), a.pubMedIDs=split(line.PubMedIDs,'|') ;\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_chemicals_diseases.csv" As line Match (c:CTDchemical{ chemical_id:line.ChemicalID }), (g:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }) Create (c)-[:associates_CD{ directEvidence:line.DirectEvidence, inferenceGeneSymbol:line.InferenceGeneSymbol, inferenceScore:line.InferenceScore, omimIDs:split(line.OmimIDs,'|'), pubMedIDs:split(line.PubMedIDs,'|') }]->(g);\n'''

    cypher_file_edges.write(query)


'''
load ctd gene-disease file:
    0:GeneSymbol
    1:GeneID
    2:DiseaseName
    3:DiseaseID
    4:DirectEvidence
    5:InferenceChemicalName
    6:InferenceScore
    7:OmimIDs
    8:PubMedIDs
and gather the information
'''


def load_gene_disease():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_diseases.csv" As line Merge (g:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }) On Create Set g.name=line.DiseaseName, g.newer_version=True;\n'''
    cypher_file_nodes.write(query)

    global counter_edges_queries, cypher_file_edges, edges_file_number

    # check if this association already exists in neo4j
    relationship_exists = False
    query = '''MATCH r=(c:CTDgene)-[:associates_GD]->(n:CTDdisease) RETURN r LIMIT 1 '''
    results = g.run(query)
    result = results.evaluate()
    # depending if the relationship are in neo4j or not the relationships need to be merged or created
    if not result is None:
        cypher_file_edges.write('begin')
        query = ''' Match (c:CTDgene)-[a:associates_GD]->(n:CTDdisease) Set a.old_version=True;\n '''
        cypher_file_edges.write(query)
        cypher_file_edges.write('commit\n')
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_diseases.csv" As line Match (c:CTDgene{ gene_id:line.GeneID }), (g:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }) Merge (c)-[a:associates_GD ]->(g) On Create Set a.directEvidence=line.DirectEvidence, a.inferenceChemicalName=line.InferenceChemicalName, a.inferenceScore=line.InferenceScore, a.omimIDs=split(line.OmimIDs,'|'), a.pubMedIDs=split(line.PubMedIDs,'|') On Match Set a.directEvidence=line.DirectEvidence, a.inferenceChemicalName=line.InferenceChemicalName, a.inferenceScore=line.InferenceScore, a.omimIDs=split(line.OmimIDs,'|'), a.pubMedIDs=split(line.PubMedIDs,'|');\n'''
    else:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/import_into_Neo4j/ctd/ctd_data/CTD_genes_diseases.csv" As line Match (c:CTDgene{ gene_id:line.GeneID }), (g:CTDdisease{ disease_id:split(line.DiseaseID,':')[1] }) Create (c)-[:associates_GD{ directEvidence:line.DirectEvidence, inferenceChemicalName:line.InferenceChemicalName, inferenceScore:line.InferenceScore, omimIDs:split(line.OmimIDs,'|'), pubMedIDs:split(line.PubMedIDs,'|') }]->(g);\n'''

    cypher_file_edges.write(query)

# delete node file
delet_node_file=open('cypher/nodes_delete.cypher','w')

'''
ad node deleter for all nodes which have no relationship to other nodes
'''
def delete_nodes_with_no_relationship(label):
    delet_node_file.write('begin\n')
    query='''MATCH (n:%s) Where not (n)--() Delete n;\n'''
    query=query %(label)
    delet_node_file.write(query)
    delet_node_file.write('commit\n')


def main():
    print(datetime.datetime.utcnow())

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('connection to db')
    database_connection()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd chemical and add to cypher file')

    load_chemicals_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd disease and add to cypher file')

    load_disease_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd pathway and add to cypher file')

    load_pathway_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd gene and add to cypher file')

    load_gene_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd chemical-go and gather the information')

    load_chemical_go_enriched()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd chemical-phenotype and gather the information')

    load_chemical_phenotype()


    # print('##########################################################################')
    #
    # print(datetime.datetime.utcnow())
    # print('load in ctd disease-go and gather the information')
    #
    # load_disease_go_inference('CTD_Disease-GO_cellular_component_associations.csv','CTD_Disease-GO_molecular_function_associations.csv','CTD_Disease-GO_biological_process_associations.csv',True)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('load in ctd phenotype disease-go and gather the information')

    load_disease_go_inference('CTD_Phenotype-Disease_cellular_component_associations.csv','CTD_Phenotype-Disease_molecular_function_associations.csv','CTD_Phenotype-Disease_biological_process_associations.csv', False)

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add go to node cypher file')

    add_go_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add gene-go relationship to cypher file')

    gene_go_into_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add gene-pathway relationship to cypher file')

    load_gene_pathway()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add disease-pathway relationship to cypher file')

    load_disease_pathway()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add chemical-gene relationship to cypher file')

    load_chemical_gene()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add chemical-pathway relationship to cypher file')

    load_chemical_pathway_enriched()

    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add chemical-disease relationship to cypher file')

    load_chemical_disease()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('add chemical-disease relationship to cypher file')

    load_gene_disease()


    print('##########################################################################')

    print(datetime.datetime.utcnow())
    print('delete nodes with no realtionships')

    delete_nodes_with_no_relationship('CTDGO')
    delete_nodes_with_no_relationship('CTDchemical')
    delete_nodes_with_no_relationship('CTDdisease')
    delete_nodes_with_no_relationship('CTDgene')
    delete_nodes_with_no_relationship('CTDpathway')

    # delete old chemical nodes which are not in ctd anymore
    query='''Match (n:CTDchemical) Where n.old_version=True and n.newer_version=False Detach Delete n;\n'''
    delet_node_file.write(query)

    print('##########################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
