'''integrate the'''
from collections import  defaultdict
from py2neo import Graph, authenticate
import datetime
import sys, csv

'''
create a connection with neo4j
'''


def create_connetion_with_neo4j():
    # set up authentication parameters and connection
    authenticate("localhost:7474", "neo4j", "test")
    global g
    g = Graph("http://localhost:7474/db/data/")

# dictionary of biological process key is the id and value the name
dict_bp_to_name={}
# dictionary of cellular component key is the id and value the name
dict_cc_to_name={}
# dictionary of molecular function key is the id and value the name
dict_mf_to_name={}

# function integrate identifier and name into the right dictionary
def integrate_information_into_dict(entity_name,dict_go):
    query = '''MATCH (n:'''+entity_name +''') RETURN n.identifier, n.name'''
    results = g.run(query)

    counter_entities=0
    for identifier, name, in results:
        dict_go[identifier]=name
        counter_entities+=1

    print('It exists ' + str(counter_entities) + ' '+ entity_name)
    print(len(dict_go))


# load all information of biological process, cellular component and molecular function and put this information into a dictionary
def load_bp_cc_mf_information():
    integrate_information_into_dict('BiologicalProcess',dict_bp_to_name)
    integrate_information_into_dict('CellularComponent', dict_cc_to_name)
    integrate_information_into_dict('MolecularFunction', dict_mf_to_name)


#dictionary from uniprot to gene id from hetionet information
dict_uniprot_to_gene_id={}

#dict_uniprot_count_genes from hetionet information
dict_uniprot_count_genes={}

#dictionary gene id to gene symbol/name
dict_gene_to_name={}

#dictionary gene id to gene name
dict_gene_id_to_gene_name={}

#dictionary gene name to genes without uniprot list
dict_gene_symbol_to_gene_without_uniprot={}
dict_gene_symbol_to_gene_id={}

# list of all gene symbols which appears in multiple genes
list_double_gene_symbol_for_genes_without_uniprot_id = set([])

#dictionary gene name to gene id
dict_gene_name_to_id=defaultdict(list)

# dictionary of the uniprot ids which mapped wrong to the correct ncbi gene id
# Q96NJ1 (Uncharacterized protein FLJ30774) mapped to 158055 (c9orf163) and with tblastn I found out that the protein is
# part of the orf
dict_wrong_uniprot_to_correct_gene_id={
    'Q8N8H1':'399669',
    'A2RUG3':'353515',
    'E5RIL1':'107983993',
    'P0DI82':'10597',
    'P0DMW3':'100129361',
    'H3BUK9':'100287399',
    'Q5XG87':'64282',
    'Q8NDF8':'11044',
    'A0A024RBG1':'440672',
    'P0DMR1':'101060301',
    'P30042':'102724023',
    'P0DPD8':'110599583',
    'P0DP73':'100133267',
    'P0DMV2':'102723680',
    'P0DMV1':'102723737',
    'A0A1B0GUU1':'110806298'
}

'''
Find mapping between genes and proteins
'''
def get_all_genes():
    query='''MATCH (n:Gene) RETURN n.identifier, n.uniProtIDs, n.geneSymbol, n.name'''
    results=g.run(query)
    counter_uniprot_to_multiple_genes=0
    counter_all_genes=0
    list_double_names=set([])
    for gene_id, list_uniprots, genesymbols, name, in results:
        counter_all_genes+=1
        dict_gene_id_to_gene_name[gene_id]=name.lower()

        if gene_id==28299:
            print('ok')

        if genesymbols:

            genesymbols = [x.lower() for x in genesymbols]
            for genesymbol in genesymbols:
                if not genesymbol in dict_gene_symbol_to_gene_id:
                    dict_gene_symbol_to_gene_id[genesymbol] = [gene_id]
                else:
                    list_double_gene_symbol_for_genes_without_uniprot_id.add(genesymbol)

                    dict_gene_symbol_to_gene_id[genesymbol].append(gene_id)


        #fill the gene name to gene id dictionary
        if name.lower() in dict_gene_name_to_id:
            list_double_names.add(name.lower())
            dict_gene_name_to_id[name.lower()].append(gene_id)
        else:
            dict_gene_name_to_id[name.lower()].append(gene_id)
            
        # if a list of uniprot ids exists fill the dictionary of uniprot id to gene ids
        if list_uniprots:
            dict_gene_to_name[gene_id]=[x.lower() for x in genesymbols]
            for uniprot in list_uniprots:
                # generate dictionary for uniprot to gene(s)
                # and if more than two genes fit to one uniprot id they will be count
                if uniprot in dict_uniprot_to_gene_id:
                    dict_uniprot_to_gene_id[uniprot].append(gene_id)
                    dict_uniprot_count_genes[uniprot]=1+dict_uniprot_count_genes[uniprot] if uniprot in dict_uniprot_count_genes else 2
                    counter_uniprot_to_multiple_genes+=1
                else:
                    dict_uniprot_to_gene_id[uniprot]=[gene_id]
                    
        # to make it possible to map the genes without uniprot id generate a dictionary from gene symbol to gene id
        else:
            if genesymbols:

                genesymbols =[x.lower() for x in genesymbols]
                dict_gene_to_name[gene_id] = genesymbols
                # for name in genesymbols:
                #     if not name in dict_gene_symbol_to_gene_without_uniprot:
                #         dict_gene_symbol_to_gene_without_uniprot[name]=[gene_id]
                #     else:
                #         list_double_gene_symbol_for_genes_without_uniprot_id.add(name)
                #
                #         dict_gene_symbol_to_gene_without_uniprot[name].append(gene_id)
                #         # print(dict_gene_symbol_to_gene_without_uniprot[name])
                #         # print(name)
                #         # print('ohje doppelt gene name')
                #         # sys.exit('ohje doppelt gene name')
            else:
                dict_gene_to_name[gene_id] = name.lower()

    # all multiple uniprot ids from the hetionet genes
    file=open('uniprot_gene/uniprot_to_multi_genes.csv','w')
    writer=csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['uniprot','gene_ids'])
    for uniprot in dict_uniprot_count_genes.keys():
        string_gene_list='|'.join(str(x) for x in dict_uniprot_to_gene_id[uniprot])
        writer.writerow([uniprot, string_gene_list])

    print('number of uniprots which appears in multiple genes:'+str(counter_uniprot_to_multiple_genes))
    print('double gene symbol for genes without uniprot id:'+str(len(list_double_gene_symbol_for_genes_without_uniprot_id)))
    print(len(dict_uniprot_to_gene_id))
    print(len(dict_uniprot_count_genes))
    # print(dict_uniprot_count_genes)

    print('number of names to gene, which has no uniprots:'+str(len(dict_gene_symbol_to_gene_without_uniprot)))
    print('number of genes:'+str(counter_all_genes))
    print('number of multiple name:'+str(len(list_double_names)))


# files with rela from uniprot protei to gene with multiple genes from  protein side
file_uniprots_with_multiple = open('uniprot_gene/db_uniprot_to_multi_genes.csv', 'w')
writer_multi = csv.writer(file_uniprots_with_multiple)
writer_multi.writerow(['uniprot_id', 'protein_name', 'genes', 'alternative_ids'])

# files with rela from uniprot protei to gene
file_uniprots_gene_rela = open('uniprot_gene/db_uniprot_to_gene_rela.csv', 'w')
writer_rela = csv.writer(file_uniprots_gene_rela)
writer_rela.writerow(['uniprot_id', 'gene_id', 'alternative_ids','name_mapping','ctd','uniprot','resource'])

# file with the gene ids where a uniprot needs to be delete from the uniprot lists
file_gene_uniprot = open('uniprot_gene/db_gene_uniprot_delete.csv', 'w')
writer_gene_uniprot= csv.writer(file_gene_uniprot)
writer_gene_uniprot.writerow(['gene_id', 'uniprot_id'])

# list of all uniprot ids which where wrong mapped and already found in the program to avoid duplication in the file
list_already_included=[]

# list of all already integrated pairs of gene uniprot id
list_already_integrated_pairs_gene_protein=[]


#counter for not matching gene names
count_not_mapping_gene_name=0

'''
check out mapping with use of name
'''
def check_mapped_gene_ids_with_name(dict_gene_ids_which_mapped, gene_names):
    list_fitting_gene_name = []
    same_gene_name=False

    # find the gene which has the same name as the protein from uniprot
    for gene_id in dict_gene_ids_which_mapped:
        for gene_name in gene_names:
            name_in_dict=dict_gene_to_name[int(gene_id)]
            if gene_name in dict_gene_to_name[int(gene_id)]:
                same_gene_name = True
                list_fitting_gene_name.append(gene_id)
    return list_fitting_gene_name, same_gene_name


'''
this goes throu a list of mapping gens and check out if they realy do not exists already
if not integrate them into the csv
'''
def check_and_add_rela_pair(identifier,uniprot_id, gene_ids,secondary_uniprot_ids, name_mapping, ctd_mapping, uniprot_mapping,map_resource):
    for gene_id in gene_ids:
        if not (identifier, int(gene_id)) in list_already_integrated_pairs_gene_protein:
            writer_rela.writerow([identifier, gene_id, secondary_uniprot_ids, name_mapping, ctd_mapping, uniprot_mapping, map_resource])
            list_already_integrated_pairs_gene_protein.append(
                (identifier, int(gene_id)))
            list_already_included.append(uniprot_id)


''' 
check if the uniprot id is in dictionary uniprot to gene and write into right file
all inputs are from the uniprot nodes
uniprot_id can be identifier or an alternative uniprot id 

gene_names are the genesymbol of uniport
gene_ids are the gene ids which from uniprot
'''
def check_and_write_uniprot_ids(uniprot_id,name,identifier,secondary_uniprot_ids,gene_names,gene_ids):
    global count_not_mapping_gene_name
    found_at_least_on = False

    gene_names= [x.lower( ) for x in gene_names]
    gene_names=list(set(gene_names))
    genes=[]
    same_gene_name=False

    name=name.split(' {E')[0].lower()

    # check if the uniprot id appears in the hetionet gene-uniprot multiple dictionary
    # if yes write this information in the multiple file
    if uniprot_id in dict_uniprot_count_genes:
        writer_multi.writerow([identifier, name, dict_uniprot_to_gene_id[uniprot_id],secondary_uniprot_ids])
        # find the gene which has the same name as the protein from uniprot
        list_fitting_gene_name,same_gene_name=check_mapped_gene_ids_with_name(dict_uniprot_to_gene_id[uniprot_id],gene_names)

        #only when one gene has the exact name sas the gene write it in the gene -protein rela file
        if same_gene_name:
            check_and_add_rela_pair(identifier,uniprot_id,list_fitting_gene_name,secondary_uniprot_ids,'yes','yes','no','CTD')

            found_at_least_on = True
            genes = list_fitting_gene_name

        else:
            gene_ids_hetionet=[str(x) for x in dict_uniprot_to_gene_id[uniprot_id]]
            difference_gene_ids=set(gene_ids).difference(gene_ids_hetionet)
            if len(difference_gene_ids)>0:
                list_fitting_gene_name, same_gene_name = check_mapped_gene_ids_with_name(
                    list(difference_gene_ids), gene_names)

                check_and_add_rela_pair(identifier, uniprot_id, difference_gene_ids, secondary_uniprot_ids, 'yes',
                                        'yes', 'yes','CTD|UniProt')

                found_at_least_on = True
                genes = difference_gene_ids
            else:
                print(identifier)
                print(dict_uniprot_to_gene_id[uniprot_id])
                print(gene_ids)
                print('name mapping is not working')


    # if an mapping between uniprot an gene exists in hetionet  write this relationship in csv file
    elif uniprot_id in dict_uniprot_to_gene_id:
        list_of_mapped_genes=[]

        #depending where the mapping is from
        yes_ctd='no'
        yes_uniprot='no'
        yes_name_mapping='no'

        list_of_resources=[]

        #first check out the mapping with each other (mapping from protein and mapping from gene)
        #because the mapping from gene is also part of the mapping of the genes only the mapping of protein has to be checked
        if len(gene_ids)>1:

            # if not str(dict_uniprot_to_gene_id[uniprot_id][0]) in gene_ids:
            #     sys.exit('not similar genes')
            yes_ctd='yes'
            yes_uniprot='yes'
            list_of_resources.append('CTD')
            list_of_resources.append('UniProt')
            list_of_mapped_genes, same_gene_name = check_mapped_gene_ids_with_name(
                gene_ids, gene_names)
            yes_name_mapping='yes'
            # print(identifier)
            # print(dict_uniprot_to_gene_id[uniprot_id])
            # print(gene_ids)
            # print(list_of_mapped_genes)
            # print('multiple from the other direction')


        elif len(gene_ids)==1 and gene_ids[0]!=str(dict_uniprot_to_gene_id[uniprot_id][0]):
            combined_list=gene_ids[:]
            combined_list.extend(dict_uniprot_to_gene_id[uniprot_id])
            list_of_mapped_genes, same_gene_name = check_mapped_gene_ids_with_name(
                combined_list, gene_names)
            yes_name_mapping = 'yes'

            #check out where the mapping is coming from
            for gene_id in list_of_mapped_genes:
                if gene_id in gene_ids:
                    yes_uniprot='yes'
                    list_of_resources.append('UniProt')
                elif gene_id in dict_uniprot_to_gene_id[uniprot_id]:
                    yes_ctd='yes'
                    list_of_resources.append('CTD')


            if len(list_of_mapped_genes)==0:
                sys.exit('non of gene and protein mapping is working')
            # print(identifier)
            # print(gene_ids)
            # print(dict_uniprot_to_gene_id[uniprot_id])
            # print(list_of_mapped_genes)
            # print('not the same mapping')
            # sys.exit('not the same mapping')
        elif len(gene_ids)==1 :
            yes_ctd = 'yes'
            list_of_resources.append('CTD')
            yes_uniprot='yes'
            list_of_resources.append('UniProt')
        else:
            yes_ctd = 'yes'
            list_of_resources.append('CTD')
            list_of_mapped_genes=dict_uniprot_to_gene_id[uniprot_id]

        string_list_resources='|'.join(list_of_resources)
        # if not the uniprot id is in the manual dictionary it can integrate
        if not uniprot_id in dict_wrong_uniprot_to_correct_gene_id:
            check_and_add_rela_pair(identifier, uniprot_id, list_of_mapped_genes, secondary_uniprot_ids,
                                    yes_name_mapping,yes_ctd,yes_uniprot,string_list_resources)

        else:
            # here is the possibility that the gene id is not in neo4j (so this can be a reason why not all relationships are integrated)
            # now it should work out
            if not (identifier, dict_wrong_uniprot_to_correct_gene_id[uniprot_id]) in list_already_integrated_pairs_gene_protein:
                writer_rela.writerow([identifier, dict_wrong_uniprot_to_correct_gene_id[uniprot_id], secondary_uniprot_ids,'no','no','no','Manual'])
                list_already_integrated_pairs_gene_protein.append((identifier, int(dict_wrong_uniprot_to_correct_gene_id[uniprot_id])))
            # change the gene uniprot list and exclude this uniprot id
            if uniprot_id not in list_already_included:
                writer_gene_uniprot.writerow([dict_uniprot_to_gene_id[uniprot_id][0], uniprot_id])
                list_already_included.append(uniprot_id)



        found_at_least_on = True

        genes = dict_uniprot_to_gene_id[uniprot_id]
    # if no gene is found in the multiple or single dictionary, search with name for on mapping or with the gene_ids from uniprot
    else:
        if identifier not in list_already_included:
            # check out the gene ids from uniprot
            if gene_ids and gene_names:
                list_of_mapped_genes, same_gene_name = check_mapped_gene_ids_with_name(
                    gene_ids, gene_names)
                # if the gene ids and nam mapping is working write into rela file
                if len(list_of_mapped_genes)!=0:
                    check_and_add_rela_pair(identifier, uniprot_id, list_of_mapped_genes, secondary_uniprot_ids,
                                            'yes', 'no', 'yes', 'UniProt')

                    return True, list_of_mapped_genes
                else:
                    if name.lower() in dict_gene_name_to_id:
                        name_mapped_list=[str(x) for x in dict_gene_name_to_id[name.lower()]]
                        intersection=set(gene_ids).intersection(name_mapped_list)
                        if len(intersection)> 0:
                            check_and_add_rela_pair(identifier, uniprot_id, intersection, secondary_uniprot_ids,
                                                   'yes', 'no', 'yes', 'UniProt')

                            return True, list(intersection)
                    else:
                        # print(identifier)
                        # print(gene_ids)
                        # print(gene_names)
                        # print(list_of_mapped_genes)
                        print('name with protein mapping')
            # check out if the mapping gene ids are good by checking the name
            # but it seems that even if the name are not the same they map correct
            elif gene_ids:
                if name.lower() in dict_gene_name_to_id:
                    list_gene_id_from_name=[str(x) for x in dict_gene_name_to_id[name.lower()]]
                    intersection=set(gene_ids).intersection(list_gene_id_from_name)
                    if len(intersection)>0:
                        check_and_add_rela_pair(identifier, uniprot_id, intersection, secondary_uniprot_ids,
                                                'yes', 'no', 'yes', 'UniProt')
                        genes=list(intersection)
                        found_at_least_on=True
                        return True, genes
                else:
                    print('only gene id mapping')

            # no mapping from the gene or protein and no gene symbol
            else:
                if name.lower() in dict_gene_name_to_id:
                    check_and_add_rela_pair(identifier, uniprot_id, dict_gene_name_to_id[name.lower()], secondary_uniprot_ids,
                                            'yes','no','no','NameMapping')

                    genes = dict_gene_name_to_id[name.lower()]
                    found_at_least_on = True
                    return True, genes

            # check if mapping is possible with gene symbol
            ## I have to check this out more but it seems like it works
            list_of_possible_mapped_gene_ids=set([])
            for gene_name in gene_names:
                if gene_name in dict_gene_symbol_to_gene_id and not gene_name in list_double_gene_symbol_for_genes_without_uniprot_id:
                    gene_ids_from_name=dict_gene_symbol_to_gene_id[gene_name]
                    list_of_possible_mapped_gene_ids=list_of_possible_mapped_gene_ids.union(gene_ids_from_name)
                    list_already_included.append(uniprot_id)
                elif gene_name in list_double_gene_symbol_for_genes_without_uniprot_id:
                    print(gene_name)
                    print(identifier)
                    print(dict_gene_symbol_to_gene_id[gene_name])
                    print('multiple name name mapping')

            #the multiple mapping with gene symbol are not the best only 4 of 14 this make sense but for the other it would be manual mapping
            if len(list_of_possible_mapped_gene_ids)==1:
                check_and_add_rela_pair(identifier, uniprot_id, list_of_possible_mapped_gene_ids,
                                        secondary_uniprot_ids, 'yes','no','no','GeneSymbolMapping')

                # print(identifier)
                # print(list_of_possible_mapped_gene_ids)
                found_at_least_on = True

    return found_at_least_on, genes

'''
Load all uniprots ids of the proteins and check out which appears also in the uniprot gene dictionary
'''
def get_gather_protein_info_and_generate_relas():
    #cypher file for nodes
    file_cypher_node=open('cypher_node.cypher','w')
    # cypher file to integrate the information into Hetionet
    file_cypher= open('cypher_rela.cypher','w')

    # file with every uniprot identifier
    file_uniprots_ids = open('db_uniprot_ids.csv', 'w')
    writer_uniprots_ids = csv.writer(file_uniprots_ids)
    writer_uniprots_ids.writerow(['uniprot_id'])


    #generate a file with all uniprots wich mapped to multiple genes
    file_uniprots_genes = open('uniprot_gene/db_uniprots_to_genes.csv', 'w')
    writer_uniprots_genes = csv.writer(file_uniprots_genes)
    writer_uniprots_genes.writerow(['uniprot_ids', 'gene_id'])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_gene/db_uniprot_to_gene_rela.csv" As line MATCH (n:Protein{identifier:line.uniprot_id}), (g:Gene{identifier:toInteger(line.gene_id)}) Create (g)-[:PRODUCES_GpP{name_mapping:line.name_mapping ,ctd:line.ctd,uniprot:line.uniprot,resource:split(line.resource,'|'),license:'Creative Commons Attribution (CC BY 4.0) License'}]->(n);\n'''
    file_cypher.write(query)

    # the queries to integrate rela to bc, cc and mf
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_go/db_uniprots_to_bc.csv" As line MATCH (g:Protein{identifier:line.uniprot_ids}),(b:BiologicalProcess{identifier:line.go}) Create (g)-[:PARTICIPATES_PRpBC{resource:['UniProt'],source:'UniPort', uniprot:'yes', license:'Creative Commons Attribution (CC BY 4.0) License', url:'https://www.uniprot.org/uniprot/'+line.uniprot_ids}]->(b);\n'''
    file_cypher.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_go/db_uniprots_to_cc.csv" As line MATCH (g:Protein{identifier:line.uniprot_ids}),(b:CellularComponent{identifier:line.go}) Create (g)-[:PARTICIPATES_PRpCC{resource:['UniProt'],source:'UniPort', uniprot:'yes', license:'Creative Commons Attribution (CC BY 4.0) License', url:'https://www.uniprot.org/uniprot/'+line.uniprot_ids}]->(b);\n'''
    file_cypher.write(query)
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_go/db_uniprots_to_mf.csv" As line MATCH (g:Protein{identifier:line.uniprot_ids}),(b:MolecularFunction{identifier:line.go}) Create (g)-[:PARTICIPATES_PRpMF{resource:['UniProt'],source:'UniPort', uniprot:'yes', license:'Creative Commons Attribution (CC BY 4.0) License', url:'https://www.uniprot.org/uniprot/'+line.uniprot_ids}]->(b);\n'''
    file_cypher.write(query)

    # generate a file with all uniprots to bc
    file_uniprots_bc = open('uniprot_go/db_uniprots_to_bc.csv', 'w')
    writer_uniprots_bc = csv.writer(file_uniprots_bc)
    writer_uniprots_bc.writerow(['uniprot_ids', 'go'])

    # generate a file with all uniprots to cc
    file_uniprots_cc = open('uniprot_go/db_uniprots_to_cc.csv', 'w')
    writer_uniprots_cc = csv.writer(file_uniprots_cc)
    writer_uniprots_cc.writerow(['uniprot_ids', 'go'])

    # generate a file with all uniprots to mf
    file_uniprots_mf = open('uniprot_go/db_uniprots_to_mf.csv', 'w')
    writer_uniprots_mf = csv.writer(file_uniprots_mf)
    writer_uniprots_mf.writerow(['uniprot_ids', 'go'])

    # query to get all Protein information {identifier:'P0DMV0'}
    query='''MATCH (n:Protein_Uniprot) RETURN n '''
    results=g.run(query)

    print(datetime.datetime.utcnow())
    #counter of combined gene protein interaction
    counter_existing_gene_protein_rela=0
    # counter all proteins
    counter_all_proteins=0

    #counter protein to gos
    counter_gos_bc=0
    counter_gos_cc = 0
    counter_gos_mf = 0

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/uniprot/db_uniprot_ids.csv" As line MATCH (p:Protein_Uniprot{identifier:line.uniprot_id}) Create (p)<-[:equal_to_uniprot]-(:Protein{'''

    #go through all Proteins
    # find overlap between protein and genes
    # maybe check out the go information to generate further relationships to go
    for node, in results:
        # add the different properties names to the query
        if counter_all_proteins==0:
            dict_node=dict(node)
            for property in dict_node.keys():
                # the go classifiers are in the rela to bc, cc and mf
                if property=='go_classifiers':
                    continue
                query+= property+':p.'+property+', '
            query+= 'uniprot:"yes", url:"https://www.uniprot.org/uniprot/"+p.identifier, source:"UniProt", resource:["UniProt"], license:"Creative Commons Attribution (CC BY 4.0) License "});\n '
            file_cypher_node.write(query)
            query = 'Create Constraint On (node:Protein) Assert node.identifier Is Unique;\n'
            file_cypher_node.write(query)

        counter_all_proteins+=1
        # get true if on of the uniprot of this nodes are in the dictionary uniprot to gene
        found_at_least_on=False

        # gather all uniprot ids which mapped to at least one gene
        overlap_uniprot_ids=set([])
        # gather all genes which mapped to all uniprots of this node
        set_list_mapped_genes=set([])

        # get the Uniprot id
        identifier= node['identifier']
        if identifier=='Q9Y2D5':
            print('ok')
        #write into integration file
        writer_uniprots_ids.writerow([identifier])

        # get the other uniprot ids
        second_uniprot_ids= node['second_ac_numbers'] if 'second_ac_numbers' in node else []
        second_uniprot_ids=list(set(second_uniprot_ids))
        # get the name of the node
        name= node['name']
        #get all xrefs of the node
        xrefs= node['xref'] if 'xref' in node else []

        # the gene symbol
        geneSymbols= node['gene_name'] if 'gene_name' in node else []
        geneSymbols= [x.split(' {')[0] for x in geneSymbols]

        # the gene ids
        gene_ids= node['gene_id'] if 'gene_id' in node else []

        #first check out the identifier
        # also check if it has multiple genes or not
        in_list,genes=check_and_write_uniprot_ids(identifier,name,identifier,'',geneSymbols,gene_ids)
        if in_list:
            found_at_least_on = True
            overlap_uniprot_ids.add(identifier)
            set_list_mapped_genes=set_list_mapped_genes.union(genes)

        #test the secondary ids if they are in dictionary uniprot to gene
        #also check if it has multiple genes or not
        for second_uniprot_id in second_uniprot_ids:
            # if second_uniprot_id=='P30042':
            #     print('huu')
            #     print(identifier)
            if second_uniprot_id == identifier:
                continue
            in_list, gene=check_and_write_uniprot_ids(second_uniprot_id, name, identifier, second_uniprot_id,geneSymbols,gene_ids)
            if in_list:
                found_at_least_on = True
                overlap_uniprot_ids.add(second_uniprot_id)
                set_list_mapped_genes=set_list_mapped_genes.union(genes)

        # if one mapped gene is found then count this and also if multiple genes mappes to multiple uniprots ids write this in a new file to check the manual
        if found_at_least_on:
            counter_existing_gene_protein_rela+=1
            if len(set_list_mapped_genes)>1 and len(overlap_uniprot_ids)>1:
                overlap_uniprot_ids=';'.join(overlap_uniprot_ids)
                set_list_mapped_genes=[str(x) for x in list(set_list_mapped_genes)]
                set_list_mapped_genes=';'.join(set_list_mapped_genes)
                writer_uniprots_genes.writerow([overlap_uniprot_ids,set_list_mapped_genes])

        # to find also relationships to biological processes, cellular component and moleculare functions
        for xref in xrefs:
            source_id=xref.split(':',1)
            if source_id[0]=='GO':
                if source_id[1] in dict_bp_to_name:
                    counter_gos_bc+=1
                    writer_uniprots_bc.writerow([identifier,source_id[1]])
                elif source_id[1] in dict_cc_to_name:
                    counter_gos_cc+=1
                    writer_uniprots_cc.writerow([identifier, source_id[1]])
                elif source_id[1] in dict_mf_to_name:
                    counter_gos_mf+=1
                    writer_uniprots_mf.writerow([identifier, source_id[1]])

    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/uniprot/uniprot_gene/db_gene_uniprot_delete.csv" As line Match (g:Gene{identifier:toInteger(line.gene_id)}) With g,FILTER(x IN g.uniProtIDs WHERE x <> line.uniprot_id) as filterdList 
                Set g.uniProtIDs=filterdList;\n '''
    file_cypher_node.write(query)
    print('number of existing gene protein rela:'+str(counter_existing_gene_protein_rela))
    print('number of all proteins:'+str(counter_all_proteins))
    print('rela to one of the bcs:'+str(counter_gos_bc))
    print('rela to one of the ccs:' + str(counter_gos_cc))
    print('rela to one of the mfs:' + str(counter_gos_mf))

def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the hetionet genes')

    get_all_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the hetionet Bp,CC and MF')

    load_bp_cc_mf_information()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the proteins')

    get_gather_protein_info_and_generate_relas()

    print('number of not matching gene names between protein and gene:'+str(count_not_mapping_gene_name))

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
