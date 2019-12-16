import sys
import datetime
import csv
import json

'''
open json file
'''
def open_json_file_write_into_csv():
    json_file=open('data/mondo.json','r')
    output_file= open('output/node_mondo.csv','w',encoding='utf-8')
    fieldnames = ['identifier', 'iri','definition','xrefs','synonyms','broad_synonyms','name','related_synonyms','narrow_synonyms']
    csv_output_node=csv.DictWriter(output_file,delimiter='\t', fieldnames=fieldnames)
    csv_output_node.writeheader()
    data= json.load(json_file)

    # dictionary of iri to id
    dict_iri_to_id={}

    # has multiple graphs
    for x in data['graphs']:
        #go through all mondo nodes
        for node in x['nodes']:
            if len(node)==1:
                print(node)
                sys.exit('node with more properties')
            dict_node={}
            iri=node['id']
            if not 'http://purl.obolibrary.org/obo/MONDO' in iri:
                continue
            identifier= iri.rsplit('/',1)[1].replace('_',':')
            dict_node['identifier']=identifier
            dict_node['iri']=iri
            dict_iri_to_id[iri]=identifier
            # some nodes even do not have a name
            dict_node['name']=node['lbl'] if 'lbl' in node else ''
            xrefs=set()
            synonyms = set()
            broad_synonyms = set()
            related_synonyms = set()
            narrow_synonyms = set()
            dict_synonyms = {
                'hasExactSynonym': synonyms,
                'hasBroadSynonym': broad_synonyms,
                'hasRelatedSynonym': related_synonyms,
                'hasNarrowSynonym': narrow_synonyms
            }
            # add meta date if existing
            if 'meta' in node:
                dict_node['definition']=node['meta']['definition']['val'] if 'definition' in  node['meta'] else ''
                if 'xrefs' in node['meta']:
                    for xref in node['meta']['xrefs']:
                        xrefs.add(xref['val'])
                dict_node['xrefs']='||'.join(xrefs)

                if 'synonyms' in node['meta']:
                    for synonym in node['meta']['synonyms']:
                        dict_synonyms[synonym['pred']].add(synonym['val'])
                dict_node['synonyms']='||'.join(synonyms)
                dict_node['broad_synonyms'] = '||'.join(broad_synonyms)
                dict_node['related_synonyms'] = '||'.join(related_synonyms)
                dict_node['narrow_synonyms']='||'.join(narrow_synonyms)

            # write in csv file
            csv_output_node.writerow(dict_node)
        set_of_edges_types=set()
        # go through all edges
        for edges in x['edges']:

            for_node=edges['sub']
            to_node=edges['obj']
            if not 'http://purl.obolibrary.org/obo/MONDO' in for_node and not 'http://purl.obolibrary.org/obo/MONDO' in to_node:
                continue
            set_of_edges_types.add(edges['pred'])
        print(set_of_edges_types)





def main():


    print('start load in concept ')
    print (datetime.datetime.utcnow())

    open_json_file_write_into_csv()

    print("start drug outcome statistic ")
    print (datetime.datetime.utcnow())

    print('create csv and cypher file to integrate aeolus int neo4j')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()