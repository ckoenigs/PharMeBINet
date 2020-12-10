sys.path.append("../..")
import create_connection_to_databases, authenticate
import sys
import datetime
import csv




# node cypher file number
node_file_number = 1

# edges cypher file number
edges_file_number = 1

# cypher file for all nodes
cypher_file_nodes = open('cypher/nodes_' + str(node_file_number) + '.cypher', 'w')
node_file_number += 1
cypher_file_nodes.write('begin\n')

# cypher file for all relationships
cypher_file_edges = open('cypher/edges_' + str(edges_file_number) + '.cypher', 'w')
edges_file_number += 1
cypher_file_edges.write('begin\n')

# count the number of queries of node generation
counter_nodes_queries = 0
# count the number of queries of node generation
counter_edges_queries = 0
# number of queries in a commit block
constraint_number = 20000
# number of queries in a cypher file
max_queries_for_a_file = 300000

dict_chemicals={}



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


    # add the chemical nodes to cypher file
    with open('ctd_data/CTD_chemicals.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:

            if i > 0:
                chemical_id = row[1]
                dict_chemicals[chemical_id]=1
            i+=1



    print('number of chemicals:'+str(len(dict_chemicals)))

dict_disease={}

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


    # add the chemical nodes to cypher file
    with open('ctd_data/CTD_diseases.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:

            if i > 0:

                disease_id = row[1].split(':')
                id_type = disease_id[0]
                disease_id = disease_id[1]

                dict_disease[disease_id]=1

            i += 1

    print('number of disease:'+ str(len(dict_disease)))

list_pathway={}
'''
load ctd pathway file and generate cypher file for the nodes with properties:
    0:PathwayName
    1:PathwayID
furthermore it test if already nodes are in Neo4j and only add the new ones 
'''


def load_pathway_and_add_to_cypher_file():


    # add the chemical nodes to cypher file
    with open('ctd_data/CTD_pathways.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:

            if i > 0:
                name = row[0]
                pathway_id = row[1].split(':')
                id_type = pathway_id[0]
                pathway_id = pathway_id[1]
                list_pathway[pathway_id]=1

            i += 1


    print('number of pathway:'+str(len(list_pathway)))

list_genes={}
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


    # add the chemical nodes to cypher file
    with open('ctd_data/CTD_genes.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        for row in reader:

            if i > 0:
                name = row[1]
                gene_id = row[2]


                list_genes[gene_id]=1

            i += 1

    print('number of genes:'+str(len(list_genes)))


# dictionary for GO with values 0:name,  1:ontology, 2:HighestGOLevel
dict_Go_properties = {}

# dictionary with (chemical_id, go_id) and properties as value PValue,CorrectedPValue,TargetMatchQty,TargetTotalQty,BackgroundMatchQty,BackgroundTotalQty
dict_chemical_go = {}
dict_of_not_chemicals={}

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
    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_chem_go_enriched.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        counter_not_existing_chemicals=0
        for row in reader:

            if i > 0:
                chemical_id = row[1]
                if not chemical_id in dict_chemicals:
                    counter_not_existing_chemicals+=1
                    dict_of_not_chemicals[chemical_id]=1

            i += 1

    print('number of chemical not existing :'+str(counter_not_existing_chemicals))
    print('number of total:'+str(len(dict_of_not_chemicals)))


# dictionary with (disease_id, go_id) and properties as value inferenceGeneSymbol, inference GeneQty
dict_disease_go = {}

# list of gene-go pairs
list_gene_go = []

'''
gather information from disease-go infernce
'''


def gather_information_from_disease_go_inferencen(file, ontology):
    with open('ctd_data/' + file) as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        counter_not_disease=0
        dict_of_not_disease = {}
        for row in reader:

            if i > 0:
                disease_id = row[1]
                if disease_id not in dict_disease:
                    dict_of_not_disease[disease_id]=1
                    counter_not_disease+=1


            i += 1

    print('number of disease not existing:'+str(counter_not_disease))
    print('number of total:' + str(len(dict_of_not_disease)))


'''
load ctd disease-go enriched files for biological process, molecular function and cellular componenet
    0:DiseaseName
    1:DiseaseID
    2:GOName
    3:GOID
    4:InferenceGeneQty
    5:InferenceGeneSymbols
gather the information
'''


def load_disease_go_inference():
    print('start Cellular Component')
    print(datetime.datetime.utcnow())
    gather_information_from_disease_go_inferencen('CTD_Disease-GO_cellular_component_associations.csv',
                                                  'Cellular Component')
    print('start Molecular Function')
    print(datetime.datetime.utcnow())
    gather_information_from_disease_go_inferencen('CTD_Disease-GO_molecular_function_associations.csv',
                                                  'Molecular Function')
    print('start Biological Process')
    print(datetime.datetime.utcnow())
    gather_information_from_disease_go_inferencen('CTD_Disease-GO_biological_process_associations.csv',
                                                  'Biological Process')

    print(len(dict_Go_properties))


dict_gene_not_existing_pathway={}
dict_pathway_not_existing_gene={}

'''
load ctd gene-pathway file:
    0:GeneSymbol
    1:GeneID
    2:PathwayName
    3:PathwayID
and gather the information
'''

def load_gene_pathway():


    count_gene_pathway_pairs = 0
    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_genes_pathways.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        count_gene_not_existing=0
        count_pathway_not_existing=0
        for row in reader:

            if i > 0:
                count_gene_pathway_pairs += 1
                gene_id = row[1]
                if not gene_id in list_genes:
                    dict_gene_not_existing_pathway[gene_id]=1
                    count_gene_not_existing+=1
                pathway_id = row[3]

                if not pathway_id in list_pathway:
                    dict_pathway_not_existing_gene[pathway_id]=1
                    count_pathway_not_existing+=1


            i += 1


    print('not existing genes:' + str(count_gene_not_existing))
    print('not existing pathways:' + str(count_pathway_not_existing))
    print('not existing genes:' + str(len(dict_gene_not_existing_pathway)))
    print('not existing pathways:' + str(len(dict_pathway_not_existing_gene)))


dict_disease_not_existing_pathway={}
dict_pathway_not_existing_disease={}


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

    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_diseases_pathways.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        count_disease_not_existing = 0
        count_pathway_not_existing = 0
        for row in reader:

            if i > 0:
                disease_id = row[1]
                pathway_id= row[3]
                if not disease_id in dict_disease:
                    dict_disease_not_existing_pathway[disease_id]=1
                    count_disease_not_existing += 1

                if not pathway_id in list_pathway:
                    dict_pathway_not_existing_disease[pathway_id]=1
                    count_pathway_not_existing += 1


            i += 1


    print('not existing disease:' + str(count_disease_not_existing))
    print('not existing pathways:' + str(count_pathway_not_existing))
    print('not existing disease:' + str(len(dict_disease_not_existing_pathway)))
    print('not existing pathways:' + str(len(dict_pathway_not_existing_disease)))

dict_gene_not_existing_chemical={}
dict_chemical_not_existing_gene={}

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

    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_chem_gene_ixns.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        count_chemaical_not_existing = 0
        count_gene_not_existing = 0
        for row in reader:

            if i > 0:

                chemical_id = row[1]
                gene_id= row[4]
                if not chemical_id in dict_chemicals:
                    dict_chemical_not_existing_gene[chemical_id]=1
                    count_chemaical_not_existing += 1

                if not gene_id in list_genes:
                    dict_gene_not_existing_chemical[gene_id]=1
                    count_gene_not_existing += 1

            i += 1

    print('not existing genes:' + str(count_gene_not_existing))
    print('not existing chemical:' + str(count_chemaical_not_existing))
    print('not existing genes:' + str(len(dict_gene_not_existing_chemical)))
    print('not existing chemical:' + str(len(dict_chemical_not_existing_gene)))

# ChemicalName	ChemicalID	CasRN	PathwayName	PathwayID	PValue	CorrectedPValue	TargetMatchQty	TargetTotalQty	BackgroundMatchQty	BackgroundTotalQty

dict_pathway_not_existing_chemical={}
dict_chemical_not_existing_pathway={}

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
    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_chem_pathways_enriched.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        count_chemical_not_existing = 0
        count_pathway_not_existing = 0
        for row in reader:

            if i > 0:
                chemical_id = row[1]
                pathway_id= row[4]
                if not chemical_id in dict_chemicals:
                    dict_chemical_not_existing_pathway[chemical_id]=1
                    count_chemical_not_existing += 1

                if not pathway_id in list_pathway:
                    dict_pathway_not_existing_chemical[pathway_id]=1
                    count_pathway_not_existing += 1

            i += 1

    print('not existing pathway:' + str(count_pathway_not_existing))
    print('not existing chemical:' + str(count_chemical_not_existing))
    print('not existing pathway:' + str(len(dict_pathway_not_existing_chemical)))
    print('not existing chemical:' + str(len(dict_chemical_not_existing_pathway)))


dict_disease_not_existing_chemical={}
dict_chemical_not_existing_disease={}

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

    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_chemicals_diseases.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        count_chemical_not_existing = 0
        count_disease_not_existing = 0
        for row in reader:

            if i > 0:
                chemical_id = row[1]
                disease_id= row[4]
                if not chemical_id in dict_chemicals:
                    dict_chemical_not_existing_disease[chemical_id]=1
                    count_chemical_not_existing += 1

                if not disease_id in dict_disease:
                    dict_disease_not_existing_chemical[disease_id]=1
                    count_disease_not_existing += 1

            i += 1

    print('not existing disease:' + str(count_disease_not_existing))
    print('not existing chemical:' + str(count_chemical_not_existing))
    print('not existing disease:' + str(len(dict_disease_not_existing_chemical)))
    print('not existing chemical:' + str(len(dict_chemical_not_existing_disease)))


dict_disease_not_existing_gene={}
dict_gene_not_existing_disease={}

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

    # gather information from CTD chemical-go enriched
    with open('ctd_data/CTD_genes_diseases.csv') as csvfile:
        reader = csv.reader(csvfile)
        i = 0
        count_gene_not_existing = 0
        count_disease_not_existing = 0
        for row in reader:

            if i > 0:
                gene_id = row[1]
                disease_id= row[3]
                if not gene_id in list_genes:
                    dict_gene_not_existing_disease[gene_id]=1
                    count_gene_not_existing += 1

                if not disease_id in dict_disease:
                    dict_disease_not_existing_gene[disease_id]=1
                    count_disease_not_existing += 1

            i += 1

    print('not existing disease:' + str(count_disease_not_existing))
    print('not existing gene:' + str(count_gene_not_existing))
    print('not existing disease:' + str(len(dict_disease_not_existing_gene)))
    print('not existing gene:' + str(len(dict_gene_not_existing_disease)))



def main():
    print(datetime.datetime.utcnow())

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
    print('load in ctd disease-go and gather the information')

    load_disease_go_inference()


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


if __name__ == "__main__":
    # execute only if run as a script
    main()
