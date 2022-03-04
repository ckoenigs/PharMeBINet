import sys, csv

set_properties_sdf = set()
dict_header = []


def prepare_sdf_file(from_file_name, to_file_name):
    from_file = open(from_file_name, 'r', encoding='utf-8')
    to_file = open(to_file_name, 'w', encoding='utf-8')

    to_csv = csv.DictWriter(to_file, fieldnames=dict_header, delimiter='\t')
    to_csv.writeheader()
    dict_one_node_information = {}
    key = ''
    counter_entries = 0
    for line in from_file:
        if len(line.strip()) != 0:
            if line.startswith("> "):
                key = line.split('<')[1].split('>')[0]
                set_properties_sdf.add(key)
            elif line.strip() == "$$$$":
                counter_entries += 1
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
    file = open(header_file_name, 'r', encoding='utf-8')
    reader = csv.reader(file, delimiter='\t')
    line = next(reader)
    dict_header.extend(line)


def generate_header_file(header_file_name, set_info):
    header_file = open(header_file_name, 'w', encoding='utf-8')
    header_tsv = csv.writer(header_file, delimiter='\t')
    header_tsv.writerow(list(set_info))
    header_file.close()


if len(sys.argv) != 3:
    sys.exit('This need as input a sdf file and an output file name as .tsv ')
my_sdf_file = sys.argv[1]
to_file = sys.argv[2]
name = to_file.rsplit('.', 1)[0]
header_file_name = name + '_header.tsv'
print(header_file_name)
exists_file = False
try:
    load_header_list(header_file_name)
    exists_file = True
except:
    print('header file not existing')

prepare_sdf_file(my_sdf_file, to_file)

if not exists_file:
    # prepare a header file
    generate_header_file(header_file_name, sorted(set_properties_sdf))
    dict_header.extend(sorted(set_properties_sdf))
    # generate file with header now
    prepare_sdf_file(my_sdf_file, to_file)
