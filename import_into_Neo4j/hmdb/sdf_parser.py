import sys, csv
from zipfile import ZipFile

set_properties_sdf = set()
dict_header = []


def prepare_sdf_file(from_file_name):
    dict_all_nodes={}
    with ZipFile(from_file_name) as z:
        with z.open("structures.sdf") as file:
            dict_one_node_information = {}
            key = ''
            counter_entries = 0
            for line in file:
                line = line.decode('utf-8')
                if len(line.strip()) != 0:
                    if line.startswith("> "):
                        key = line.split('<')[1].split('>')[0]
                        set_properties_sdf.add(key)
                    elif line.strip() == "$$$$":
                        counter_entries += 1
                        dict_all_nodes[dict_one_node_information['DATABASE_ID']]=dict_one_node_information
                        dict_one_node_information = {}
                        key = ''
                    elif key != '':
                        if key in dict_one_node_information:
                            print(key)
                            print(dict_one_node_information)
                            sys.exit('multi line information')
                        dict_one_node_information[key] = line.strip()
    return dict_all_nodes
    print('number of entries', counter_entries)


#
# my_sdf_file = 'database/structures.zip'
#
#
# prepare_sdf_file(my_sdf_file)

