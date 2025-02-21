# all node source to delete
import sys, datetime
import lxml.etree as ET

# dc = drugcentral
TODELETE = {'adrecs', 'adrecstarget', 'aeolus', 'atc', 'biogrid', 'bindingdb', 'chebiontology', 'clinvar', 'ctd', 'co',
            'dbsnp', 'dc', 'ddinter', 'diseases', 'disgenet', 'diseaseontology', 'drugbank', 'fideo', 'foodb', 'foodon',
            'efo', 'gencc', 'go', 'gwas', 'gwascatalog', 'hetionet', 'hgnc', 'hippie', 'hmdb', 'hpo', 'iid', 'iptmnet', 'markerdb',
            'medrt', 'mirbase', 'mondo', 'ncbi', 'ndfrt', 'multi', 'omim', 'openfda', 'pharmgkb', 'ptmd', 'qptm',
            'reactome', 'refseq', 'rnacentral', 'rnadisease', 'rnainter', 'sider', 'smpdb', 'ttd', 'uberon', 'uniprot'}


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
    for key, value in attributs.items():
        tree.attrib[key.replace(ns, '')] = value


# other_root = ET.Element('graphml', nsmap={None: 'http://graphml.graphdrawing.org/xmlns'})
# # add attributes
#
# added_graph = ET.SubElement(other_root, 'graph')


print(datetime.datetime.now())
print(
    '###########################################################################################################################################')

set_of_added_ids = set()
counter_all_nodes = 0
counter_selected_node = 0

counter_key = 0

counter_all_edges = 0
counter_selected_edge = 0

path_start='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/'
if len(sys.argv) > 1:
    path_start=sys.argv[1]

file_name_from = path_start+'wholedata.graphml'


# file_name_from='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/query.graphml'


def clear_attributes(text: str) -> str:
    return text.replace('xmlns="http://graphml.graphdrawing.org/xmlns"', '').replace(
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"', '').replace('  ', ' ').replace('  ', ' ')


filename = path_start+ "PharMeBiNet_finished.graphml"
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

    print(datetime.datetime.now())
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
                print(datetime.datetime.now())
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
                print(datetime.datetime.now())
                print('edges', counter_all_edges)
                xf.flush()
            node.clear()
    xf.write('  </graph>\n')
    xf.write('</graphml>\n')
print('from all nodes', counter_all_nodes, 'are real nodes', counter_selected_node)
print('from all edges', counter_all_edges, 'are real edges', counter_selected_edge)
# ET.ElementTree(other_root).write('/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/PharMeBiNet/PharMeBiNet_finished.graphml')

print('finished xml parser')
print(datetime.datetime.now())
print(
    '###########################################################################################################################################')
