import sys
import datetime
import csv

# node cypher file number
node_file_number = 1

# edges cypher file number
edges_file_number = 1

# cypher file for all nodes
cypher_file_nodes = open('cypher/nodes_' + str(node_file_number) + '.cypher', 'w')

# cypher file for all relationships
cypher_file_edges = open('cypher/edges_' + str(edges_file_number) + '.cypher', 'w')

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
    # 8:DrugBankID is excluded
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_chemicals_and_add_to_cypher_file():
    # say if in neo4j already ctd chemicals exists
    cypher_file_nodes.write(':begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created

    cypher_file_nodes.write('Create Constraint On (node:CTD_chemical) Assert node.chemical_id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chemicals.tsv" As line FIELDTERMINATOR '\\t' Create (c:CTD_chemical{ chemical_id:split(line.ChemicalID,':')[1] , casRN:line.CasRN, synonyms:split(line.Synonyms,'|'),  parentIDs:split(line.ParentIDs,'|'), parentTreeNumbers:split(line.ParentTreeNumbers,'|'), treeNumbers:split(line.TreeNumbers,'|'), definition:line.Definition, name:line.ChemicalName, url:"http://ctdbase.org/detail.go?type=chem&acc="+ split(line.ChemicalID,':')[1]});\n '''

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

    cypher_file_nodes.write(':begin\n')

    cypher_file_nodes.write('Create Constraint On (node:CTD_disease) Assert node.disease_id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_diseases.tsv" As line FIELDTERMINATOR '\\t' Create (c:CTD_disease{ disease_id:split(line.DiseaseID,':')[1], altDiseaseIDs:split(line.AltDiseaseIDs,"|"), idType:split(line.DiseaseID,':')[0] , synonyms:split(line.Synonyms,'|'), slimMappings:split(line.SlimMappings,'|'), parentIDs:split(line.ParentIDs,'|'), parentTreeNumbers:split(line.ParentTreeNumbers,'|'), treeNumbers:split(line.TreeNumbers,'|'), definition:line.Definition, name:line.DiseaseName, url:"http://ctdbase.org/detail.go?type=disease&acc="+ split(line.DiseaseID,':')[1]}) ;\n '''

    cypher_file_nodes.write(query)


'''
load ctd pathway file and generate cypher file for the nodes with properties:
    0:PathwayName
    1:PathwayID
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_pathway_and_add_to_cypher_file():

    cypher_file_nodes.write(':begin\n')
    cypher_file_nodes.write('Create Constraint On (node:CTD_pathway) Assert node.pathway_id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_pathways.tsv" As line FIELDTERMINATOR '\\t' Create (c:CTD_pathway{ pathway_id:split(line.PathwayID,':')[1], name:line.PathwayName, id_type:split(line.PathwayID,':')[0], url:" http://ctdbase.org/detail.go?type=pathway&acc="+split(line.PathwayID,':')[1]}) ;\n '''

    cypher_file_nodes.write(query)


'''
load ctd pathway file and generate cypher file for the nodes with properties:
    0:AnatomyName
    1:AnatomyID (MeSH identifier)
    2:Definition
    3:AltAnatomyIDs (alternative identifiers; '|'-delimited list)
    4:ParentIDs (identifiers of the parent terms; '|'-delimited list)
    5:TreeNumbers (identifiers of the anatomical term's nodes; '|'-delimited list)
    6:ParentTreeNumbers (identifiers of the parent nodes; '|'-delimited list)
    7:Synonyms ('|'-delimited list)
    8:ExternalSynonyms ('|'-delimited list)

furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_anatomy_and_add_to_cypher_file():

    cypher_file_nodes.write(':begin\n')
    cypher_file_nodes.write('Create Constraint On (node:CTD_anatomy) Assert node.anatomy_id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_anatomy.tsv" As line FIELDTERMINATOR '\\t' Create (c:CTD_anatomy{ anatomy_id:split(line.AnatomyID,':')[1], name:line.AnatomyName, id_type:split(line.AnatomyID,':')[0], definition:line.Definition,  alternative_ids:split(line.AltAnatomyIDs,'|'), parent_id:split(line.ParentIDs,'|'), tree_numbers:split(line.TreeNumbers,'|'), parent_tree_numbers:split(line.ParentTreeNumbers,'|'), synonyms:split(line.Synonyms,'|'), externamSynonyms:split(line.ExternalSynonyms,'|'), url:"http://ctdbase.org/detail.go?type=anatomy&acc="+split(line.AnatomyID,':')[1] }) ;\n '''

    cypher_file_nodes.write(query)


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
    # say if in neo4j already ctd chemicals exists
    exists_ctd_gene_already_in_neo4j = False

    number_of_genes = 0
    cypher_file_nodes.write(':begin\n')
    cypher_file_nodes.write('Create Constraint On (node:CTD_gene) Assert node.gene_id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_genes.tsv" As line FIELDTERMINATOR '\\t' Create (c:CTD_gene{ gene_id:line.GeneID, altGeneIDs:split(line.AltGeneIDs,'|'), synonyms:split(line.Synonyms,'|'), bioGRIDIDs:split(line.BioGRIDIDs,'|'), pharmGKBIDs:split(line.PharmGKBIDs,'|'), uniProtIDs:split(line.UniProtIDs,'|'),  geneSymbol:line.GeneSymbol, name:line.GeneName, url:" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID}) ;\n '''

    cypher_file_nodes.write(query)

    ## add the chemical nodes to cypher file
    with open(path_of_ctd_data + '/ctd_data/CTD_genes.tsv') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
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

    if not reduced:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_go_enriched.tsv" As line FIELDTERMINATOR '\\t' Merge (c:CTD_chemical{ chemical_id:line.ChemicalID }) On Create Set  c.casRN=line.CasRN, c.name=line.ChemicalName;\n '''
        cypher_file_nodes.write(query)

        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_go_enriched.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_chemical{ chemical_id:line.ChemicalID }), (g:CTD_GO{ go_id:line.GOTermID }) Create (c)-[a:affects_CGO{unbiased:True, pValue:line.PValue, correctedPValue:line.CorrectedPValue, targetMatchQty:line.TargetMatchQty, targetTotalQty:line.TargetTotalQty, backgroundMatchQty:line.BackgroundMatchQty, backgroundTotalQty:line.BackgroundTotalQty, url:"http://ctdbase.org/detail.go?type=chem&acc="+line.ChemicalID}]->(g);\n '''

        cypher_file_edges.write(query)

    dict_counter_go = {}

    # gather information from CTD chemical-go enriched
    with open(path_of_ctd_data + '/ctd_data/CTD_chem_go_enriched.tsv') as tsvfile:
        reader = csv.reader(tsvfile, quotechar='"', delimiter='\t')
        i = 0
        for row in reader:

            if i > 0:
                ontology = row[3]
                goTermName = row[4]
                goTermId = row[5]
                highestGOLevel = row[6]
                # if ontology in ['Molecular Function','Biological Process','Cellular Component']:
                if ontology in dict_counter_go:
                    dict_counter_go[ontology] += 1
                else:
                    dict_counter_go[ontology] = 1

                if not goTermId in dict_Go_properties:
                    dict_Go_properties[goTermId] = [goTermName, ontology, highestGOLevel]

            i += 1

    print(len(dict_Go_properties))
    print(dict_counter_go)
    result = sum(dict_counter_go[x] for x in dict_counter_go.keys())
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
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_pheno_term_ixns.tsv" As line FIELDTERMINATOR '\\t' Merge (c:CTD_chemical{ chemical_id:line.chemicalid }) On Create Set  c.casRN=line.casrn, c.name=line.chemicalname;\n '''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_pheno_term_ixns.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_chemical{ chemical_id:line.chemicalid }), (g:CTD_GO{ go_id:line.phenotypeid }) Create (c)-[a:phenotype{unbiased:True, organismid:line.organismid, comentionedterms:split(line.comentionedterms,'|'), interaction:line.interaction, interactionactions:split(line.interactionactions,'|'), anatomyterms:split(line.anatomyterms,'|'), pubMed_ids:split(line.pubmedids,'|'), inferencegenesymbols:split(line.inferencegenesymbols,'|'), url:"http://ctdbase.org/detail.go?type=chem&acc="+line.chemicalid}]->(g);\n '''

    cypher_file_edges.write(query)

    dict_counter_go = {}

    # gather information from CTD chemical-go enriched
    with open(path_of_ctd_data + '/ctd_data/CTD_pheno_term_ixns.tsv') as tsvfile:
        reader = csv.reader(tsvfile, quotechar='"', delimiter='\t')
        i = 0
        for row in reader:

            if i > 0:
                if row[1] == 'C023505':
                    print('ok')
                ontology = ''
                goTermName = row[3]
                goTermId = row[4]
                organism_id = row[7]
                # if organism_id!='9606':
                #     continue
                # if ontology in ['Molecular Function','Biological Process','Cellular Component']:
                if ontology in dict_counter_go:
                    dict_counter_go[ontology] += 1
                else:
                    dict_counter_go[ontology] = 1

                if not goTermId in dict_Go_properties:
                    dict_Go_properties[goTermId] = [goTermName, ontology, '']

            i += 1

    print(len(dict_Go_properties))
    print(dict_counter_go)
    result = sum(dict_counter_go[x] for x in dict_counter_go.keys())
    print(result)


# dictionary with (disease_id, go_id) and properties as value inferenceGeneSymbol, inference GeneQty
dict_disease_go = {}

# list of gene-go pairs
dict_gene_go = {}

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
    if not reduced:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/''' + file + '''" As line FIELDTERMINATOR '\\t' Match (d:CTD_disease{ disease_id:split(line.DiseaseID,':')[1]}), (g:CTD_GO{ go_id:line.GOID }) Create (d)-[a:affects_DGO{unbiased:True, inferenceGeneSymbols:line.InferenceGeneSymbols, inferenceGeneQty:line.InferenceGeneQty, url:"http://ctdbase.org/detail.go?type=disease&acc="+split(line.DiseaseID,':')[1]}]->(g);\n'''

        cypher_file_edges.write(query)

    with open(path_of_ctd_data + '/ctd_data/' + file) as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
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

                dict_disease_go[(disease_id, goId)] = [inferenceGeneSymbols, inferenceGeneQty, inferenceChemicalNames,
                                                       inferenceChemicalQty]

                for gene_symbol in inferenceGeneSymbols:
                    if gene_symbol == '':
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


def load_disease_go_inference(file_d_cc, file_d_mf, file_d_bp):
    print('start Cellular Component')
    print(datetime.datetime.now())
    gather_information_from_disease_phenotyp_go_inference(file_d_cc,
                                                          'Cellular Component')
    print('start Molecular Function')
    print(datetime.datetime.now())
    gather_information_from_disease_phenotyp_go_inference(file_d_mf,
                                                          'Molecular Function')
    print('start Biological Process')
    print(datetime.datetime.now())
    gather_information_from_disease_phenotyp_go_inference(file_d_bp,
                                                          'Biological Process')
    print(len(dict_Go_properties))


'''
Add GO to the node cypher file
'''


def add_go_to_cypher_file():

    cypher_file_nodes.write(':begin\n')
    cypher_file_nodes.write('Create Constraint On (node:CTD_GO) Assert node.go_id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_GO.tsv" As line FIELDTERMINATOR '\\t' Create (c:CTD_GO{ go_id:line.GOID, ontology:line.Ontology, highestGOLevel:line.HighestGOLevel, name:line.GOName, url:" http://ctdbase.org/detail.go?type=go&acc="+line.GOID});\n'''

    cypher_file_nodes.write(query)

    with open(path_of_ctd_data + '/ctd_data/CTD_GO.tsv', 'w') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['GOID', 'GOName', 'Ontology', 'HighestGOLevel'])
        # add the go nodes to cypher file
        for go_id, [name, ontology, highestGOLevel] in dict_Go_properties.items():
            writer.writerow([go_id, name, ontology, highestGOLevel])


'''
add gene-go relationship to cypher file
'''


def gene_go_into_cypher_file():
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_Gene_GO.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_gene{ gene_id:line.GeneID }), (g:CTD_GO{ go_id:line.GOID }) Create (c)-[a:associates_GGO{unbiases:false, url:"http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID}]->(g) ;\n'''

    cypher_file_edges.write(query)

    with open(path_of_ctd_data + '/ctd_data/CTD_Gene_GO.tsv', 'w', encoding='utf-8', newline='') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
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
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_genes_pathways.tsv" As line FIELDTERMINATOR '\\t' Merge (c:CTD_gene{ gene_id:line.GeneID }) On Create Set  c.geneSymbol=line.GeneSymbol;\n'''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_genes_pathways.tsv" As line FIELDTERMINATOR '\\t' Merge (g:CTD_pathway{ pathway_id:split(line.PathwayID,':')[1] }) On Create Set g.name=line.PathwayName ;\n'''
    cypher_file_nodes.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_genes_pathways.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_gene{ gene_id:line.GeneID }), (g:CTD_pathway{ pathway_id:split(line.PathwayID,':')[1] }) Create (c)-[a:participates_GP{unbiases:false, url:"http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID}]->(g) ;\n'''

    cypher_file_edges.write(query)


'''
load ctd disease-pathway file:
    0:DiseaseName
    1:DiseaseID
    2:PathwayName
    3:PathwayID
    4:InferenceGeneSymbol
and gather the information
'''


def load_disease_pathway():
    if not reduced:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_diseases_pathways.tsv" As line FIELDTERMINATOR '\\t' Merge (c:CTD_disease{ disease_id:split(line.DiseaseID,':')[1] }) On Create Set  c.name=line.DiseaseName;\n'''
        cypher_file_nodes.write(query)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_diseases_pathways.tsv" As line FIELDTERMINATOR '\\t' Merge  (g:CTD_pathway{ pathway_id:line.PathwayID })  On Create Set g.name=line.PathwayName;\n'''
        cypher_file_nodes.write(query)

        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_diseases_pathways.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_disease{ disease_id:split(line.DiseaseID,':')[1] }), (g:CTD_pathway{ pathway_id:split(line.PathwayID,':')[1] })  Create (c)-[:associates_DP{inferenceGeneSymbol:line.InferenceGeneSymbol, url:"http://ctdbase.org/detail.go?type=disease&acc="+split(line.DiseaseID,':')[1]}]->(g);\n'''

        cypher_file_edges.write(query)




'''
load ctd chemical-gene file:
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
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_gene_ixns.tsv" As line FIELDTERMINATOR '\\t' Merge (c:CTD_chemical{ chemical_id:line.ChemicalID }) On Create Set c.casRN=line.CasRN, c.name=line.ChemicalName;\n'''
    cypher_file_nodes.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_gene_ixns.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_chemical{ chemical_id:line.ChemicalID }), (g:CTD_gene{ gene_id:line.GeneID }) Create (c)-[:associates_CG{unbiased:false, gene_forms:split(line.GeneForms,'|'), organism:line.Organism, organism_id:line.OrganismID, interaction_text:line.Interaction, interactions_actions:split(line.InteractionActions,'|'), pubMed_ids:split(line.PubMedIDs,'|'), url:" http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID }]->(g);\n'''

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
    if not reduced:
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_pathways_enriched.tsv" As line FIELDTERMINATOR '\\t' Merge (c:CTD_chemical{ chemical_id:line.ChemicalID }) On Create Set c.casRN=line.CasRN, c.name=line.ChemicalName ;\n'''
        cypher_file_nodes.write(query)
        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_pathways_enriched.tsv" As line FIELDTERMINATOR '\\t' Merge (g:CTD_pathway{ pathway_id:split(line.PathwayID,':')[1] }) On Create Set g.name=line.PathwayName;\n'''
        cypher_file_nodes.write(query)

        query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chem_pathways_enriched.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_chemical{ chemical_id:line.ChemicalID }), (g:CTD_pathway{ pathway_id:split(line.PathwayID,':')[1]}) Create (c)-[:associates_CP{url:"http://ctdbase.org/detail.go?type=chem&acc="+line.ChemicalID ,unbiased:True, pValue:line.PValue, correctedPValue:line.CorrectedPValue, targetMatchQty:line.TargetMatchQty, targetTotalQty:line.TargetTotalQty, backgroundMatchQty:line.BackgroundMatchQty, backgroundTotalQty:line.BackgroundTotalQty }]->(g);\n'''

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
    file_name = '/ctd_data/CTD_chemicals_diseases.tsv'
    if reduced:
        file = open(path_of_ctd_data + file_name, 'r', encoding='utf-8')
        csv_reader = csv.DictReader(file, delimiter='\t')

        generated_header = False
        file_name = '/ctd_data/CTD_chemicals_diseases_reduced.tsv'
        write_file = open(path_of_ctd_data + file_name, 'w', encoding='utf-8')
        counter = 0
        counter_evidence_line = 0
        for line_dict in csv_reader:
            if not generated_header:
                csv_writer = csv.DictWriter(write_file, fieldnames=list(line_dict.keys()), delimiter='\t')
                csv_writer.writeheader()
                generated_header=True
            if line_dict['DirectEvidence'] != '':
                csv_writer.writerow(line_dict)
                counter_evidence_line += 1
            counter += 1
            if counter % 5000000 == 0:
                print(counter, datetime.datetime.now(), counter_evidence_line)
        file.close()
        write_file.close()

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + file_name + '''" As line FIELDTERMINATOR '\\t' Merge (c:CTD_chemical{ chemical_id:line.ChemicalID }) On Create  Set  c.casRN=line.CasRN, c.name=line.ChemicalName;\n'''
    cypher_file_nodes.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + file_name + '''" As line FIELDTERMINATOR '\\t' Merge (g:CTD_disease{ disease_id:split(line.DiseaseID,':')[1]}) On Create Set  g.name=line.DiseaseName;\n'''
    cypher_file_nodes.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_chemicals_diseases.tsv" As line FIELDTERMINATOR '\\t' Match (c:CTD_chemical{ chemical_id:line.ChemicalID }), (g:CTD_disease{ disease_id:split(line.DiseaseID,':')[1] }) Create (c)-[:associates_CD{ url:"http://ctdbase.org/detail.go?type=chem&acc="+line.ChemicalID ,directEvidence:line.DirectEvidence, inferenceGeneSymbol:line.InferenceGeneSymbol, inferenceScore:line.InferenceScore, omimIDs:split(line.OmimIDs,'|'), pubMed_ids:split(line.PubMedIDs,'|') }]->(g);\n'''

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
    file_name = '/ctd_data/CTD_genes_diseases.tsv'
    if reduced:
        file = open(path_of_ctd_data + file_name, 'r', encoding='utf-8')
        csv_reader = csv.DictReader(file, delimiter='\t')

        generated_header = False
        file_name = '/ctd_data/CTD_genes_diseases_reduced.tsv'
        write_file = open(path_of_ctd_data + file_name, 'w', encoding='utf-8')
        counter = 0
        counter_evidence_line = 0
        for line_dict in csv_reader:
            if not generated_header:
                csv_writer = csv.DictWriter(write_file, fieldnames=list(line_dict.keys()), delimiter='\t')
                csv_writer.writeheader()
                generated_header=True
            if line_dict['DirectEvidence'] != '':
                csv_writer.writerow(line_dict)
                counter_evidence_line += 1
            counter += 1
            if counter % 5000000 == 0:
                print(counter, datetime.datetime.now(), counter_evidence_line)
        file.close()
        write_file.close()
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + file_name + '''" As line FIELDTERMINATOR '\\t' Merge (g:CTD_disease{ disease_id:split(line.DiseaseID,':')[1] }) On Create Set g.name=line.DiseaseName;\n'''
    cypher_file_nodes.write(query)

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + file_name + '''" As line FIELDTERMINATOR '\\t' Match (c:CTD_gene{ gene_id:line.GeneID }), (g:CTD_disease{ disease_id:split(line.DiseaseID,':')[1] }) Create (c)-[:associates_GD{ url:"http://ctdbase.org/detail.go?type=gene&acc="+line.GeneID , directEvidence:line.DirectEvidence, inferenceChemicalName:line.InferenceChemicalName, inferenceScore:line.InferenceScore, omimIDs:split(line.OmimIDs,'|'), pubMed_ids:split(line.PubMedIDs,'|') }]->(g);\n'''

    cypher_file_edges.write(query)


def genereate_rela_file(file_name, dict_rela_to_file, rela, label, label_id, rela_properties, rela_name='associates'):
    """
    prepare tsv file and cypher query
    :param file_name: string
    :param dict_rela_to_file:dict
    :param rela: string
    :return:
    """
    file_rela_stressor = open(path_of_ctd_data + '/ctd_data/' + file_name + '.tsv', 'w', encoding='utf-8')
    tsv_rela_stressor = csv.writer(file_rela_stressor, delimiter='\t')
    tsv_rela_stressor.writerow(['reference', 'Id'])
    dict_rela_to_file[rela] = tsv_rela_stressor

    global cypher_file_edges

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/''' + file_name + '''.tsv" As line FIELDTERMINATOR '\\t' Match (c:%s{ %s:line.Id }), (g:CTD_exposureStudy{ reference:line.reference}) Create (g)-[:%s %s]->(c);\n'''
    query = query % (label, label_id, rela_name, rela_properties)
    cypher_file_edges.write(query)


def prepare_exposure_studies():
    """
    Reference
    StudyFactors ( | delimited list)
    ExposureStressors ( | delimited list ) entries formatted as Name^Id^Source
    Receptors ( | delimited list) formatted as Name^Id^Source^description
    StudyCountries (| delimited list)
    Mediums (| delimited list)
    ExposureMarkers ( | delimited list) entries formatted as Name^Id^Source
    Diseases ( | delimited list) entries formatted as Name^Id^Source
    Phenotypes ( | delimited list) entries formatted as Name^Id^Source
    AuthorSummary

    :return:
    """
    global cypher_file_nodes
    file = open(path_of_ctd_data + '/ctd_data/CTD_exposure_studies.tsv', 'r', encoding='utf-8')
    csv_reader = csv.DictReader(file, delimiter='\t')
    header = csv_reader.fieldnames

    other_properties = ['exposurestressors', 'exposuremarkers', 'diseases', 'phenotypes']
    properties_with_list = ['mediums', 'studycountries', 'receptors', 'studyfactors']

    exposure_header = [x for x in header if x not in other_properties]

    cypher_file_nodes.write(':begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created

    cypher_file_nodes.write('Create Constraint On (node:CTD_exposureStudy) Assert node.reference Is Unique;\n')
    cypher_file_nodes.write(':commit\n')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/CTD_exposure_studies.tsv" As line FIELDTERMINATOR '\\t'  Create (g:CTD_exposureStudy{ '''
    for exposure_head in exposure_header:
        if exposure_head == '':
            continue
        if exposure_head in properties_with_list:
            query += exposure_head + ':split(line.' + exposure_head + ', "|"), '
        else:
            query += exposure_head + ':line.' + exposure_head + ', '
    query += "url:'http://ctdbase.org/detail.go?type=reference&acc='+ line.reference});\n"
    cypher_file_nodes.write(query)

    dict_rela_to_file = {}
    property_for_rela = '{ url:"http://ctdbase.org/detail.go?type=reference&acc="+line.reference  }'

    genereate_rela_file('CTD_exposure_studies_stressor_rela', dict_rela_to_file, 'stressor', 'CTD_chemical',
                        'chemical_id', property_for_rela, rela_name='stressor')
    genereate_rela_file('CTD_exposure_studies_marker_gene_rela', dict_rela_to_file, 'marker_gene', 'CTD_gene',
                        'gene_id',
                        property_for_rela, rela_name='marker')
    genereate_rela_file('CTD_exposure_studies_marker_chem_rela', dict_rela_to_file, 'marker_chem', 'CTD_chemical',
                        'chemical_id', property_for_rela, rela_name='marker')
    genereate_rela_file('CTD_exposure_studies_disease_rela', dict_rela_to_file, 'disease', 'CTD_disease', 'disease_id',
                        property_for_rela)
    genereate_rela_file('CTD_exposure_studies_phenotype_rela', dict_rela_to_file, 'pheno', 'CTD_GO', 'go_id',
                        property_for_rela)

    for line in csv_reader:
        reference = line['reference']
        for exposure_stressor in line['exposurestressors'].split('|'):
            stressor_id = exposure_stressor.split('^')[1]
            dict_rela_to_file['stressor'].writerow([reference, stressor_id])

        if line['exposuremarkers'] != '':
            for marker in line['exposuremarkers'].split('|'):
                marker = marker.split('^')
                if marker[2] == 'GENE':
                    dict_rela_to_file['marker_gene'].writerow([reference, marker[1]])
                else:
                    dict_rela_to_file['marker_chem'].writerow([reference, marker[1]])
        if line['phenotypes'] != '':
            for disease in line['phenotypes'].split('|'):
                disease = disease.split('^')
                dict_rela_to_file['pheno'].writerow([reference, disease[1]])
        if line['diseases'] != '':
            for pheno in line['diseases'].split('|'):
                pheno = pheno.split('^')
                dict_rela_to_file['disease'].writerow([reference, pheno[1]])


def genereate_rela_file_event(file_name, dict_rela_to_file, rela, label, label_id, rela_name='associates',
                              rela_property=''):
    """
    prepare csv file and cypher query
    :param file_name: string
    :param dict_rela_to_file:dict
    :param rela: string
    :return:
    """
    file_rela_stressor = open(path_of_ctd_data + '/ctd_data/' + file_name + '.tsv', 'w', encoding='utf-8')
    tsv_rela_stressor = csv.writer(file_rela_stressor, delimiter='\t')
    tsv_rela_stressor.writerow(['exposureId', 'Id']) if rela_property == "" else tsv_rela_stressor.writerow(
        ['exposureId', 'Id', rela_property])
    dict_rela_to_file[rela] = tsv_rela_stressor

    global cypher_file_edges

    rela_property = '{ ' + rela_property + ':line.' + rela_property + '}' if rela_property != '' else ''
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/''' + file_name + '''.tsv" As line FIELDTERMINATOR '\\t' Match (c:%s{ %s:line.Id }), (g:CTD_exposureEvents{ id:line.exposureId}) Create (g)-[:%s %s]->(c);\n'''
    query = query % (label, label_id, rela_name.lower(), rela_property)
    cypher_file_edges.write(query)


def prepare_exposure():
    global cypher_file_nodes
    file = open(path_of_ctd_data + '/ctd_data/CTD_exposure_events.tsv', 'r', encoding='utf-8')
    csv_reader = csv.DictReader(file, delimiter='\t')

    header = csv_reader.fieldnames
    exposure_id = 0

    other_properties = ['exposurestressorname', 'exposurestressorid', 'exposuremarker', 'exposuremarkerid',
                        'outcomerelationship', 'diseasename', 'diseaseid', 'phenotypename', 'phenotypeid',
                        'phenotypeactiondegreetype', 'reference']  # , 'anatomy'
    properties_with_list = ['stressorsourcecategory', 'smokingstatus', 'sex', 'race', 'methods', 'studycountries',
                            'stateorprovince', 'citytownregionarea', 'associatedstudytitles', 'studyfactors',
                            'receptors']

    exposure_header = [x for x in header if x not in other_properties]
    exposure_header.append('id')

    cypher_file_nodes.write(':begin\n')
    # depending if chemicals are in neo4j or not the nodes need to be merged or created

    cypher_file_nodes.write('Create Constraint On (node:CTD_exposureEvents) Assert node.id Is Unique;\n')
    cypher_file_nodes.write(':commit\n')

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:''' + path_of_ctd_data + '''/ctd_data/exposure.tsv" As line Fieldterminator "\\t" Create  (g:CTD_exposureEvents{ '''
    for exposure_head in exposure_header:
        if exposure_head == '':
            continue
        if exposure_head in properties_with_list:
            query += exposure_head + ':split(line.' + exposure_head + ', "|"), '
        else:
            query += exposure_head + ':line.' + exposure_head + ', '
    query += "url:'http://ctdbase.org/detail.go?type=chem&acc='+line.chemicalID});\n"
    cypher_file_nodes.write(query)

    exposure_header.append('chemicalID')

    write_file = open(path_of_ctd_data + '/ctd_data/exposure.tsv', 'w', encoding='utf-8')
    csv_writer = csv.writer(write_file, delimiter='\t')
    csv_writer.writerow(exposure_header)

    dict_event_rela_to_tsv = {}
    genereate_rela_file_event('stressor_exposure', dict_event_rela_to_tsv, 'stressor', 'CTD_chemical', 'chemical_id',
                              rela_name='stressor')
    genereate_rela_file_event('marker_chem_exposure', dict_event_rela_to_tsv, 'marker_chem', 'CTD_chemical',
                              'chemical_id', rela_name='marker')
    genereate_rela_file_event('marker_gene_exposure', dict_event_rela_to_tsv, 'marker_gene', 'CTD_gene', 'gene_id',
                              rela_name='marker')
    genereate_rela_file_event('reference_exposure', dict_event_rela_to_tsv, 'reference', 'CTD_exposureStudy',
                              'reference')

    for line in csv_reader:
        exposure_stressor = line['exposurestressorid']

        dict_event_rela_to_tsv['stressor'].writerow([exposure_id, exposure_stressor])
        dict_event_rela_to_tsv['reference'].writerow([exposure_id, line['reference']])

        exposure_marker = line['exposuremarkerid']
        if exposure_marker.startswith('D') or exposure_marker.startswith('C'):
            dict_event_rela_to_tsv['marker_chem'].writerow([exposure_id, exposure_marker])
        else:
            dict_event_rela_to_tsv['marker_gene'].writerow([exposure_id, exposure_marker])

        outcome_relas = line['outcomerelationship']
        outcome_relas = outcome_relas.replace(' ', '_').replace('/', '_') if outcome_relas != '' else 'associates'

        if line['diseaseid'] != "":
            if 'disease_' + outcome_relas not in dict_event_rela_to_tsv:
                genereate_rela_file_event('disease_exposure_' + outcome_relas, dict_event_rela_to_tsv,
                                          'disease_' + outcome_relas, 'CTD_disease', 'disease_id',
                                          rela_name=outcome_relas)
            dict_event_rela_to_tsv['disease_' + outcome_relas].writerow([exposure_id, line['diseaseid']])
        if line['phenotypeid'] != "":
            if 'go_' + outcome_relas not in dict_event_rela_to_tsv:
                genereate_rela_file_event('go_exposure_' + outcome_relas, dict_event_rela_to_tsv, 'go_' + outcome_relas,
                                          'CTD_GO', 'go_id', rela_name=outcome_relas,
                                          rela_property='phenotypeactiondegreetype')
            dict_event_rela_to_tsv['go_' + outcome_relas].writerow(
                [exposure_id, line['phenotypeid'], line['phenotypeactiondegreetype']])

        exposure_marker_gene_chemical = line['exposuremarkerid']
        # prepare exposure node
        exposure_entries = []
        for head, value in line.items():
            if head not in other_properties:
                # if head in properties_with_list:
                #     value=value.split('|')
                exposure_entries.append(value)
        exposure_entries.append(exposure_id)
        exposure_entries.append(exposure_stressor)
        csv_writer.writerow(exposure_entries)

        exposure_id += 1


# delete node file
delet_node_file = open('cypher/nodes_delete.cypher', 'w')

'''
ad node deleter for all nodes which have no relationship to other nodes
'''


def delete_nodes_with_no_relationship(label):
    delet_node_file.write(':begin\n')
    query = '''MATCH (n:%s) Where not (n)--() Delete n;\n'''
    query = query % (label)
    delet_node_file.write(query)
    delet_node_file.write(':commit\n')


# path to directory
path_of_ctd_data = ''


def main():
    global path_of_ctd_data, reduced

    reduced = False
    if len(sys.argv) == 2:
        path_of_ctd_data = sys.argv[1]
    elif len(sys.argv) > 1:

        path_of_ctd_data = sys.argv[1]
        reduced = True

    else:
        sys.exit('need a path to ctd data and maybe reduced True')

    print(reduced, len(sys.argv))
    print(datetime.datetime.now())

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd chemical and add to cypher file')

    load_chemicals_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd pathway and add to cypher file')

    load_pathway_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd anatomy and add to cypher file')

    load_anatomy_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd gene and add to cypher file')

    load_gene_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd disease and add to cypher file')

    load_disease_and_add_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd chemical-go and gather the information')

    load_chemical_go_enriched()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd chemical-phenotype and gather the information')

    load_chemical_phenotype()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('load in ctd phenotype disease-go and gather the information')

    load_disease_go_inference('CTD_Phenotype-Disease_cellular_component_associations.tsv',
                              'CTD_Phenotype-Disease_molecular_function_associations.tsv',
                              'CTD_Phenotype-Disease_biological_process_associations.tsv')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add go to node cypher file')

    add_go_to_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add gene-go relationship to cypher file')

    gene_go_into_cypher_file()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add gene-pathway relationship to cypher file')

    load_gene_pathway()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add disease-pathway relationship to cypher file')

    load_disease_pathway()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add chemical-gene relationship to cypher file')

    load_chemical_gene()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add chemical-pathway relationship to cypher file')

    load_chemical_pathway_enriched()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add chemical-disease relationship to cypher file')

    load_chemical_disease()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add gene-disease relationship to cypher file')

    load_gene_disease()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add exposure study and relas')

    prepare_exposure_studies()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('add exposure event and relas')

    prepare_exposure()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('delete nodes with no realtionships')

    delete_nodes_with_no_relationship('CTD_GO')
    # delete_nodes_with_no_relationship('CTD_chemical')
    delete_nodes_with_no_relationship('CTD_disease')
    delete_nodes_with_no_relationship('CTD_gene')
    delete_nodes_with_no_relationship('CTD_pathway')

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
