import sys, csv

set_properties_sdf = set()
dict_header = []

def prepare_sdf_file(from_file_name, to_file_name):
    from_file = open(from_file_name, 'r', encoding='utf-8')
    to_file = open(to_file_name, 'w', encoding='utf-8')

    to_csv=csv.DictWriter(to_file,fieldnames=dict_header)
    to_csv.writeheader()
    dict_one_node_information = {}
    key = ''
    counter_entries=0
    for line in from_file:
        if len(line.strip()) != 0:
            if line.startswith("> "):
                key = line.split('<')[1].split('>')[0]
                set_properties_sdf.add(key)
            elif line.strip() == "$$$$":
                counter_entries+=1
                try:
                    to_csv.writerow(dict_one_node_information)
                except:
                    print('no header')
                dict_one_node_information = {}
                key = ''
            elif key != '':
                if key in dict_one_node_information:
                    print(key)
                    print(dict_one_node_information)
                    sys.exit('multi line information')
                dict_one_node_information[key] = line.strip()

    print('number of entries', counter_entries)

def load_header_list(header_file_name):
    file= open(header_file_name,'r',encoding='utf-8')
    line=file.readline()
    dict_header.extend(line.split(','))

def generate_header_file(header_file_name, string):

    header_file=open(header_file_name,'w',encoding='utf-8')
    header_file.write(string)

if len(sys.argv) != 3:
    sys.exit('This need as input a sdf file and an output file name as .csv ')
my_sdf_file = sys.argv[1]
to_file = sys.argv[2]
name=to_file.rsplit('.',1)[0]
header_file_name=name+'_header.txt'
try:
    load_header_list(header_file_name)
except:
    print('header file not existing')

prepare_sdf_file(my_sdf_file, to_file)


print(",".join(sorted(set_properties_sdf)))
generate_header_file(header_file_name,",".join(sorted(set_properties_sdf)))