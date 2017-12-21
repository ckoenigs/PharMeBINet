# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 16:45:32 2017

@author: Cassandra
"""
import datetime
import sys
import csv
import io

# path to data for windows
if len(sys.argv) > 1:
    # filepath= "file:///"+sys.argv[1]
    filepath = sys.argv[1]
else:
    # filepath="file:///c:/Users/Cassandra/Documents/uni/Master/test/CDT/"
    filepath = 'CDT/'

# a dictionary of chemicals where the mesh id is the key and value is class chemicals   
dict_chemicals = {}


class chemicals:
    """
    name: string
    chem_id: string (Mesh ID)
    idType: string (Mesh)
    casRN:string
    drugBankID: string
    definition: string
    parentIDs: string (MESH ID/s with | as seperator)
    treeNumbers: string (with | as seperator)
    parentTreeNumbers: string
    synonyms: string (with separator |)
    drugBankIDs: string (with separator |)
    """

    def __init__(self, name, chem_id, CasRN):
        self.name = name
        divide_ID = chem_id.split(':')
        # separated id in type and ID
        if len(divide_ID) > 1:
            self.chem_id = divide_ID[1]
            self.idType = divide_ID[0]
        else:
            self.chem_id = chem_id
            self.idType = ''
        self.casRN = CasRN
        self.drugBankID = ''
        self.definition = ''
        self.parentIDs = ''
        self.treeNumbers = ''
        self.parentTreeNumbers = ''
        self.synonyms = ''
        self.drugBankIDs = ''

    def set_other_properties(self, definition, parentIDs, treeNumbers, parentTreeNumbers, synonyms, drugBankIDs):
        self.definition = definition
        self.parentIDs = parentIDs
        self.treeNumbers = treeNumbers
        self.parentTreeNumbers = parentTreeNumbers
        self.synonyms = synonyms
        if drugBankIDs:
            splitt = drugBankIDs.split('|')
            self.drugBankID = splitt[0]
            self.drugBankIDs = '|'.join(splitt[1:])
        else:
            self.drugBankIDs = drugBankIDs


# dictionary with disease mesh/omim id as key and element of class diseases as value
dict_diseases = {}


class diseases():
    """
    disease_id: string (Mesh or OMIM ID)
    name: string
    idType: string (is MESH or OMIM)
    definition: string
    altDiseaseIDs: string (can be OMIM, Mesh or DOID)
    parentIDs: string (Mesh ID/s with | as seperator)
    treeNumbers: string (with | as seperator)
    parentTreeNumbers: string (with | as seperator)
    synonyms: string (with | as seperator)
    slimMappings: string (with | as seperator)
    """

    def __init__(self, name, disease_id):
        self.name = name
        divide_ID = disease_id.split(':')
        # seperate type and ID
        if len(divide_ID) > 1:
            self.disease_id = divide_ID[1]
            self.idType = divide_ID[0]
        else:
            self.disease_id = disease_id
            self.idType = ''
        self.definition = ''
        self.altDiseaseIDs = ''
        self.parentIDs = ''
        self.treeNumbers = ''
        self.parentTreeNumbers = ''
        self.synonyms = ''
        self.slimMappings = ''

    def set_other_properties(self, definition, altDiseaseIDs, parentIDs, treeNumbers, parentTreeNumbers, synonyms,
                             slimMappings):
        self.definition = definition
        self.altDiseaseIDs = altDiseaseIDs
        self.parentIDs = parentIDs
        self.treeNumbers = treeNumbers
        self.parentTreeNumbers = parentTreeNumbers
        self.synonyms = synonyms
        self.slimMappings = slimMappings


# dictionary with go_id as key and a element ot class phenotype_syntom as value
dict_phenotype = {}


class phenotype_symptom():
    '''
    go_id: string (only the number of the id)
    name: string
    idType: string (is GO)
    phenotypeActionDegreeType: string
    '''

    def __init__(self, name, go_id):
        self.name = name
        divide = go_id.split(':')
        self.go_id = divide[1]
        self.idType = divide[0]


# dictionary with key (chemical id (mesh id), disease id (mesh/omim id)) and value is element of
#  class edge_chemical_disease_side_effect

dict__chemical_disease_side_effect = {}


class edge_chemical_disease_side_effect:
    """
    chemical_id: string (mesh id)
    disease_id: string (mesh/omim id)
    correlation: string (is positive correlated)
    """

    def __init__(self, chemical_id, disease_id, correlation):
        divide_chemical = chemical_id.split(':')
        if len(divide_chemical) > 1:
            self.chemical_id = divide_chemical[1]
        else:
            self.chemical_id = chemical_id
        divide_disease = disease_id.split(':')
        if len(divide_disease) > 1:
            self.disease_id = divide_disease[1]
        else:
            self.disease_id = disease_id
        self.correlation = correlation


# dictionary with key (chemical id, disease id) and value is element of class edge_chemical_phenotype_side_effect

dict__chemical_phenotype_side_effect = {}


class edge_chemical_phenotype_side_effect:
    '''
    chemical_id: string (Mesh ID)
    go_id: string (int from GO ID)
    correlation: string (is positive correlated)
    phenotypeActionDegreeType: string (defined what happened to the phenotype)
    '''

    def __init__(self, chemical_id, go_id, correlation, phenotypeActionDegreeType):
        divide_chemical = chemical_id.split(':')
        if len(divide_chemical) > 1:
            self.chemical_id = divide_chemical[1]
        else:
            self.chemical_id = chemical_id
        divide_go_id = go_id.split(':')
        self.go_id = divide_go_id[1]
        self.correlation = correlation
        self.phenotypeActionDegreeType = phenotypeActionDegreeType


# dictionary with key (chemical id (Mesh ID), disease id(Mesh/omim ID)) and value is element
# of class edge_chemical_disease
dict_edge_chemical_disease = {}


class edge_chemical_disease():
    """
    chemical_id: string (Mesh id)
    disease_id: string (Mesh/omim id)
    directEvidence: string (nothing /therapeutic / marker/mechanism)
    inferenceGeneSymbol: string 
    inferenceScore: string (is a float)
    pubMedIDs: string (separator |)
    """

    def __init__(self, chemical_id, disease_id, directEvidence, inferenceGeneSymbol, inferenceScore, pubMedIDs):
        divide_chemical = chemical_id.split(':')
        if len(divide_chemical) > 1:
            self.chemical_id = divide_chemical[1]
        else:
            self.chemical_id = chemical_id
        divide_disease = disease_id.split(':')

        if len(divide_disease) > 1:
            self.disease_id = divide_disease[1]
        else:
            self.disease_id = disease_id
        self.directEvidence = directEvidence
        self.inferenceGeneSymbol = inferenceGeneSymbol
        self.inferenceScore = inferenceScore
        self.pubMedIDs = pubMedIDs


# list with all receptors
list_receptors = []

# dictionary with count of the different receptors with disease
dict_receptor_number_disease = {}

# dictionary with count of outcome
dict_receptor_number_outcome = {}

'''
Go through this file CTD_exposure_events.csv and put all information into the dictionary.
This only contains the information about the causese relationship, but only the one with outcome and positive 
correlation.
The information of the receptors are gathered and written in a new file.
1    ExposureStressorName
2    ExposureStressorID (MeSH identifier)
3    StressorSourceCategory ('|'-delimited list) x
4    StressorSourceDetails x
5    NumberOfStressorSamples x
6    StressorNotes x
7    NumberOfReceptors x
8    Receptors x
9    ReceptorNotes x
10    SmokingStatus ('|'-delimited list) x
11    Age x
12    AgeUnitsOfMeasurement x
13   AgeQualifier x
14    Sex x
15    Race ('|'-delimited list) x
16    Methods ('|'-delimited list) x
17    DetectionLimit x
18    DetectionLimitUnitsOfMeasurement x
19    DetectionFrequency x
20    Medium x
21    ExposureMarker x
22    ExposureMarkerID (MeSH or NCBI Gene identifier) x
23    MarkerLevel x
24    MarkerUnitsOfMeasurement x
25    MarkerMeasurementStatistic x
26    AssayNotes x
27    StudyCountries ('|'-delimited list) x
28    StateOrProvince ('|'-delimited list) x
29    City,Town,Region,Area ('|'-delimited list) x
30    ExposureEventNotes x
31    OutcomeRelationship 
32    DiseaseName
33    DiseaseID (MeSH or OMIM identifier)
34    PhenotypeName
35    PhenotypeID (GO identifier)
36    PhenotypeActionDegreeType
37    Anatomy (MeSH term; '|'-delimited list) x
38    ExposureOutcomeNotes 
39    Reference x
40    AssociatedStudyTitles ('|'-delimited list) x
41    EnrollmentStartYear x
42    EnrollmentEndYear x
43    StudyFactors ('|'-delimited list) x
'''


def get_chemical_event_relation():
    i = 0
    g = open('CTD_outcome/file_with_outcome.tsv', 'w')
    count_chemical_disease = 0
    count_chemichal_phenotype = 0
    count_all = 0
    with open(filepath + 'CTD_exposure_events.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            i += 1
            # the file has a lot of comments in the first rows
            if i > 27:
                name = ''
                j = 1
                # every row has 2 elements
                for key, value in row.items():
                    
                    # the order of the elements change sometimes and can causes errors
                    if j == 1:
                        name = value
                    else:
                        chemical_id = value[0]
                        chemical = chemicals(name, chemical_id, '')
                        if len(chemical_id.split(':')) > 1:
                            if (not chemical_id in dict_chemicals) or (not chemical_id.split(':')[1] in dict_chemicals):
                                dict_chemicals[chemical_id.split(':')[1]] = chemical
                        elif (not chemical_id in dict_chemicals):
                            dict_chemicals[chemical_id] = chemical
                        receptor = value[6]
                        if not receptor in list_receptors:
                            list_receptors.append(receptor)
                        outcomeRelation = value[29]
                        diseaseName = value[30]
                        diseaseID = value[31]
                        phenotypeName = value[32]
                        phenotypeID = value[33]
                        count_all += 1
                        PhenotypeActionDegreeType = value[34]
                        # take only the one with positive correlation
                        if outcomeRelation:
                            if outcomeRelation == 'positive correlation':
                                # this is only for the outcome is a disease
                                if diseaseName:
                                    if receptor in dict_receptor_number_disease:
                                        dict_receptor_number_disease[receptor] += 1
                                    else:
                                        dict_receptor_number_disease[receptor] = 1

                                    if receptor in dict_receptor_number_outcome:
                                        dict_receptor_number_outcome[receptor] += 1
                                    else:
                                        dict_receptor_number_outcome[receptor] = 1

                                    count_chemical_disease += 1
                                    disease = diseases(diseaseName, diseaseID)
                                    # order get only the disease id and att the disease to the dictionary
                                    if len(diseaseID.split(':')) > 1:
                                        if (not diseaseID in dict_diseases) or (
                                        not diseaseID.split(':')[1] in dict_diseases):
                                            dict_diseases[diseaseID.split(':')[1]] = disease
                                    elif (not diseaseID in dict_diseases):
                                        dict_diseases[diseaseID] = disease

                                    # take only the id from the chemicals
                                    if len(chemical_id.split(':')) > 1 and len(diseaseID.split(':')) > 1:
                                        if (not (chemical_id.split(':')[1],
                                                 diseaseID) in dict__chemical_disease_side_effect) or (not (chemical_id,
                                                                                                        diseaseID.split(
                                                                                                                ':')[
                                                                                                            1]) in dict__chemical_disease_side_effect) or (
                                        not (chemical_id.split(':')[1],
                                             diseaseID.split(':')[1]) in dict__chemical_disease_side_effect):
                                            edge = edge_chemical_disease_side_effect(chemical_id, diseaseID,
                                                                                 outcomeRelation)
                                            dict__chemical_disease_side_effect[
                                                (chemical_id.split(':')[1], diseaseID.split(':')[1])] = edge
                                    elif len(chemical_id.split(':')) > 1:
                                        if (
                                        not (chemical_id.split(':')[1], diseaseID) in dict__chemical_disease_side_effect):
                                            edge = edge_chemical_disease_side_effect(chemical_id, diseaseID,
                                                                                 outcomeRelation)
                                            dict__chemical_disease_side_effect[
                                                (chemical_id.split(':')[1], diseaseID)] = edge
                                    elif len(diseaseID.split(':')) > 1:
                                        if (
                                        not (chemical_id, diseaseID.split(':')[1]) in dict__chemical_disease_side_effect):
                                            edge = edge_chemical_disease_side_effect(chemical_id, diseaseID,
                                                                                 outcomeRelation)
                                            dict__chemical_disease_side_effect[
                                                (chemical_id, diseaseID.split(':')[1])] = edge
                                    elif (not (chemical_id, diseaseID) in dict__chemical_disease_side_effect):
                                        edge = edge_chemical_disease_side_effect(chemical_id, diseaseID, outcomeRelation)
                                        dict__chemical_disease_side_effect[(chemical_id, diseaseID)] = edge
                                # this is for the outcome is a phenotype
                                elif phenotypeID:
                                    count_chemichal_phenotype += 1

                                    if receptor in dict_receptor_number_outcome:
                                        dict_receptor_number_outcome[receptor] += 1
                                    else:
                                        dict_receptor_number_outcome[receptor] = 1

                                    # split the id in the integer and add the phenotype to the dictionary
                                    if len(phenotypeID.split(':')) > 1:
                                        if (not phenotypeID.split(':')[1] in dict_phenotype):
                                            phenotype = phenotype_symptom(phenotypeName, phenotypeID)
                                            dict_phenotype[phenotypeID.split(':')[1]] = phenotype
                                    elif (not phenotypeID in dict_phenotype):
                                        phenotype = phenotype_symptom(phenotypeName, phenotypeID)
                                        dict_phenotype[phenotypeID] = phenotype

                                    # add the edge to the dictionary
                                    if len(chemical_id.split(':')) > 1 and len(diseaseID.split(':')) > 1:
                                        if (not (chemical_id.split(':')[1],
                                                 phenotypeID) in dict__chemical_phenotype_side_effect) or (not (chemical_id,
                                                                                                            phenotypeID.split(
                                                                                                                    ':')[
                                                                                                                1]) in dict__chemical_phenotype_side_effect) or (
                                        not (chemical_id.split(':')[1],
                                             phenotypeID.split(':')[1]) in dict__chemical_phenotype_side_effect):
                                            edge = edge_chemical_phenotype_side_effect(chemical_id, phenotypeID,
                                                                                   outcomeRelation,
                                                                                   PhenotypeActionDegreeType)
                                            dict__chemical_phenotype_side_effect[
                                                (chemical_id.split(':')[1], phenotypeID.split(':')[1])] = edge
                                    elif len(chemical_id.split(':')) > 1:
                                        if (not (chemical_id.split(':')[1],
                                                 phenotypeID) in dict__chemical_phenotype_side_effect):
                                            edge = edge_chemical_phenotype_side_effect(chemical_id, phenotypeID,
                                                                                   outcomeRelation,
                                                                                   PhenotypeActionDegreeType)
                                            dict__chemical_phenotype_side_effect[
                                                (chemical_id.split(':')[1], phenotypeID)] = edge
                                    elif len(diseaseID.split(':')) > 1:
                                        if (not (chemical_id,
                                                 phenotypeID.split(':')[1]) in dict__chemical_phenotype_side_effect):
                                            edge = edge_chemical_phenotype_side_effect(chemical_id, phenotypeID,
                                                                                   outcomeRelation,
                                                                                   PhenotypeActionDegreeType)
                                            dict__chemical_phenotype_side_effect[
                                                (chemical_id, phenotypeID.split(':')[1])] = edge
                                    elif (not (chemical_id, phenotypeID) in dict__chemical_phenotype_side_effect):
                                        edge = edge_chemical_phenotype_side_effect(chemical_id, phenotypeID,
                                                                               outcomeRelation,
                                                                               PhenotypeActionDegreeType)
                                        dict__chemical_phenotype_side_effect[(chemical_id, phenotypeID)] = edge

                                line = "\t".join(value)
                                g.write(line + '\n')

                    j += 1

    g.close()
    # wrote all receptors in a file
    receptors = '\n'.join(list_receptors)
    t = open('CTD_outcome/all_receptors.txt', 'w')
    t.write(receptors)
    t.close()
    print('all outcome:' + str(count_chemical_disease + count_chemichal_phenotype))
    print('phenotype:' + str(count_chemichal_phenotype))
    print('disease:' + str(count_chemical_disease))
    print('all events' + str(count_all))
    # write how often every receptor have a disease
    b = open('CTD_outcome/receptor_disease.tsv', 'w')
    b.write('receptor \t number of diseases \n')
    for receptor, count in dict_receptor_number_disease.items():
        b.write(receptor + '\t' + str(count) + '\n')
    b.close()

    # write in a fie how often a receptor has a phenotype as outcome
    b = open('CTD_outcome/receptor_outcome.tsv', 'w')
    b.write('receptor \t number of outcome (disease/phenotype) \n')
    for receptor, count in dict_receptor_number_outcome.items():
        b.write(receptor + '\t' + str(count) + '\n')
    b.close()


'''
load in the information from the file CTD_chemicals_diseases.csv and remember them in the dictionary dict_disease,
 dict_chemicals, edge_chemical_disease
1.    ChemicalName
2:    ChemicalID (MeSH identifier)
3:    CasRN (CAS Registry Number, if available)
4:    DiseaseName
5:    DiseaseID (MeSH or OMIM identifier)
6:    DirectEvidence ('|'-delimited list)
7:    InferenceGeneSymbol
8:    InferenceScore
9:    OmimIDs ('|'-delimited list)
10:    PubMedIDs ('|'-delimited list)

'''


def get_chemical_disease_associations():
    # row counter
    i = 0
    h = open('CTD_outcome/file_with_association_marker_mechanism.tsv', 'w')
    with open(filepath + 'CTD_chemicals_diseases.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            i += 1

            # row with information start later, but somtimes the program get this information early or later
            if i > 28:
                chemical_name = ''
                j = 1
                
                # every row has two elements
                for key, value in row.items():

                    # domtimes the order is the other way around
                    if j == 1:
                        chemical_name = value
                    else:
                        chemicalID = value[0]
                        casRN = value[1]
                        directEvidence = value[4]
                        # write all information about marker/mechanism in a file
                        if directEvidence == 'marker/mechanism':
                            line = '\t'.join(value)
                            h.write(line + '\n')
                        # when the directEvidence is empty then the relationship is from inference and can not be used
                        elif directEvidence == '':
                            break
                        # get the the chemical id and add the chemical to the dictionary
                        if len(chemicalID.split(':')) > 1:
                            if (not chemicalID.split(':')[1] in dict_chemicals):
                                chemical = chemicals(chemical_name, chemicalID, casRN)
                                dict_chemicals[chemicalID.split(':')[1]] = chemical
                        elif (not chemicalID in dict_chemicals):
                            chemical = chemicals(chemical_name, chemicalID, casRN)
                            dict_chemicals[chemicalID] = chemical

                        diseaseName = value[2]
                        diseaseID = value[3]
                        inferenceGeneSymbol = value[5]
                        inferenceScore = value[6]
                        omimIDs = value[7]
                        pubMedIDs = value[8]
                        # get the disease id and add the disease to the dictionary if not already is in their
                        if len(diseaseID.split(':')) > 1:
                            if (not diseaseID.split(':')[1] in dict_diseases):
                                disease = diseases(diseaseName, diseaseID)
                                dict_diseases[diseaseID.split(':')[1]] = disease
                        elif (not diseaseID in dict_diseases):
                            disease = diseases(diseaseName, diseaseID)
                            dict_diseases[diseaseID] = disease

                        # add the edge to the dictionary
                        if len(chemicalID.split(':')) > 1 and len(diseaseID.split(':')) > 1:
                            if (not (chemicalID.split(':')[1], diseaseID) in dict_edge_chemical_disease) or (
                            not (chemicalID, diseaseID.split(':')[1]) in dict_edge_chemical_disease) or (
                            not (chemicalID.split(':')[1], diseaseID.split(':')[1]) in dict_edge_chemical_disease):
                                edge = edge_chemical_disease(chemicalID, diseaseID, directEvidence, inferenceGeneSymbol,
                                                             inferenceScore, pubMedIDs)
                                dict_edge_chemical_disease[(chemicalID.split(':')[1], diseaseID.split(':')[1])] = edge
                        elif len(chemicalID.split(':')) > 1:
                            if (not (chemicalID.split(':')[1], diseaseID) in dict_edge_chemical_disease):
                                edge = edge_chemical_disease(chemicalID, diseaseID, directEvidence, inferenceGeneSymbol,
                                                             inferenceScore, pubMedIDs)
                                dict_edge_chemical_disease[(chemicalID.split(':')[1], diseaseID)] = edge
                        elif len(diseaseID.split(':')) > 1:
                            if (not (chemicalID, diseaseID.split(':')[1]) in dict_edge_chemical_disease):
                                edge = edge_chemical_disease(chemicalID, diseaseID, directEvidence, inferenceGeneSymbol,
                                                             inferenceScore, pubMedIDs)
                                dict_edge_chemical_disease[(chemicalID, diseaseID.split(':')[1])] = edge
                        elif (not (chemicalID, diseaseID) in dict_edge_chemical_disease):
                            edge = edge_chemical_disease(chemicalID, diseaseID, directEvidence, inferenceGeneSymbol,
                                                         inferenceScore, pubMedIDs)
                            dict_edge_chemical_disease[(chemicalID, diseaseID)] = edge
                    j += 1
    h.close()


'''
Load further information for chemicals in dictionary from file CTD_chemicals.csv.
properties:
1    ChemicalName
2    ChemicalID (MeSH identifier)
3    CasRN (CAS Registry Number, if available)
4    Definition
5    ParentIDs (identifiers of the parent terms; '|'-delimited list)
6    TreeNumbers (identifiers of the chemical's nodes; '|'-delimited list)
7    ParentTreeNumbers (identifiers of the parent nodes; '|'-delimited list)
8    Synonyms ('|'-delimited list)
9   DrugBankIDs ('|'-delimited list)
'''


def more_information_for_chemical():
    # row counter
    i = 0
    with open(filepath + 'CTD_chemicals.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            i += 1
            # file has big header in file, sometimes it start earlier or later 
            if i > 28:
                chemical_name = ''
                j = 1
                for key, value in row.items():
                    # a row has to properties but the order change somtimes
                    if j == 1:
                        chemical_name = value
                    else:
                        # print(value)
                        chemicalID = value[0]
                        casRN = value[1]
                        definition = value[2]
                        parentIDs = value[3]
                        treeNumbers = value[4]
                        parentTreeNumbers = value[5]
                        synonyms = value[6]
                        drugBankIDs = value[7]

                        # add the addtional information for chemicals which are in the dictionary
                        if chemicalID in dict_chemicals:

                            dict_chemicals[chemicalID].set_other_properties(definition, parentIDs, treeNumbers,
                                                                            parentTreeNumbers, synonyms, drugBankIDs)
                        elif len(chemicalID.split(':')) > 1:
                            if chemicalID.split(':')[1] in dict_chemicals:
                                dict_chemicals[chemicalID.split(':')[1]].set_other_properties(definition, parentIDs,
                                                                                              treeNumbers,
                                                                                              parentTreeNumbers,
                                                                                              synonyms, drugBankIDs)

                    j += 1



'''
Load further disease information into the dictionary from CTD_diseases.csv.
Properties:
1    DiseaseName
2    DiseaseID (MeSH or OMIM identifier)
3    AltDiseaseIDs (alternative identifiers; '|'-delimited list)
4    Definition
5    ParentIDs (identifiers of the parent terms; '|'-delimited list)
6    TreeNumbers (identifiers of the disease's nodes; '|'-delimited list)
7    ParentTreeNumbers (identifiers of the parent nodes; '|'-delimited list)
8    Synonyms ('|'-delimited list)
9    SlimMappings (MEDIC-Slim mappings; '|'-delimited list)
'''


def more_information_for_disease():
    # row counter
    i = 0
    with open(filepath + 'CTD_diseases.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            i += 1
            # the information start in row 27, sometimes it is earlier or later
            if i > 28:
                j = 1
                disease_Name = ''
                # every row has two properties
                for key, value in row.items():
                    # somtimes it is the program change the order fro all information
                    if j != 1:

                        diseaseID = value[0]
                        definition = value[2]
                        altDiseaseIDs = value[1]
                        parentIDs = value[3]
                        treeNumbers = value[4]
                        parentTreeNumbers = value[5]
                        synonyms = value[6]
                        slimMappings = value[7]
                        # add the new properties only to the diseases from the dictionary
                        if diseaseID in dict_diseases:
                            dict_diseases[diseaseID].set_other_properties(definition, altDiseaseIDs, parentIDs,
                                                                          treeNumbers, parentTreeNumbers, synonyms,
                                                                          slimMappings)
                        elif len(diseaseID.split(':')) > 1:
                            if diseaseID.split(':')[1] in dict_diseases:
                                # print(diseaseID)
                                dict_diseases[diseaseID.split(':')[1]].set_other_properties(definition, altDiseaseIDs,
                                                                                            parentIDs, treeNumbers,
                                                                                            parentTreeNumbers, synonyms,
                                                                                            slimMappings)

                    else:
                        disease_Name = value
                    j += 1
'''
This generate the csv files for the nodes and relationships which can be use to be integrated with neo4j import tool.
This need the the links to ctd.
'''

def generate_csv():
    print('drug Create')
    print (datetime.datetime.utcnow())
    # csv file for chemicals
    f = open('chemical_CTD.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(('chemical_id:ID(CTDchemical)', 'name', 'idType', 'casRN', 'drugBankID', 'definition',
                         'parentIDs', 'treeNumbers', 'parentTreeNumbers', 'synonyms', 'drugBankIDs'))
        for key, value in dict_chemicals.items():
            writer.writerow((value.chem_id, value.name, value.idType, value.casRN, value.drugBankID, value.definition,
                             value.parentIDs, value.treeNumbers, value.parentTreeNumbers, value.synonyms,
                             value.drugBankIDs))

    finally:
        f.close()

    print('disease Create')
    print (datetime.datetime.utcnow())
    # csv file for diseases
    f = open('disease_CTD.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(('disease_id:ID(CTDdisease)', 'name', 'idType', 'definition', 'altDiseaseIDs', 'parentIDs',
                         'treeNumbers', 'parentTreeNumbers', 'synonyms', 'slimMappings'))
        for key, value in dict_diseases.items():
            writer.writerow((value.disease_id, value.name, value.idType, value.definition, value.altDiseaseIDs,
                             value.parentIDs, value.treeNumbers, value.parentTreeNumbers, value.synonyms,
                             value.slimMappings))

    finally:
        f.close()

    print('phenotype Create')
    print (datetime.datetime.utcnow())
    # csv file for phenotypes
    f = open('phenotype_CTD.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(('go_id:ID(CTDphenotype)', 'name', 'idType'))
        for key, value in dict_phenotype.items():
            writer.writerow((value.go_id, value.name, value.idType))

    finally:
        f.close()

    print('rel chemical disease side effects')
    print (datetime.datetime.utcnow())
    # csv for all chemical -disease causese relationships
    f = open('chemical_disease_side_effects_relation_CTD.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow((':START_ID(CTDchemical)', 'correlation', ':END_ID(CTDdisease)'))

        for key, value in dict__chemical_disease_side_effect.items():
            writer.writerow((value.chemical_id, value.correlation, value.disease_id))


    finally:
        f.close()

    print('rel chemical phenotype side effect')
    print (datetime.datetime.utcnow())
    # csv for all chemical-phenotype causes relationship
    f = open('chemical_phenotype_side_effects_relation_CTD.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow((':START_ID(CTDchemical)', 'correlation', 'phenotypeActionDegreeType', ':END_ID(CTDphenotype)'))

        for key, value in dict__chemical_phenotype_side_effect.items():
            writer.writerow((value.chemical_id, value.correlation, value.phenotypeActionDegreeType, value.go_id))


    finally:
        f.close()

    print('rel chemical disease')
    print (datetime.datetime.utcnow())
    # csv for all chemical- diseases which has direct evidence : therapeutic or marker/mechanism
    f = open('chemical_disease_relation_CTD.csv', 'wt', newline='', encoding='utf-8')
    try:
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow((':START_ID(CTDchemical)', 'directEvidence', 'inferenceGeneSymbol', 'inferenceScore',
                         'pubMedIDs', ':END_ID(CTDdisease)'))

        for key, value in dict_edge_chemical_disease.items():
            writer.writerow((value.chemical_id, value.directEvidence, value.inferenceGeneSymbol, value.inferenceScore,
                             value.pubMedIDs, value.disease_id))


    finally:
        f.close()

'''
Generate cypher file to integrat all information into neo4j with neo4j shell
'''

def generate_cypher_file_for_construction():
    # file counter
    i = 1
    # maximal number of queries for a commit block
    constrain_number = 20000
    # maximal number of queries in a file
    creation_max_in_file = 1000000

    f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
    f.write('begin \n')
    i += 1

    # queries counter
    counter_create = 0
    print('drug Create')
    print (datetime.datetime.utcnow())
    # first all chemical nodes are added into the file
    for key, value in dict_chemicals.items():
        create_text = 'Create (:CTDchemical{chemical_id: "%s" , name: "%s", idType: "%s", casRN: "%s", drugBankID: "%s" ,definition: "%s" ,parentIDs: "%s" ,treeNumbers: "%s" ,parentTreeNumbers: "%s", synonyms: "%s", drugBankIDs:"%s", ctd_url:"http://ctdbase.org/detail.go?type=chem&acc=%s"});\n' % (
        value.chem_id, value.name, value.idType, value.casRN, value.drugBankID, value.definition, value.parentIDs,
        value.treeNumbers, value.parentTreeNumbers, value.synonyms, value.drugBankIDs, value.chem_id )
        counter_create += 1
        f.write(create_text)
        #test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')
    f.write('commit \n begin \n')
    # make the id unique
    f.write('Create Constraint On (node:CTDchemical) Assert node.chemical_id Is Unique; \n')
    f.write('commit \n schema await \n begin \n')

    print('disease Create')
    print (datetime.datetime.utcnow())
    # all disease nodes are added
    for key, value in dict_diseases.items():
        create_text = 'Create (:CTDdisease{disease_id: "%s" , name: "%s" , idType: "%s" ,definition: "%s" ,altDiseaseIDs: "%s",parentIDs: "%s" , treeNumbers: "%s" ,parentTreeNumbers: "%s" ,synonyms: "%s" ,slimMappings: "%s", ctd_url="http://ctdbase.org/detail.go?type=disease&acc=%s"});\n' % (
        value.disease_id, value.name, value.idType, value.definition, value.altDiseaseIDs, value.parentIDs,
        value.treeNumbers, value.parentTreeNumbers, value.synonyms, value.slimMappings, value.idType+':'+value.disease_id)
        counter_create += 1
        f.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')

    f.write('commit \n begin \n')
    # make id unique in neo4j
    f.write('Create Constraint On (node:CTDdisease) Assert node.disease_id Is Unique; \n')
    f.write('commit \n schema await \n begin \n')

    print('phenotype Create')
    print (datetime.datetime.utcnow())
    # add all phenotype nodes
    for key, value in dict_phenotype.items():
        create_text = 'Create (:CTDphenotype{go_id: "%s" , name: "%s" , idType: "%s", ctd_url:"http://ctdbase.org/detail.go?type=go&acc=GO:%s"});\n' % (
        value.go_id, value.name, value.idType, value.go_id )
        counter_create += 1
        f.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')

    f.write('commit \n begin \n')
    # make id unique
    f.write('Create Constraint On (node:CTDphenotype) Assert node.go_id Is Unique; \n')
    f.write('commit \n schema await \n begin \n')

    print('rel chemical phenotype side effects')
    print (datetime.datetime.utcnow())
    # add the causes relationships with phenotypes
    for key, value in dict__chemical_phenotype_side_effect.items():
        create_text = '''Match (n1:CTDchemical {chemical_id: "%s"}), (n2:CTDphenotype {go_id: "%s"}) Create (n1)-[:Causes{correlation: "%s", phenotypeActionDegreeType: "%s" , ctd_url:"http://ctdbase.org/detail.go?type=chem&acc=%s"}]->(n2); \n''' % (
        value.chemical_id, value.go_id, value.correlation, value.phenotypeActionDegreeType, value.chemical_id)

        counter_create += 1
        f.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')

    print('rel chemical disease syntome')
    print (datetime.datetime.utcnow())
    # add causes relationship with disease
    for key, value in dict__chemical_disease_side_effect.items():
        create_text = '''Match (n1:CTDchemical {chemical_id: "%s"}), (n2:CTDdisease {disease_id: "%s"}) Create (n1)-[:Causes{correlation: "%s", ctd_url:"http://ctdbase.org/detail.go?type=chem&acc=%s"}]->(n2); \n''' % (
        value.chemical_id, value.disease_id, value.correlation, value.chemical_id)

        counter_create += 1
        f.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')

    print('rel chemical disease')
    print (datetime.datetime.utcnow())
    # add therapeutic and marker/mechanism relationships
    for key, value in dict_edge_chemical_disease.items():
        create_text = '''Match (n1:CTDchemical {chemical_id: "%s"}), (n2:CTDdisease {disease_id: "%s"})  Create (n1)-[:Association{directEvidence: "%s", inferenceGeneSymbol: "%s",inferenceScore: "%s" ,pubMedIDs: "%s", ctd_url:"http://ctdbase.org/detail.go?type=chem&acc=%s"}]->(n2); \n''' % (
        value.chemical_id, value.disease_id, value.directEvidence, value.inferenceGeneSymbol, value.inferenceScore,
        value.pubMedIDs, value.chemical_id)

        counter_create += 1
        f.write(create_text)
        # test if a new commit block or new file need to be generated
        if counter_create % constrain_number == 0:
            f.write('commit \n')
            if counter_create % creation_max_in_file == 0:
                f.close()
                f = open('CTD_database_' + str(i) + '.cypher', 'w', encoding="utf-8")
                f.write('begin \n')
                i += 1
            else:
                f.write('begin \n')

    f.write('commit')


def main():
    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('get_chemical event relation')

    get_chemical_event_relation()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('get_chemical disease relation')
    get_chemical_disease_associations()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('get_chemical informtation')
    more_information_for_chemical()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    print('get_disease informtation')
    more_information_for_disease()

    # print('#############################################################')
    # print (datetime.datetime.utcnow())
    # print('generate csv')
    # generate_csv()

    print('#############################################################')
    print (datetime.datetime.utcnow())
    generate_cypher_file_for_construction()


if __name__ == "__main__":
    # execute only if run as a script
    main()
