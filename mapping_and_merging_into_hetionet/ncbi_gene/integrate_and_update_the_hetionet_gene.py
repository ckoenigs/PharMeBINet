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


# dictionary with all gene ids to there name
dict_hetionet_gene_ids_to_name = {}

'''
load all ncbi identifier from the gene ides into a dictionary (or list)
'''


def get_all_ncbi_ids_form_hetionet_genes():
    query = '''Match (g:Gene) Return g;'''
    results = g.run(query)
    for node, in results:
        identifier = node['identifier']

        dict_hetionet_gene_ids_to_name[identifier] = dict(node)

    print('number of genes in hetionet:' + str(len(dict_hetionet_gene_ids_to_name)))


# ditionary from ncbi property to hetionet property name
dict_ncbi_property_to_hetionet_property = {
    "Full_name_from_nomenclature_authority": 'name',
    "Symbol": 'geneSymbol',
    "Symbol_from_nomenclature_authority": 'geneSymbol',
    "Synonyms": 'synonyms',
    "dbXrefs": 'xrefs'
}

dict_hetionet_property_to_ncbi_property = dict(map(reversed, dict_ncbi_property_to_hetionet_property.items()))

# list of properties  which have a list element
list_properties_with_list_elements = ['geneSymbol', 'synonyms', 'xrefs', 'map_location', 'Feature_type']

# list of found gene ids, because i think not all gene ids from hetionet exists anymore
found_gene_ids = []


def add_value_into_dict_with_list_or_not(dict_insert, head, question_header, dict_with_values):
    # gene Symobole sind keine Liste, muss noch geaendert werden und Feature_type ist leer
    if question_header in dict_with_values:
        if head in list_properties_with_list_elements:
            dict_insert[head] = '|'.join(dict_with_values[question_header])
        else:
            dict_insert[head] = dict_with_values[question_header]


'''
load ncbi tsv file in and write only the important lines into a new csv file for integration into Neo4j
'''


def load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes():
    # file for integration into hetionet
    file = open('output_data/genes_merge.csv', 'w')
    header = ['identifier', 'name', 'description', 'chromosome', 'geneSymbol', 'synonyms', 'Feature_type',
              'type_of_gene', 'map_location', 'xrefs']
    writer = csv.DictWriter(file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL,
                            fieldnames=header)
    writer.writeheader()

    cypher_file = open('cypher_merge.cypher', 'w')
    query = '''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:/home/cassandra/Dokumente/Project/master_database_change/mapping_and_merging_into_hetionet/ncbi_gene/output_data/genes_merge.csv" As line Fieldterminator '\\t' Match (n:Gene_Ncbi {identifier:line.identifier}) Merge (g:Gene{identifier:toInteger(line.identifier) }) On Match Set '''

    on_create_string = ''' On Create SET '''
    for head in header:
        if head != 'identifier':
            part = 'g.' + head.lower() + '='
            if head in list_properties_with_list_elements:
                part += 'split(line.' + head + ',"|"), '
            else:
                part += 'line.' + head + ', '
            query += part
            on_create_string += part

    query += 'g.ncbi="yes", g.resource=g.resource+"NCBI" ' + on_create_string + ''' g.ctd="no", g.hetionet="no", g.source="Entrez Gene", g.resource="NCBI", g.license="CC0 1.0", g.url="http://identifiers.org/ncbigene/"+line.identifier, g.ncbi='yes', g.resource=['NCBI'] Create (n)<-[:equal_to_ncbi_gene]-(g);\n'''
    cypher_file.write(query)
    query='''MATCH (a:Gene) Where not  (a)-[:equal_to_ncbi_gene]->() Detach Delete a;'''
    cypher_file.write(query)
    cypher_file.close()

    query = '''MATCH (n:Gene_Ncbi) RETURN n.identifier, n.Full_name_from_nomenclature_authority, n;'''
    results = g.run(query)
    counter_not_same_name = 0
    counter_all = 0
    counter_all_in_hetionet = 0
    for gene_id, name, node, in results:
        counter_all += 1
        # make a dictionary from the node
        node = dict(node)
        # generate on list of gene symbols
        gene_symbol = set([])

        # remove the empty values '-' and combine the list of other designations and symbols, and symbol_from-Nomeclature_authority and symbol
        for property, value in node.items():

            if type(value) == list:
                list_of_values = []
                for value_part in value:
                    if value_part != '-':
                        list_of_values.append(value_part)
                node[property] = list_of_values
            else:
                if value == '-':
                    node[property] = ''

            if property == 'Other_designations' and len(list_of_values) != 0:
                node['Synonyms'].extend(value)
            elif property == 'Symbol_from_nomenclature_authority' and value != '-':
                gene_symbol.add(value)
            elif property == 'Symbol' and value != '-':
                gene_symbol.add(value)

        # make one list
        node['Symbol_from_nomenclature_authority'] = list(gene_symbol)
        node['Symbol'] = list(gene_symbol)
        symbols_ncbi=[x.lower() for x in list(gene_symbol)]
        synonyms= node['Synonyms'] if 'Synonyms' in node else []
        synonyms =[x.lower() for x in synonyms]


        if int(gene_id) in dict_hetionet_gene_ids_to_name:
            counter_all_in_hetionet += 1
            if 'name' in dict_hetionet_gene_ids_to_name[int(gene_id)]:
                if gene_id=='26083':
                    print('ok')
                name=name.lower()
                hetionet_gene_name=dict_hetionet_gene_ids_to_name[int(gene_id)]['name'].lower()
                description=node['description'].lower()
                hetionet_gene_description=dict_hetionet_gene_ids_to_name[int(gene_id)]['description'].lower()
                if not name == hetionet_gene_name:
                    if name == '-':
                        print('has no name')
                        if node['description']=='-':
                            print('description is also empty')
                        node['Full_name_from_nomenclature_authority'] = node['description']

                    if description == hetionet_gene_name:

                        print(gene_id)
                        print(node['description'])
                        print(' are same description')
                    elif hetionet_gene_description == name:
                        print(gene_id)
                        print('hetionet description match ncbi name')
                    elif hetionet_gene_description==description:
                        print(gene_id)
                        print('equal description')
                    elif len(synonyms)>0 and hetionet_gene_name in synonyms:
                        print(gene_id)
                        print('equal to synonyms')
                    elif len(symbols_ncbi)>0 and hetionet_gene_name in symbols_ncbi:
                        print(gene_id)
                        print('equal to gene symbol')
                    else:
                        counter_not_same_name += 1
                        print(gene_id)
                        print(name)
                        print(dict_hetionet_gene_ids_to_name[int(gene_id)]['name'])
                        # print(node)
                        print('kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')

                else:
                    print(gene_id)
                    print('has same name')

            else:
                counter_not_same_name += 1
                print(gene_id)
                print(name)
                print(dict_hetionet_gene_ids_to_name[int(gene_id)])
                node['Full_name_from_nomenclature_authority']=list(gene_symbol)[0]
                print('nonamenonamenonamenonamenonamenonamenonamenonamenonamenonamenoname')

            if 'chromosome' in dict_hetionet_gene_ids_to_name[int(gene_id)] and 'chromosome' in node:
                chromosome_hetionet = dict_hetionet_gene_ids_to_name[int(gene_id)]['chromosome']
                if chromosome_hetionet != node['chromosome'] and chromosome_hetionet != '':
                    print('chromosome ;(')
                    print(dict_hetionet_gene_ids_to_name[int(gene_id)]['chromosome'])
                    print(node['chromosome'])
                    print(gene_id)
                    # sys.exit(gene_id)

            dict_for_insert_into_tsv = {}
            for head in header:
                if head in dict_hetionet_property_to_ncbi_property:
                    add_value_into_dict_with_list_or_not(dict_for_insert_into_tsv, head,
                                                         dict_hetionet_property_to_ncbi_property[head], node)

                else:
                    if head in node:
                        add_value_into_dict_with_list_or_not(dict_for_insert_into_tsv, head,
                                                             head, node)
            writer.writerow(dict_for_insert_into_tsv)

        else:
            print('not in hetionet')
            print(gene_id)
            if name == '-':
                node['Full_name_from_nomenclature_authority'] = node['description']

            dict_for_insert_into_tsv = {}
            for head in header:
                if head in dict_hetionet_property_to_ncbi_property:
                    add_value_into_dict_with_list_or_not(dict_for_insert_into_tsv, head,
                                                         dict_hetionet_property_to_ncbi_property[head], node)

                else:
                    if head in node:
                        add_value_into_dict_with_list_or_not(dict_for_insert_into_tsv, head,
                                                             head, node)
            writer.writerow(dict_for_insert_into_tsv)
    print('number of all genes:' + str(counter_all))
    print('counter of all genes already in hetionet:' + str(counter_all_in_hetionet))
    print('counter not the same name:' + str(counter_not_same_name))


def main():
    print(datetime.datetime.utcnow())
    print('create connection with neo4j')

    create_connetion_with_neo4j()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gather all information of the hetionet genes')

    get_all_ncbi_ids_form_hetionet_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())
    print('gnerate a tsv file with only the hetionet genes')

    load_tsv_ncbi_infos_and_generate_new_file_with_only_the_important_genes()

    print(
        '#################################################################################################################################################################')

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
