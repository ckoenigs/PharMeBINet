import xml.etree.ElementTree as ET
from collections import defaultdict
import os, sys


def mergedicts(x, y):
    z = x.copy()  # start with x's keys and values
    z.update(y)  # modifies z with y's keys and values & returns None
    return z


# def look_synonyms(dic,xml_dic):
#    i=0 
#   # print dic
#    for filename in xml_dic:
#        for name in xml_dic[filename]:
#           
#            if name in dic:
#                i+=1
#    print i
#    return xml_dic


def parse_CUI_line(l):
    e = l.split('|')
    ID = e[0]
    tmp = e[1].strip(']').split('[')
    synonym1 = tmp[0].split(',')

    cui = e[2]
    tmp1 = e[3].split('[')
    synonym2 = tmp1[0].split(',')

    synonym = set(synonym1).union(synonym2)
    return ID, {'synonym': synonym, 'cui': cui}


def CUI_to_dic(CUI):
    with open(CUI, 'r',encoding='utf-8') as c:
        dic = dict(parse_CUI_line(l) for l in c)
    return {e['cui']: ID for ID, e in dic.items()}


def get_asdic(root, dic, fIDName):
    as_dic = defaultdict(dict)

    with open(fIDName, 'a+', encoding='utf-8') as fID:
        fID.write('"ID","name","namespace"\n')
        for ass in root.iter('association'):
            filename = ass.find('name').text
            namespace = ass.find('namespace').text
            to_code = ass.find('to_code').text
            from_code = ass.find('from_code').text
            qual = ass.find('qualifier')
            qname = qual.find('name').text
            qnamespace = qual.find('namespace').text
            qvalue = qual.find('value').text

            if to_code[0] != 'N':
                if to_code in dic:
                    to_code = dic[to_code]

                else:
                    fID.write('"' + to_code + '","' + filename + '","' + namespace + '"\n')

            if from_code[0] != 'N':
                if from_code in dic:
                    from_code = dic[from_code]

                else:
                    fID.write('"' + from_code + '","' + filename + '","' + namespace + '"\n')

            as_dic[filename][(to_code, from_code)] = {'to_code': to_code, 'from_code': from_code,
                                                      'qualifier': (qname, qnamespace, qvalue)}

    return as_dic


def write_file(name, adf):
    with open(name, 'a+',encoding='utf-8') as f:
        f.write('"from_code","to_code","qualifier(name, namespace, value)"\n')
        for key, value in adf.items():
            f.write('"' + value['from_code'] + '","' + value['to_code'] + '","' + str(value['qualifier']) + '"\n')


def generate_xml_dic(dic, fIDName):
    path='data/Core_MEDRT_XML/'
    xml_files= [f for f in os.listdir(path) if f.endswith('.xml')]
    if len(xml_files)==1:
        file_name=xml_files[0]
    else:
        sys.exit('xmp not in path '+path)
    tree = ET.parse(path+file_name)
    root = tree.getroot()
    as_dic = get_asdic(root, dic, fIDName)

    for filenames in as_dic:
        write_file('output/' + filenames + '.csv', as_dic[filenames])

    xml_dic = defaultdict(dict)
    for con in root.iter('concept'):
        propertys = []
        synonyme = []
        namespace = con.find('namespace').text
        tmp = con.find('name').text.strip(']').split('[')
        if len(tmp) == 2:
            filename = tmp[1]

        else:
            filename = 'other'
        name = tmp[0]
        status = con.find('status').text
        code = con.find('code').text
        synonyms = con.findall('synonym')
        for s in synonyms:
            synonym = s.find('to_name').text
            if synonym not in synonyme:
                synonyme.append(synonym)
        prop = con.findall('property')
        for p in prop:
            pnamespace = p.find('namespace').text
            pname = p.find('name').text
            pvalue = p.find('value').text
            propertys.append((pnamespace, pname, pvalue))

        #        for e in concept:
        #
        #
        #                    tu
        #            if e.tag=='code':
        #                code=e.text
        #            if e.tag=='status':
        #                status=e.text
        #
        #            if e.tag == 'property':
        #
        #            if e.tag =='synonym':
        #                synonym=e.find('name').text
        #
        #
        xml_dic[filename][code] = {'status': status, 'namespace': namespace, 'name': name, 'propertys': propertys,
                                   'synonyme': synonyme}
    #
    return xml_dic


def write_xmlfiles(d):
    for filename, df in d.items():
        with open('output/' + filename + '.csv', 'a+', encoding='utf-8') as f:
            f.write('"ID","name","status","synonyme","propertys(namespace,name,value)"\n')
            for k, v in df.items():
                f.write('"' + k + '","' + v['name'] + '","' + v['status'] + '","')
                for i in v['synonyme']:
                    f.write('"' + i + '"')
                f.write(',')
                for i in v['propertys']:
                    f.write('"' + str(i) + '"')
                f.write('\n')


def main():
    # to avoid problems with data
    path='data/Core_MEDRT_Accessory_Files/'
    txt_files= [f for f in os.listdir(path) if 'DTS' not in f]
    for txt_file in txt_files:
        if 'mesh' in txt_file.lower():
            Mesh_CUI=path+txt_file
        elif 'rxnorm' in txt_file.lower():
            Rx_CUI=path+txt_file

    Mesh_map = CUI_to_dic(Mesh_CUI)
    Rx_map = CUI_to_dic(Rx_CUI)
    total_map = mergedicts(Mesh_map, Rx_map)

    xml_dic = generate_xml_dic(total_map, 'falseID.csv')
    # nicht nötig da kene N...IDs in den Dateien vorhanden
    # xml_dic= look_synonyms(Rx_dic,xml_dic)
    # xml_dic= look_synonyms(Mesh_dic,xml_dic)
    write_xmlfiles(xml_dic)


if __name__ == "__main__":
    # execute only if run as a script
    main()
