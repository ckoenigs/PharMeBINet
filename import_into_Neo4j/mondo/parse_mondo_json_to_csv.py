import sys
import datetime
import csv
import json

'''
prepare the id
'''
def prepare_id(iri):
    return iri.rsplit('/',1)[1].replace('_',':')

'''
open json file
'''
def open_json_file_write_into_csv():
    # open json file from mondo
    json_file=open('data/mondo.json','r')

    #the node csv file for generating disease nodes
    output_file= open('output/node_mondo.csv','w',encoding='utf-8')
    fieldnames = ['identifier', 'iri','definition','xrefs','synonyms','broad_synonyms','name','related_synonyms','narrow_synonyms']
    csv_output_node=csv.DictWriter(output_file,delimiter='\t', fieldnames=fieldnames)
    csv_output_node.writeheader()

    # generate cypher file
    cypher_file=open('cypher.cypher','w')
    query_start='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:'''+path_of_directory+'''master_database_change/import_into_Neo4j/mondo/%s" As line FIELDTERMINATOR '\\t' '''
    query_node=query_start+' Create (n:disease{'
    for fieldname in fieldnames:
        if fieldname in ['xrefs','synonyms','broad_synonyms','related_synonyms','narrow_synonyms']:
            query_node+= fieldname+':split(line.'+fieldname+',"||"), '
        else:
            query_node += fieldname + ':line.' + fieldname + ', '

    query_node=query_node+' license:"CC By 3.0"});\n'
    query_node= query_node %('output/node_mondo.csv')
    cypher_file.write(query_node)

    cypher_file.write(':begin \n')
    cypher_file.write('Create Constraint On (node:disease) Assert node.identifier Is Unique; \n')
    cypher_file.write(':commit \n')

    # load the content of the json file
    data= json.load(json_file)

    #relationships_files from the different relationship types
    dict_relationships_files={}

    # dictionary of iri to id
    dict_iri_to_id={}

    # has multiple graphs
    for x in data['graphs']:
        #go through all mondo nodes
        for node in x['nodes']:

            # dictionary which contains the file information
            dict_node={}

            # the id in mondo
            iri=node['id']

            #if this is not a mondo node do not use it
            if not 'http://purl.obolibrary.org/obo/MONDO' in iri:
                continue

            # get the usable identifier of mondo
            identifier= prepare_id(iri)

            # add information to dictionary
            dict_node['identifier']=identifier
            dict_node['iri']=iri

            # remember iri-identifier relationship
            dict_iri_to_id[iri]=identifier

            # some nodes even do not have a name
            dict_node['name']=node['lbl'] if 'lbl' in node else ''

            # the other mondo information which are lists (here set to avoid duplication
            xrefs=set()
            synonyms = set()
            broad_synonyms = set()
            related_synonyms = set()
            narrow_synonyms = set()
            # synonyms are all in the same content but to add the synonym to the right list this dictionary is for
            dict_synonyms = {
                'hasExactSynonym': synonyms,
                'hasBroadSynonym': broad_synonyms,
                'hasRelatedSynonym': related_synonyms,
                'hasNarrowSynonym': narrow_synonyms
            }
            # add meta date if existing
            if 'meta' in node:
                # check if they are not deprecated (veraltet)
                # if so they should not appear in Disease
                if 'deprecated' in node['meta']:
                    print('ok')
                    value=node['meta']['deprecated']
                    if value:
                        continue
                # definition
                dict_node['definition']=node['meta']['definition']['val'] if 'definition' in  node['meta'] else ''
                #external identifier
                if 'xrefs' in node['meta']:
                    for xref in node['meta']['xrefs']:
                        xrefs.add(xref['val'])
                dict_node['xrefs']='||'.join(xrefs)

                # synonyms
                if 'synonyms' in node['meta']:
                    for synonym in node['meta']['synonyms']:
                        dict_synonyms[synonym['pred']].add(synonym['val'])
                dict_node['synonyms']='||'.join(synonyms)
                dict_node['broad_synonyms'] = '||'.join(broad_synonyms)
                dict_node['related_synonyms'] = '||'.join(related_synonyms)
                dict_node['narrow_synonyms']='||'.join(narrow_synonyms)

            # write in csv file
            csv_output_node.writerow(dict_node)
        # generate edge query
        query_edge = query_start + ' Match (f:disease{identifier:line.from_id}), (t:disease{identifier:line.to_id}) Create (f)-[d:%s{license:"CC by 3.0"}]->(t);\n'
        fieldnames_rela = ['from_id', 'to_id']
        # go through all edges
        for edges in x['edges']:
            #child node
            from_node=edges['sub']
            # parent node
            to_node=edges['obj']
            # do avoid tho integrate relationships where one node is not a mondo node
            if not 'http://purl.obolibrary.org/obo/MONDO' in from_node or not 'http://purl.obolibrary.org/obo/MONDO' in to_node:
                continue

            # if relationship is not in dictionary generate a csv file for this relationship
            if not edges['pred'] in dict_relationships_files:
                # some relationships has a http name and this is not possible to be a file name
                rela_name_preparation=edges['pred'].replace('/','').replace(':','').replace('#','_')
                # generate filename
                filename='output/edge_mondo_%s.csv' %(rela_name_preparation)

                # prepare cypher file with edge relationships
                if "http" in edges['pred']:
                    query=query_edge %(filename, '`'+edges['pred']+'`')
                else:
                    query=query_edge %(filename, edges['pred'])
                cypher_file.write(query)

                # generate csv file and add headder
                output_rela_file = open(filename, 'w', encoding='utf-8')
                csv_output_rela = csv.writer(output_rela_file, delimiter='\t')
                csv_output_rela.writerow(fieldnames_rela)
                # add file to rela dictionary
                dict_relationships_files[edges['pred']]=csv_output_rela
            # add relationship to file
            dict_relationships_files[edges['pred']].writerow([prepare_id(from_node), prepare_id(to_node)])

    output_file.close()
    cypher_file.close()





def main():
    global path_of_directory
    # path to data for windows
    if len(sys.argv) ==2:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need path to project (mondo)')

    print('load json and prepare files')
    print (datetime.datetime.utcnow())

    open_json_file_write_into_csv()

    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()