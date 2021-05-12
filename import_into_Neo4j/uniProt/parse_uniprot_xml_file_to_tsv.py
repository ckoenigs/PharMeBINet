import os
import csv
import datetime
import sys
import lxml.etree as etree

ns = '{http://uniprot.org/uniprot}'


# dictionary keywords
dict_keyword = {}

# set of keyword_id and protein id
set_keyword_protein_pairs = set()

# set evidence
set_evidence = set()

# dict of evidence and protein id
dict_evidence_protein_pairs_to_info = {}


def combine_xrefs(attributes):
    """
    combine source and id to one string
    :param attributes: kind of dict
    :return:
    """
    return attributes['type'] + ':' + attributes['id']


def prepare_dbReference(dict_protein, attributes):
    """
    add refference to dictionary
    :param dict_protein:
    :param attributes:
    :return:
    """
    if not 'xrefs' in dict_protein:
        dict_protein['xrefs'] = set()
    dict_protein['xrefs'].add(combine_xrefs(attributes))
    evidence= attributes['evidence'] if 'evidence' in attributes else ''


def prepare_evidence(attrib, protein_id, parent=None):
    """
    Prepare evidence nodes and relationships. Some contains relationship information
    :param attrib: kind of dict
    :param protein_id: string
    :param parent: a xml node
    :return:
    """
    evidence_id = attrib['type']
    set_evidence.add(evidence_id)
    if not (evidence_id, protein_id) in dict_evidence_protein_pairs_to_info:
        dict_evidence_protein_pairs_to_info[(evidence_id, protein_id)] = {}
    if parent is not None:
        for child in parent.iterchildren():
            tag = child.tag.replace(ns, '')
            if tag not in dict_evidence_protein_pairs_to_info[(evidence_id, protein_id)]:
                dict_evidence_protein_pairs_to_info[(evidence_id, protein_id)][tag] = set()
            for dbRefs in child.iterchildren():
                db_ref_tag = dbRefs.tag.replace(ns, '')
                if db_ref_tag != 'dbReference':
                    sys.exit('evidence has not df Ref')
                dict_evidence_protein_pairs_to_info[(evidence_id, protein_id)][tag].add(combine_xrefs(dbRefs.attrib))

def preparation_gene_location(dictionary, attributes, node=None):
    """
    Prepare the gene location information into a list of strings.
    :param dictionary: dictionary
    :param attributes: kind of dict
    :param node: xml node
    :return:
    """
    if 'gene_location' not in dictionary:
        dictionary['gene_location']=set()
    type = attributes['type']
    evidence= attributes['evidence'] if 'evidence' in attributes else ''

    list_of_names=[]
    if node is not None:
        for child in node.iterchildren():
            child_att=child.attrib
            name=''
            if 'status' in child_att:
                name+=child_att['status']
            name+= ' '+ child.text
            list_of_names.append(name.strip())
    type += ' '+'; '.join(list_of_names)
    dictionary['gene_location'].append(type.strip())

def add_name_or_ec_to_list_from_protein(node,dict_protein):
    """
    Add the name to the list of names and the ec to a ec-list.
    :param node: xml leaf
    :param dict_protein: dictionary
    :return:
    """
    subsub_tag = node.tag.replace(ns, '')
    evidence_protein_name = node.attrib['evidence'] if 'evidence' in node else ''
    if subsub_tag != 'ecNumber':
        dict_protein['protein_name'].append(node.text)
    else:
        dict_protein['ec_number'].add(node.text)

def add_key_value_to_dictionary_as_list(dictionary, key, value):
    """
    Add a key value pair into a dictionary with a list.
    :param dictionary: dictionary
    :param key:  string
    :param value: string
    :return:
    """
    if key not in dictionary:
        dictionary[key]=[]
    dictionary[key].append(value)



def run_trough_xml_and_parse_data():
    # counter of human entries
    counter_human = 0

    # open xml file
    file = open('test.xml', 'rb')
    # go through the entries in uniprot xml
    for event, node in etree.iterparse(file, events=('end',), tag="{ns}entry".format(ns=ns)):

        # check if this is a human entry
        organism = node.find("{ns}organism".format(ns=ns))
        df_references = organism.findall("{ns}dbReference".format(ns=ns))

        has_ncbi_tax_id = False
        is_human = False
        for df_ref in df_references:
            df_ref_attributes = df_ref.attrib
            if "NCBI Taxonomy" == df_ref_attributes["type"]:
                has_ncbi_tax_id = True
                if df_ref_attributes["id"] == '9606':
                    is_human = True

        # check if at least one one ncbi tax entry
        if not has_ncbi_tax_id:
            sys.exit("a protein without a organism with ncbi tax")
        #  continue if it is not a human
        if not is_human:
            node.clear()
            continue

        counter_human += 1

        # dictionary of protein information
        dict_protein = {}

        # the identifier
        identifier = ''

        for child in node.iterchildren():

            tag = child.tag.replace(ns, '')
            # the attributes
            attributes = child.attrib

            if len(child):
                # print('has child')
                # print("%s - %s - %s" % (tag, child.text, child.attrib))
                # prepare the dbRefs with child to xrefs and into xrefs with additional info
                if tag == 'dbReference':
                    prepare_dbReference(dict_protein, attributes)
                    dict_xref = {'id': attributes['type'] + ':' + attributes['id']}
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag == 'property':
                            dict_xref[subchild.attrib['type']] = subchild.attrib['value']
                        else:
                            # print(dict_protein)
                            # print("%s - %s - %s" % (sub_tag, subchild.text, subchild.attrib))
                            dict_xref[sub_tag+'_id']= subchild.attrib['id']
                            if subchild.text is not None:
                                sys.exit('molecule dbRef has text')
                            # print("molecular in dbRef")

                    if 'xrefs_with_infos' not in dict_protein:
                        dict_protein['xrefs_with_infos'] = []
                    dict_protein['xrefs_with_infos'].append(dict_xref)
                # evidence of the protein
                elif tag == 'evidence':
                    prepare_evidence(attributes, identifier, child)
                # different kind of features like mutation version/ regions/...
                elif tag == 'feature':
                    if tag not in dict_protein:
                        dict_protein[tag] = []
                    dict_feature = dict(attributes)
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag == 'original':
                            dict_feature[sub_tag] = subchild.text
                        elif sub_tag == 'variation':
                            add_key_value_to_dictionary_as_list(dict_feature,sub_tag, subchild.text)
                        else:
                            if len(subchild.attrib) > 0:
                                for key, value in dict(subchild.attrib).items():
                                    dict_feature[key]=value
                            for subsubchild in subchild.iterchildren():
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                text = ''
                                subsubchild_attributes = subsubchild.attrib
                                if 'status' in subsubchild_attributes:
                                    text += subsubchild_attributes['status']
                                if 'position' in subsubchild_attributes:
                                    text += ' ' + subsubchild_attributes['position']
                                subsubchild_evidence = subsubchild_attributes[
                                    'evidence'] if 'evidence' in subsubchild_attributes else ''

                                dict_feature[subsub_tag] = text.strip()
                    dict_protein[tag].append(dict_feature)
                # name of the gene
                elif tag == 'gene':
                    if 'gene_name' not in dict_protein:
                        dict_protein['gene_name'] = set()
                    for subchild in child.iterchildren():
                        subchild_type = subchild.attrib['type']
                        subchild_evidence = subchild.attrib['evidence'] if 'evidence' in subchild.attrib else ''
                        dict_protein['gene_name'].add(subchild_type + ':' + subchild.text)
                # location of the gene
                elif tag=='geneLocation':
                    preparation_gene_location(dict_protein,attributes,child)

                # is already human
                elif tag =='organism':
                    continue
                # protein contains name and ec-codes
                elif tag =='protein':
                    dict_protein['protein_name']=[]
                    dict_protein['ec_number']=set()
                    for subchild in child.iterchildren():
                        for subsubchild in subchild.iterchildren():
                            # fullname/alternativeName/submittedName/allergenName/biotechName/cdAntigenName/innName
                            if not len(subsubchild):
                                add_name_or_ec_to_list_from_protein(subsubchild,dict_protein)
                            # domain/component with the infos from before
                            else:
                                for subsubsubchild in subsubchild.iterchildren():
                                    add_name_or_ec_to_list_from_protein(subsubsubchild, dict_protein)

                elif tag=='reference':
                    if not 'references' in dict_protein:
                        dict_protein['references']=[]
                    dict_ref={}
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag!='citation':
                            # source
                            if len(subchild):
                               for subsubchild in subchild.iterchildren():
                                   subsub_tag = subsubchild.tag.replace(ns, '')
                                   add_key_value_to_dictionary_as_list(dict_ref, subsub_tag, subsubchild.text)
                                   evidence_citation_group= subsubchild.attrib['evidence'] if 'evidence' in subsubchild.attrib else ''
                            # scope
                            else:
                                add_key_value_to_dictionary_as_list(dict_ref,sub_tag,subchild.text)
                        # citation
                        else:
                            subchild_attributes=dict(subchild.attrib)
                            dict_ref.update(subchild_attributes)
                            for subsubchild in subchild.iterchildren():
                                subsub_tag = subsubchild.tag.replace(ns, '')
                                if not len(subsubchild) and subsub_tag!='dbReference':
                                    dict_ref[subsub_tag]=subsubchild.text
                                elif subsub_tag=='dbReference':
                                    subsub_att=subsubchild.attrib
                                    prepare_dbReference(dict_ref, subsub_att)
                                    if len(subsubchild):
                                        sys.exit('ref dbref has child nodes!')
                                # editorList/authorList
                                else:
                                    subsub_tag=subsub_tag.replace('List','')+'s'
                                    dict_ref[subsub_tag]=[]
                                    for subsubsubchild in subsubchild.iterchildren():
                                        dict_ref[subsub_tag].append(subsubsubchild.attrib['name'])


                elif tag=='comment':
                    dict_comment={}
                    for subchild in child.iterchildren():
                        sub_tag = subchild.tag.replace(ns, '')
                        if sub_tag=='molecule':
                            dict_comment[sub_tag]=subchild.text
                else:
                    print("%s - %s - %s" % (tag, child.text, child.attrib))
            else:
                if tag in ["accession", "name"]:
                    if tag not in dict_protein:
                        dict_protein[tag] = []
                        # get the node identifier
                        if tag == 'accession':
                            dict_protein['identifier'] = child.text
                            identifier = child.text
                            continue
                    dict_protein[tag].append(child.text)
                # sequence information
                elif tag == 'sequence':
                    dict_protein["as_sequence"] = child.text
                    dict_protein['sequenceLength'] = attributes['length']
                    dict_protein['mass'] = attributes['mass']
                    if 'fragment' in attributes:
                        print(dict_protein)
                        print('has fragment in seq')
                        sys.exit('seq fragment')
                # reference information
                elif tag == 'dbReference':
                    prepare_dbReference(dict_protein, attributes)
                # kind of existence of the protein
                elif tag == 'proteinExistence':
                    dict_protein['protein_existence'] = attributes['type']
                # classification of the protein
                elif tag == 'keyword':
                    keyword_id = attributes['id']
                    if keyword_id not in dict_keyword:
                        dict_keyword[keyword_id] = child.text
                    evidence_keyword= attributes['evidence'] if 'evidence' in attributes else ''
                    set_keyword_protein_pairs.add((keyword_id, identifier))
                # evidence of the protein
                elif tag == 'evidence':
                    prepare_evidence(attributes, identifier)
                # location of the gene
                elif tag=='geneLocation':
                    preparation_gene_location(dict_protein,attributes)

                # else:
                #     print('not')
                #     print("%s - %s - %s" % (tag, child.text, child.attrib))
        # print(dict_protein)

        node.clear()
    print("number of human proteins:", counter_human)


def main():


    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('parse xml data ')

    run_trough_xml_and_parse_data()

    print('#############################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
