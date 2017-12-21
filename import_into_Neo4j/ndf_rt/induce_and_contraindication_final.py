# -*- coding: utf-8 -*-
"""
Created on Fri Jul 14 10:34:41 2017

@author: Cassandra
"""

import xml.dom.minidom as dom

import datetime


# all different kinds has the same form, so both drug and disease can defind as on class
class Concept(object):
    """
     Attribute:
         name: string
         code : string  (id that is used for relationships)
         ndf_rt_id : string (only intern used)
         properties : list of strings (like synonyms or other ids)
         association: list of string ( can be: Product component, heading mapped to, PharmClass Member)
    """

    def __init__(self, name, code, ndf_rt_id, properties, association):
        self.name = name
        self.code = code
        self.ndf_rt_id = ndf_rt_id
        self.properties = ','.join(properties)
        self.association = ','.join(association)


# dictionary of all properties with code as key and the name as value, because in the other concepts only the 
# concept id of the property and the value appears
dict_properties_code_to_name = {}

# dictionary of all qualifiers with code as key and the name as valueConcept , because in the other concepts only the 
# concept id of the qualifier and the value appears
dict_qualifiers_concept_to_name = {}

# dictionary of all association with code as key and the name as value, because in the other concepts only the 
# concept id of the association and the value appears
dict_associations_concept_to_name = {}

# list of tupels which build a contraindication where the first valus is the drug and the second is disease 
# (with role 'CI_with {NDFRT}')
list_contraindication = []

# list of tupels where the first valus is the drug and induce the second is disease (with role 'induces {NDFRT}')
list_induces = []

# dictionary of all drugs from ndf-rt that has a relation 'CI_with {NDFRT}' or 
# 'induces {NDFRT}', where code is the key and the value is a concept
dict_drugs = {}

# dictionary of all diseases from ndf-rt, where code is the key and the value is a concept
dict_diseases = {}

# list of codes of disease which are in a relation 'CI_with {NDFRT}' or 'induces {NDFRT}'
list_disease = []

'''
go through the ndf-rt xml file and gather all important information in dictionaries or lists.
'''
def load_ndf_rt_xml_inferred_in():
    print (datetime.datetime.utcnow())
    tree = dom.parse("NDF-RT_XML_Inferred/NDFRT_Public_2017.06.05/NDFRT_Public_2017.06.05_TDE_inferred.xml")
    print (datetime.datetime.utcnow())

    terminology = tree.documentElement
    properties = terminology.getElementsByTagName('propertyDef')

    # save for all properties the code and name in a dictionary
    for prop in properties:
        name = prop.getElementsByTagName('name')[0].childNodes[0].nodeValue
        code = prop.getElementsByTagName('code')[0].childNodes[0].nodeValue
        dict_properties_code_to_name[code] = name

    # save all qualifier in a dictionary with code and name
    qualifiers = terminology.getElementsByTagName('qualifierDef')
    for qualifier in qualifiers:
        name = qualifier.getElementsByTagName('name')[0].childNodes[0].nodeValue
        code = qualifier.getElementsByTagName('code')[0].childNodes[0].nodeValue
        dict_qualifiers_concept_to_name[code] = name

    # save all association in a dictionary
    associations = terminology.getElementsByTagName('associationDef')
    for association in associations:
        name = association.getElementsByTagName('name')[0].childNodes[0].nodeValue
        code = association.getElementsByTagName('code')[0].childNodes[0].nodeValue
        dict_associations_concept_to_name[code] = name

    # get all important concepts                      
    concepts = terminology.getElementsByTagName('conceptInf')
    for concept in concepts:

        # test if it is a drug
        if concept.getElementsByTagName('kind')[0].childNodes[0].nodeValue == 'C8':
            # boolean which shows if a drug has a relationship iduce and/or contraindicate
            has_a_interesting_rela = False

            name = concept.getElementsByTagName('name')[0].childNodes[0].nodeValue
            code = concept.getElementsByTagName('code')[0].childNodes[0].nodeValue
            rdf_rt_id = concept.getElementsByTagName('id')[0].childNodes[0].nodeValue

            # go through all possible Role (Relationships) and only the drug are except, 
            # which has Role of contraindication or induce
            definitionRoles = concept.getElementsByTagName('definingRoles')[0]
            if definitionRoles.hasChildNodes() == True:
                roles = definitionRoles.getElementsByTagName('role')
                # list with all diseases that has a contra indication with this drug
                list_contra = []
                # list with all diseases that has a induce by this drug
                list_induce = []
                for role in roles:
                    # test if has a relationship 'CI_with' (code:36)
                    if role.getElementsByTagName('name')[0].childNodes[0].nodeValue == 'C36':
                        has_a_interesting_rela = True
                        list_contra.append(role.getElementsByTagName('value')[0].childNodes[0].nodeValue)
                    # test if has a relationship 'induces' (code:40)
                    elif role.getElementsByTagName('name')[0].childNodes[0].nodeValue == 'C40':
                        has_a_interesting_rela = True
                        list_induce.append(role.getElementsByTagName('value')[0].childNodes[0].nodeValue)

                # only when a relation with induce or contraindicates was found save the information in lists and dictionary
                if has_a_interesting_rela == True:

                    # list of all disease that has a relationship that is wanted
                    global list_disease
                    list_disease = list_disease + list(set(list_contra) - set(list_disease))
                    list_disease = list_disease + list(set(list_induce) - set(list_disease))

                    # all contraindictaion are saved as tuple of drug and disease
                    for contraindication in list_contra:
                        if not (code, contraindication) in list_contraindication:
                            list_contraindication.append((code, contraindication))

                    # all induce are saved as tuple of drug and disease
                    for induce in list_induce:
                        if not (code, induce) in list_induces:
                            list_induces.append((code, induce))

                    # go through all properties of this drug and generate a list of string
                    prop = concept.getElementsByTagName('properties')[0]
                    properties = prop.getElementsByTagName('property')
                    properties_list = []
                    for proper in properties:
                        name_property = proper.getElementsByTagName('name')[0].childNodes[0].nodeValue
                        value = proper.getElementsByTagName('value')[0].childNodes[0].nodeValue
                        value = value.replace('"', '\'')
                        text = dict_properties_code_to_name[name_property] + ':' + value
                        properties_list.append(text)

                    # go through association of this drug and generate a list of string
                    association_list = []
                    if len(concept.getElementsByTagName('associations')) > 0:
                        associat = concept.getElementsByTagName('associations')[0]
                        associations = associat.getElementsByTagName('association')

                        if len(associations) > 0:

                            for association in associations:
                                name_association = association.getElementsByTagName('name')[0].childNodes[0].nodeValue
                                value = association.getElementsByTagName('value')[0].childNodes[0].nodeValue
                                text = dict_associations_concept_to_name[name_association] + ':' + value
                                association_list.append(text)

                    # create a drug as a concept class
                    concept = Concept(name, code, rdf_rt_id, properties_list, association_list)
                    # add drug to the dictionary
                    dict_drugs[code] = concept

        # test if it is a disease and all disease will be save in a dictionary
        elif concept.getElementsByTagName('kind')[0].childNodes[0].nodeValue == 'C16':
            name = concept.getElementsByTagName('name')[0].childNodes[0].nodeValue
            code = concept.getElementsByTagName('code')[0].childNodes[0].nodeValue
            rdf_rt_id = concept.getElementsByTagName('id')[0].childNodes[0].nodeValue

            # go through all properties of this disease and generate a list of string
            prop = concept.getElementsByTagName('properties')[0]
            properties = prop.getElementsByTagName('property')
            properties_list = []
            for proper in properties:
                name_property = proper.getElementsByTagName('name')[0].childNodes[0].nodeValue
                value = proper.getElementsByTagName('value')[0].childNodes[0].nodeValue
                value = value.replace('"', '\'')
                text = dict_properties_code_to_name[name_property] + ':' + value
                properties_list.append(text)

            # go through association of this disease and generate a list of string
            association_list = []
            if len(concept.getElementsByTagName('associations')) > 0:
                associat = concept.getElementsByTagName('associations')[0]
                associations = associat.getElementsByTagName('association')

                if len(associations) > 0:

                    for association in associations:
                        name_association = association.getElementsByTagName('name')[0].childNodes[0].nodeValue
                        value = association.getElementsByTagName('value')[0].childNodes[0].nodeValue
                        text = dict_associations_concept_to_name[name_association] + ':' + value
                        association_list.append(text)
            # create a disease as a concept class       
            concept = Concept(name, code, rdf_rt_id, properties_list, association_list)
            # add disease to the dictionary
            dict_diseases[code] = concept


'''
This function generate one or more cyper files to integrate the important ndf-rt data into neo4j with the neo4j shell.
For the nodes it goes through the dictionary of the drug and disease and generate a cypher commands to Create this node
also the id will be defined as unique
The relationships are get from the list for induces and contraindicates.
The cypher code is that first need to match the nodes and than the relationship can be created
'''


def generate_cypher_file():
    # counter of files that are generate
    i = 1

    # can not commit so many nodes and relationship at once, so this is the maximal number of commited oderes
    constrain_number = 20000

    # the computer in the room, has problem with the cypher files wich has mor than 1,000,000 orders, so this ich the maximal number of oderes in a file
    creation_max_in_file = 1000000

    f = open('NDF_RT_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
    # a commit start every time with begin
    f.write('begin \n')
    i += 1

    # counter of creation steps
    counter_create = 0
    print('drug Create')
    print (datetime.datetime.utcnow())
    # go through all drugs that has a contraindication or induces a disease 
    for key, value in dict_drugs.items():
        create_text = 'Create (:NDF_RT_drug{name: "%s" , code: "%s", properties: "%s", association: "%s"});\n' % (
        value.name, key, value.properties, value.association)
        counter_create += 1
        f.write(create_text)

        # test if the counter has the maximal number of creation for a commit or for a file break
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('NDF_RT_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit \n begin \n')
    # generate that code is for the node with lable NDFR_RT_drug unique
    f.write('Create Constraint On (node:NDF_RT_drug) Assert node.code Is Unique; \n')
    f.write('commit \n schema await \n begin \n')
    print(len(dict_drugs))

    print('disease Create')
    print (datetime.datetime.utcnow())
    # go through all diseases that has a contraindication or iduces with a drug 
    for disease in list_disease:
        create_text = 'Create (:NDF_RT_disease{name: "%s" , code: "%s", properties: "%s", association: "%s"});\n' % (
        dict_diseases[disease].name, dict_diseases[disease].code, dict_diseases[disease].properties,
        dict_diseases[disease].association)
        counter_create += 1
        f.write(create_text)

        # test if the counter has the maximal number of creation for a commit or for a file break
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('NDF_RT_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit \n begin \n')
    # generate that code is for the node with lable NDFR_RT_disease unique
    f.write('Create Constraint On (node:NDF_RT_disease) Assert node.code Is Unique; \n')
    f.write('commit \n schema await \n begin \n')

    print(len(list_disease))

    print('rel contraindictaion')
    print (datetime.datetime.utcnow())
    # go through the list with all contraindication realtionships and generate a cypher code to create it in neo4j
    for pair in list_contraindication:
        create_text = '''Match (n1:NDF_RT_drug {code: "%s"}), (n2:NDF_RT_disease {code: "%s"}) Create (n1)-[:ContraIndicates]->(n2); \n''' % (
        pair[0], pair[1])

        counter_create += 1
        f.write(create_text)
        # test if the counter has the maximal number of creation for a commit or for a file break
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('NDF_RT_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')

    print(len(list_contraindication))

    print('rel induce')
    print (datetime.datetime.utcnow())
    # go through the list with all induces realtionships and generate a cypher code to create it in neo4j
    for pair in list_induces:
        create_text = '''Match (n1:NDF_RT_drug {code: "%s"}), (n2:NDF_RT_disease {code: "%s"}) Create (n1)-[:Induces]->(n2); \n''' % (
        pair[0], pair[1])

        counter_create += 1
        f.write(create_text)
        # test if the counter has the maximal number of creation for a commit or for a file break
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('NDF_RT_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit')

    print(len(list_induces))


def main():
    # start the function to load in the xml file and save the importen values in list and dictionaries
    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('load in the xml data')
    load_ndf_rt_xml_inferred_in()

    # this generate from the dictionaries and the list the cypher file 
    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('generate cypher file')
    generate_cypher_file()

    print('#############################################################')
    print (datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
