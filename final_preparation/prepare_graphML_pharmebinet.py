# all node source to delete
import sys, datetime
import lxml.etree as ET

TODELETE = {'sider', 'ctd', 'ndfrt', 'aeolus', 'drugbank', 'ncbi', 'efo', 'hpo', 'uniprot', 'multi', 'go', 'dc',
            'diseaseontology', 'mondo', 'clinvar', 'omim', 'reactome', 'adrecstarget', 'iid', 'medrt', 'pharmgkb',
            'biogrid', 'dbsnp', 'hmdb', 'smpdb'}


# def
def check_source_info_in_label(label):
    is_ok_label = False
    if label[0].isupper():
        splitted = label.lower().split('_')
        if len(splitted) == 1:
            return True
        intersection = TODELETE.intersection(splitted)
        if len(intersection) == 0:
            print('has a _ but no source?')
            print(label)
            return True
        # elif len(intersection)>1:
        #     print(label)
        #     print('multiple _ but not a source?')
    return is_ok_label


ns = '{http://graphml.graphdrawing.org/xmlns}'

def add_atrributes(tree, attributs):
    for key,value in attributs.items():
        tree.attrib[key.replace(ns,'')]=value

# other_root = ET.Element('graphml', nsmap={None: 'http://graphml.graphdrawing.org/xmlns'})
# # add attributes
#
# added_graph = ET.SubElement(other_root, 'graph')


print(datetime.datetime.utcnow())
print('###########################################################################################################################################')

set_of_added_ids=set()
counter_all_nodes=0
counter_selected_node=0

counter_key=0


counter_all_edges=0
counter_selected_edge=0

file_name_from='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/wholedata.graphml'
# file_name_from='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/query.graphml'


def clear_attributes(text: str)->str:
    return text.replace('xmlns="http://graphml.graphdrawing.org/xmlns"', '').replace('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '').replace('  ', ' ').replace('  ', ' ')


filename = "/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/PharMeBiNet_finished.graphml"
with open(filename, 'w', encoding='utf-8') as xf:
    xf.write('<?xml version="1.0" encoding="utf-8"?>\n')
    xf.write('<graphml>\n')
    for event, node in ET.iterparse(file_name_from, encoding='utf-8', events=('end',)):
        if node.tag == ns + 'key':
            counter_key += 1
            xf.write('  ')
            xf.write(clear_attributes(ET.tostring(node, encoding='utf-8').decode('utf-8')))
        node.clear()
        # Stop at first node, as all keys are defined before
        if node.tag == ns + 'node':
            break

    print(datetime.datetime.utcnow())
    print('graph')
    print('###########################################################################################################')
    xf.write('  <graph id="G" todo="directed">\n')
    for event, node in ET.iterparse(file_name_from, encoding='utf-8', events=('end',)):
        if node.tag == ns + 'node':
            counter_all_nodes += 1
            labels_ok = False
            # print(tag,subchild.attrib)
            node_id = node.attrib['id']
            labels = node.attrib['labels']
            for label in labels.split(':')[1:]:
                is_ok_label = check_source_info_in_label(label)
                if is_ok_label:
                    labels_ok = True
            if labels_ok:
                counter_selected_node += 1
                set_of_added_ids.add(node_id)
                xf.write('     ')
                xf.write(clear_attributes(ET.tostring(node, encoding='utf-8').decode('utf-8')))
            if counter_all_nodes % 500_000 == 0 and counter_all_nodes > 0:
                print(datetime.datetime.utcnow())
                print('node', counter_all_nodes)
                xf.flush()
            node.clear()
        if node.tag == ns + 'edge':
            counter_all_edges += 1
            source = node.attrib['source']
            target = node.attrib['target']
            if source in set_of_added_ids and target in set_of_added_ids:
                counter_selected_edge += 1
                xf.write('     ')
                xf.write(clear_attributes(ET.tostring(node, encoding='utf-8').decode('utf-8')))
            if counter_all_edges % 1_000_000 == 0 and counter_all_edges > 0:
                print(datetime.datetime.utcnow())
                print('edges', counter_all_edges)
                xf.flush()
            node.clear()
    xf.write('  </graph>\n')
    xf.write('</graphml>\n')
print('from all nodes', counter_all_nodes, 'are real nodes', counter_selected_node)
print('from all edges', counter_all_edges, 'are real edges', counter_selected_edge)
# ET.ElementTree(other_root).write('/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/PharMeBiNet_finished.graphml')

print('finished xml parser')
print(datetime.datetime.utcnow())
print('###########################################################################################################################################')


sys.exit()


# TODELETE = {'sider', 'ctd', 'ndfrt', 'aeolus', 'drugbank', 'ncbi', 'efo', 'hpo', 'uniprot', 'multi', 'go', 'dc',
#             'diseaseontology', 'mondo', 'clinvar', 'omim', 'reactome', 'adrecstarget', 'iid', 'medrt', 'pharmgkb',
#             'biogrid', 'dbsnp', 'hmdb', 'smpdb'}
# # def
# def check_source_info_in_label(label):
#     is_ok_label=False
#     if label[0].isupper():
#         splitted = label.lower().split('_')
#         if len(splitted) == 1:
#             return True
#         intersection = TODELETE.intersection(splitted)
#         if len(intersection) == 0:
#             print('has a _ but no source?')
#             print(label)
#             return True
#         # elif len(intersection)>1:
#         #     print(label)
#         #     print('multiple _ but not a source?')
#     return is_ok_label
#
# file=open('/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/PharMeBiNet.graphml','r',encoding='utf-8')
# file_final=open('/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/PharMeBiNet_finished.graphml','w',encoding='utf-8')
#
# counter_nodes_all=0
# counter_nodes_add=0
# counter_edges_all=0
# counter_edges_added=0
# set_of_all_node_ids=set()
# is_ok_before=False
# is_edge=False
# for line in file:
#     splitted=line.split(' ')
#     if splitted[0].strip() in ['<?xml','<graphml','<key', '<graph','</graph>','</graphml>']:
#         file_final.write(line)
#     elif splitted[0]=='<node':
#         is_ok_before = False
#         counter_nodes_all+=1
#         # id="n0"
#         id_part=splitted[1].split('="')[1][:-1]
#         labels=splitted[2].split('"')[1]
#         labels_ok=False
#         for label in labels.split(':')[1:]:
#             is_ok_label=check_source_info_in_label(label)
#             if is_ok_label:
#                 labels_ok=True
#
#         if labels_ok:
#             is_ok_before = True
#             file_final.write(line)
#             set_of_all_node_ids.add(id_part)
#             counter_nodes_add += 1
#         else:
#             is_ok_before = False
#     elif (len(splitted[0])>0 and splitted[0][0]!='<') or len(splitted[0])==0:
#         if is_edge:
#             print(line)
#         if is_ok_before:
#             print('missing < or multiple line node?')
#             print(line)
#             file_final.write(line)
#             # sys.exit()
#
#     elif splitted[0]=='</data><data' and '</node' in line:
#
#         if is_ok_before:
#             print('weared <data>')
#             print(line)
#             file_final.write(line)
#             sys.exit()
#     elif splitted[0]=='<edge':
#         # sys.exit()
#
#         is_edge=True
#         counter_edges_all+=1
#         source=splitted[2].split('="')[1][:-1]
#         target = splitted[3].split('="')[1][:-1]
#         if source in set_of_all_node_ids and target in set_of_all_node_ids:
#             is_ok_before = True
#             counter_edges_added+=1
#             file_final.write(line)
#         # else:
#         #     is_ok_before = True
#             # print(line)
#             # sys.exit()
#     else:
#         print('start of creazy')
#         print(line)
#         print(splitted[0])
#         sys.exit()
#
#     if counter_nodes_all % 500000==0 and counter_nodes_all>0:
#         print(datetime.datetime.utcnow())
#         print('node',counter_nodes_all)
#
#     if counter_edges_all%1000000==0 and counter_edges_all>0:
#         print(datetime.datetime.utcnow())
#         print('edges', counter_edges_all)
#
#     # if counter_nodes_all % 8859764==0 and counter_nodes_all>0:
#     #     break
#
#     # if counter_edges_all % 1000==0 and counter_edges_all>0:
#     #     break
#
# print('from all nodes', counter_nodes_all, 'are real nodes', counter_nodes_add)
# print('from all edges', counter_edges_all, 'are real edges', counter_edges_added)

