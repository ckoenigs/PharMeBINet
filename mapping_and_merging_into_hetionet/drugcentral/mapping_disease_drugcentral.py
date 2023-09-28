import datetime
import csv
import sys
from collections import defaultdict

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create a connection with neo4j
    :return:
    """
    # set up authentication parameters and connection
    global graph_database, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    graph_database = driver.session()


# dictionary for map to disease
dict_disease_doid = {}
dict_disease_umls_cui = {}
dict_disease_set_id = {}
dict_disease_mesh_id = {}
dict_disease_nci_id = {}
dict_disease_omim_id = {}
dict_disease_ordo_id = {}
dict_disease_icd10_id = {}
dict_diseaseId_to_resource = {}
dict_disease_name = {}

# dictionary to map to symptom
dict_symptomId_to_resource = {}
dict_symptom_umls_cui = {}
dict_symptom_set_id = {}
dict_symptom_mesh_id = {}
dict_symptom_name = {}

dict_disease_mapping = defaultdict(dict)
dict_symptom_mapping = defaultdict(dict)
dict_doi_disease_mapping = defaultdict(dict)
dict_doi_symptom_mapping = defaultdict(dict)


def load_disease_in():
    """
    Load disease nodes and write information into dictionaries
    :return:
    """
    # query ist ein String
    query = '''MATCH (n:Disease) RETURN n'''
    # graph_database.run(query) führt den Befehl aus query aus, Ergebnisse sind in results als Liste gespeichert
    results = graph_database.run(query)

    # results werden einzeln durchlaufen
    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]

        xrefs = node["xrefs"] if "xrefs" in node else []
        dis_name = node["name"] if "name" in node else []
        names = node["synonyms"] if "synonyms" in node else []

        if not names:
            names = [dis_name]
        else:
            names.append(dis_name)

        # im dictionary werden passend zu den Identifiern die Namen und die idOwns gespeichert
        dict_diseaseId_to_resource[identifier] = resource

        for ref in xrefs:
            # doid
            if ref.startswith("DOID"):
                doid_ref = ref.split(':')
                if doid_ref[1] not in dict_disease_doid:
                    dict_disease_doid[doid_ref[1]] = set()
                dict_disease_doid[doid_ref[1]].add(identifier)

            # umls_cui
            if ref.startswith("UMLS"):
                uc_ref = ref.split(':')
                if uc_ref[1] not in dict_disease_umls_cui:
                    dict_disease_umls_cui[uc_ref[1]] = set()
                dict_disease_umls_cui[uc_ref[1]].add(identifier)

            # snomed ID
            if ref.startswith("SCTID"):
                sct_ref = ref.split(':')
                if sct_ref[1] not in dict_disease_set_id:
                    dict_disease_set_id[sct_ref[1]] = set()
                dict_disease_set_id[sct_ref[1]].add(identifier)

            # MESH
            if ref.startswith("MESH"):
                mesh_ref = ref.split(':')
                if mesh_ref[1] not in dict_disease_mesh_id:
                    dict_disease_mesh_id[mesh_ref[1]] = set()
                dict_disease_mesh_id[mesh_ref[1]].add(identifier)

            # NCI
            if ref.startswith("NCI"):
                nci_ref = ref.split(':')
                if nci_ref[1] not in dict_disease_nci_id:
                    dict_disease_nci_id[nci_ref[1]] = set()
                dict_disease_nci_id[nci_ref[1]].add(identifier)

            # OMIM
            if ref.startswith("OMIM"):
                omim_ref = ref.split(':')
                if omim_ref[1] not in dict_disease_omim_id:
                    dict_disease_omim_id[omim_ref[1]] = set()
                dict_disease_omim_id[omim_ref[1]].add(identifier)

            if ref.startswith("OMIMPS"):
                omim_ref = ref.split(':')
                if omim_ref[1] not in dict_disease_omim_id:
                    dict_disease_omim_id[omim_ref[1]] = set()
                dict_disease_omim_id[omim_ref[1]].add(identifier)

            # ORDO
            if ref.startswith("Orphanet"):
                ordo_ref = ref.split(':')
                if ordo_ref[1] not in dict_disease_ordo_id:
                    dict_disease_ordo_id[ordo_ref[1]] = set()
                dict_disease_ordo_id[ordo_ref[1]].add(identifier)

            # ICD10
            if ref.startswith("ICD10"):
                icd10_ref = ref.split(':')
                if icd10_ref[1] not in dict_disease_icd10_id:
                    dict_disease_icd10_id[icd10_ref[1]] = set()
                dict_disease_icd10_id[icd10_ref[1]].add(identifier)

        # name
        for name in names:
            name = name.lower()
            d_name = name.split('[')
            if d_name[0] not in dict_disease_name:
                dict_disease_name[d_name[0]] = set()
            dict_disease_name[d_name[0]].add(identifier)


def load_symptom_in():
    """
    Load symptoms and write information into dictionaries
    :return:
    """
    query = '''MATCH (n:Symptom) RETURN n'''
    results = graph_database.run(query)

    for record in results:
        node = record.data()['n']
        identifier = node["identifier"]
        resource = node["resource"]
        sym_name = node["name"]
        names = node["synonyms"] if "synonyms" in node else []

        if not names:
            names = [sym_name]
        else:
            names.append(sym_name)

        xrefs = node["xrefs"] if "xrefs" in node else []
        dict_symptomId_to_resource[identifier] = resource

        for ref in xrefs:
            # umls_cui
            if ref.startswith("UMLS"):
                uc_ref = ref.split(':')
                if uc_ref[1] not in dict_symptom_umls_cui:
                    dict_symptom_umls_cui[uc_ref[1]] = set()
                dict_symptom_umls_cui[uc_ref[1]].add(identifier)

            # snomed ID
            if ref.startswith("SNOMEDCT_US"):
                sct_ref = ref.split(':')
                if sct_ref[1] not in dict_symptom_set_id:
                    dict_symptom_set_id[sct_ref[1]] = set()
                dict_symptom_set_id[sct_ref[1]].add(identifier)

            # mesh
            if ref.startswith("MESH"):
                mesh_ref = ref.split(':')
                if mesh_ref[1] not in dict_symptom_mesh_id:
                    dict_symptom_mesh_id[mesh_ref[1]] = set()
                dict_symptom_mesh_id[mesh_ref[1]].add(identifier)

        # name
        for name in names:
            name = name.lower()
            if name not in dict_symptom_name:
                dict_symptom_name[name] = set()

            dict_symptom_name[name].add(identifier)


def load_omopConcept_in():
    query = '''MATCH (n:DC_OMOPConcept) RETURN n, id(n)'''
    results = graph_database.run(query)

    mapped_diseases = set()
    mapped_symptoms = set()

    for record in results:
        node = record.data()['n']
        node_id = record.data()['id(n)']
        umls_cui = node["umls_cui"] if "umls_cui" in node else ""
        concept_id = node['concept_id']
        is_mapped = False
        # 40249495 got a wrong umls cui
        if umls_cui and concept_id != '40249495':

            # mapping to disease
            if umls_cui in dict_disease_umls_cui:
                is_mapped = True
                diseases = dict_disease_umls_cui[umls_cui]
                for disease_id in diseases:
                    if node_id not in dict_disease_mapping[node_id]:
                        dict_disease_mapping[node_id][disease_id] = set()
                    dict_disease_mapping[node_id][disease_id].add('umls_cui')
                    mapped_diseases.add(node_id)

            if is_mapped:
                continue

            if umls_cui in dict_symptom_umls_cui:
                is_mapped = True
                symptoms = dict_symptom_umls_cui[umls_cui]
                for symptom_id in symptoms:
                    if node_id not in dict_symptom_mapping[node_id]:
                        dict_symptom_mapping[node_id][symptom_id] = set()
                    dict_symptom_mapping[node_id][symptom_id].add('umls_cui')
                    mapped_symptoms.add(node_id)
        if is_mapped:
            continue

        sct_id = node["snomed_concept_id"] if "snomed_concept_id" in node else ""
        if sct_id:

            if sct_id in dict_disease_set_id:
                is_mapped = True
                diseases = dict_disease_set_id[sct_id]
                for disease_id in diseases:
                    if node_id not in dict_disease_mapping[node_id]:
                        dict_disease_mapping[node_id][disease_id] = set()
                    dict_disease_mapping[node_id][disease_id].add('sct_id')
                    mapped_diseases.add(node_id)

            if is_mapped:
                continue

            if sct_id in dict_symptom_set_id:
                is_mapped = True
                symptoms = dict_symptom_set_id[sct_id]
                for symptom_id in symptoms:
                    if node_id not in dict_symptom_mapping[node_id]:
                        dict_symptom_mapping[node_id][symptom_id] = set()
                    dict_symptom_mapping[node_id][symptom_id].add('sct_id')
                    mapped_symptoms.add(node_id)
        if is_mapped:
            continue

        disease_name = node["concept_name"].lower()

        if disease_name in dict_disease_name:
            is_mapped = True
            diseases = dict_disease_name[disease_name]
            for disease_id in diseases:
                if node_id not in dict_disease_mapping[node_id]:
                    dict_disease_mapping[node_id][disease_id] = set()
                dict_disease_mapping[node_id][disease_id].add('name')
                mapped_diseases.add(node_id)

            if is_mapped:
                continue

        # mapping to symptome

        if disease_name in dict_symptom_name:
            is_mapped = True
            symptoms = dict_symptom_name[disease_name]
            for symptom_id in symptoms:
                if node_id not in dict_symptom_mapping[node_id]:
                    dict_symptom_mapping[node_id][symptom_id] = set()
                dict_symptom_mapping[node_id][symptom_id].add('name')
                mapped_symptoms.add(node_id)

        if not is_mapped:
            csv_not_mapped.writerow([node_id, umls_cui, sct_id, disease_name])

    for node_id in mapped_diseases:
        for disease_id in dict_disease_mapping[node_id]:
            methodes = list(dict_disease_mapping[node_id][disease_id])
            methodes = '|'.join(methodes)
            resource = set(dict_diseaseId_to_resource[disease_id])
            csv_mapped.writerow(
                [node_id, disease_id, pharmebinetutils.resource_add_and_prepare(resource, 'DrugCentral'), methodes])

    for node_id in mapped_symptoms:
        for symptom_id in dict_symptom_mapping[node_id]:
            methodes = list(dict_symptom_mapping[node_id][symptom_id])
            methodes = '|'.join(methodes)
            resource = set(dict_symptomId_to_resource[symptom_id])
            csv_mapped_sym.writerow(
                [node_id, symptom_id, pharmebinetutils.resource_add_and_prepare(resource, 'DrugCentral'), methodes])


dict_doTermID_to_xref = defaultdict(lambda: defaultdict(set))


def load_DOTerm_xref_in():
    query = '''MATCH (n:DC_DOTermXref)--(m:DC_DOTerm) RETURN id(m), n.source, n.xref'''
    results = graph_database.run(query)

    for record in results:
        doTerm_id = record.data()['id(m)']
        xref_source = record.data()['n.source']
        xref_identifier = record.data()['n.xref']
        dict_doTermID_to_xref[doTerm_id][xref_source].add(xref_identifier)


def load_DOTerm_in():
    query = '''MATCH (n:DC_DOTerm) RETURN id(n), n'''
    results = graph_database.run(query)

    mapped_diseases = set()
    mapped_symptoms = set()

    for record in results:
        identifier = record.data()['id(n)']
        node = record.data()['n']
        doid = node["doid"]
        doid_id = doid.split(':')[1]

        if doid_id in dict_disease_doid:
            doids = dict_disease_doid[doid_id]
            for doid in doids:
                if identifier not in dict_doi_disease_mapping[identifier]:
                    dict_doi_disease_mapping[identifier][doid] = set()
                dict_doi_disease_mapping[identifier][doid].add('doid')
                mapped_diseases.add(identifier)

        # xref
        xrefs = dict_doTermID_to_xref[identifier]
        for xref in xrefs:

            # umls
            if xref == 'UMLS_CUI':
                umls_cuis = dict_doTermID_to_xref[identifier][xref]
                for umls_cui in umls_cuis:
                    if umls_cui in dict_disease_umls_cui:
                        diseases = dict_disease_umls_cui[umls_cui]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('umls_cui')
                            mapped_diseases.add(identifier)

                    elif umls_cui in dict_symptom_umls_cui:
                        symptoms = dict_symptom_umls_cui[umls_cui]
                        for symptom_id in symptoms:
                            if identifier not in dict_doi_symptom_mapping[identifier]:
                                dict_doi_symptom_mapping[identifier][symptom_id] = set()
                            dict_doi_symptom_mapping[identifier][symptom_id].add('umls_cui')
                            mapped_symptoms.add(identifier)

            # snomed
            if xref == 'SNOMEDCT_US_2019_09_01':
                sct_ids = dict_doTermID_to_xref[identifier][xref]
                for sct_id in sct_ids:
                    if sct_id in dict_disease_set_id:
                        diseases = dict_disease_set_id[sct_id]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('sct_id')
                            mapped_diseases.add(identifier)

                    elif sct_id in dict_symptom_set_id:
                        symptoms = dict_symptom_set_id[sct_id]
                        for symptom_id in symptoms:
                            if identifier not in dict_doi_symptom_mapping[identifier]:
                                dict_doi_symptom_mapping[identifier][symptom_id] = set()
                            dict_doi_symptom_mapping[identifier][symptom_id].add('sct_id')
                            mapped_symptoms.add(identifier)

            # mesh
            if xref == 'MESH':
                mesh_ids = dict_doTermID_to_xref[identifier][xref]
                for mesh_id in mesh_ids:
                    if mesh_id in dict_disease_mesh_id:
                        diseases = dict_disease_mesh_id[mesh_id]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('mesh')
                            mapped_diseases.add(identifier)

                    elif mesh_id in dict_symptom_mesh_id:
                        symptoms = dict_symptom_mesh_id[mesh_id]
                        for symptom_id in symptoms:
                            if identifier not in dict_doi_symptom_mapping[identifier]:
                                dict_doi_symptom_mapping[identifier][symptom_id] = set()
                            dict_doi_symptom_mapping[identifier][symptom_id].add('mesh')
                            mapped_symptoms.add(identifier)
            # nci
            if xref == 'NCI':
                nci_ids = dict_doTermID_to_xref[identifier][xref]
                for nci_id in nci_ids:
                    if nci_id in dict_disease_nci_id:
                        diseases = dict_disease_nci_id[nci_id]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('nci')
                            mapped_diseases.add(identifier)

            # omim
            if xref == 'OMIM':
                omim_ids = dict_doTermID_to_xref[identifier][xref]
                for omim_id in omim_ids:
                    if omim_id in dict_disease_omim_id:
                        diseases = dict_disease_omim_id[omim_id]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('omim')
                            mapped_diseases.add(identifier)

            # ordo
            if xref == 'ORDO':
                ordo_ids = dict_doTermID_to_xref[identifier][xref]
                for ordo_id in ordo_ids:
                    if ordo_id in dict_disease_ordo_id:
                        diseases = dict_disease_ordo_id[ordo_id]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('ordo')
                            mapped_diseases.add(identifier)

            # icd10
            if xref == 'ICD10CM':
                icd10_ids = dict_doTermID_to_xref[identifier][xref]
                for icd10_id in icd10_ids:
                    if icd10_id in dict_disease_icd10_id:
                        diseases = dict_disease_icd10_id[icd10_id]
                        for disease_id in diseases:
                            if identifier not in dict_doi_disease_mapping[identifier]:
                                dict_doi_disease_mapping[identifier][disease_id] = set()
                            dict_doi_disease_mapping[identifier][disease_id].add('icd10')
                            mapped_diseases.add(identifier)

        if identifier not in mapped_diseases:
            csv_not_mapped_doid.writerow([identifier, doid_id])

    for node_id in mapped_diseases:
        for disease_id in dict_doi_disease_mapping[node_id]:
            methodes = list(dict_doi_disease_mapping[node_id][disease_id])
            methodes = '|'.join(methodes)
            resource = set(dict_diseaseId_to_resource[disease_id])
            csv_mapped_doid.writerow(
                [node_id, disease_id, pharmebinetutils.resource_add_and_prepare(resource, 'DrugCentral'), methodes])

    for node_id in mapped_symptoms:
        for symptom_id in dict_doi_symptom_mapping[node_id]:
            methodes = list(dict_doi_symptom_mapping[node_id][symptom_id])
            methodes = '|'.join(methodes)
            resource = set(dict_symptomId_to_resource[symptom_id])
            csv_mapped_doid_sym.writerow(
                [node_id, symptom_id, pharmebinetutils.resource_add_and_prepare(resource, 'DrugCentral'), methodes])


# file for mapped or not mapped identifier
# erstellt neue TSV, überschreibt auch bestehende und leert sie wieder
file_not_mapped_disease = open('disease/not_mapped_disease.tsv', 'w', encoding="utf-8")
file_not_mapped_doid_disease = open('disease/not_mapped_doid_disease.tsv', 'w', encoding="utf-8")
csv_not_mapped = csv.writer(file_not_mapped_disease, delimiter='\t', lineterminator='\n')
csv_not_mapped_doid = csv.writer(file_not_mapped_doid_disease, delimiter='\t', lineterminator='\n')
# Header setzen
csv_not_mapped.writerow(['id', 'umls_cui', 'sct_id', 'name'])
csv_not_mapped_doid.writerow(['id', 'doid'])

file_name_mapped_disease = 'disease/mapped_disease.tsv'
file_mapped_disease = open(file_name_mapped_disease, 'w', encoding="utf-8")
csv_mapped = csv.writer(file_mapped_disease, delimiter='\t', lineterminator='\n')
csv_mapped.writerow(['id', 'id_hetionet', 'resource', 'how_mapped'])

file_name_mapped_disease_doi = 'disease/mapped_doid_disease.tsv'
file_mapped_doid = open(file_name_mapped_disease_doi, 'w', encoding="utf-8")
csv_mapped_doid = csv.writer(file_mapped_doid, delimiter='\t', lineterminator='\n')
csv_mapped_doid.writerow(['id', 'id_hetionet', 'resource', 'how_mapped'])

file_name_mapped_symptom = 'disease/mapped_symptom.tsv'
file_mapped_symptom = open(file_name_mapped_symptom, 'w', encoding="utf-8")
csv_mapped_sym = csv.writer(file_mapped_symptom, delimiter='\t', lineterminator='\n')
csv_mapped_sym.writerow(['id', 'id_hetionet', 'resource', 'how_mapped'])

file_name_mapped_symptom_doid = 'disease/mapped_doid_symptom.tsv'
file_mapped_doid_symptom = open(file_name_mapped_symptom_doid, 'w', encoding="utf-8")
csv_mapped_doid_sym = csv.writer(file_mapped_doid_symptom, delimiter='\t', lineterminator='\n')
csv_mapped_doid_sym.writerow(['id', 'id_hetionet', 'resource', 'how_mapped'])


def generate_cypher_file(file_name_term, file_name_concept, label):
    """
    prepare cypher query and add to cypher file
    :param file_name: string
    :param label: string
    :return:
    """
    cypher_file = open('output/cypher.cypher', 'a')

    query = f' MATCH (n:DC_OMOPConcept), (c:{label}{{identifier:line.id_hetionet}}) Where ID(n)= ToInteger(line.id)  Set c.drugcentral="yes", c.resource=split(line.resource,"|") Create (c)-[:equal_to_{label}_drugcentral{{how_mapped:line.how_mapped}}]->(n)'
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/" + file_name_concept,
                                              query)
    cypher_file.write(query)

    query = f' MATCH (n:DC_DOTerm), (c:{label}{{identifier:line.id_hetionet}}) Where ID(n)= ToInteger(line.id)  Set c.drugcentral="yes", c.resource=split(line.resource,"|") Create (c)-[:equal_to_{label}_drugcentral{{how_mapped:line.how_mapped}}]->(n)'''
    query = pharmebinetutils.get_query_import(path_of_directory,
                                              "mapping_and_merging_into_hetionet/drugcentral/" + file_name_term,
                                              query)
    cypher_file.write(query)
    cypher_file.close()


def main():
    global path_of_directory
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path dc disease')
    print(datetime.datetime.utcnow())
    print('Generate connection with neo4j and mysql')

    create_connection_with_neo4j()
    print("load disease in")
    load_disease_in()
    print("load symptom in")
    load_symptom_in()
    print("load omop_concept")
    load_omopConcept_in()
    print("load doid in")
    load_DOTerm_xref_in()
    load_DOTerm_in()
    print(
        '###########################################################################################################################')

    generate_cypher_file(file_name_mapped_disease_doi, file_name_mapped_disease, "Disease")
    generate_cypher_file(file_name_mapped_symptom_doid, file_name_mapped_symptom, "Symptom")

    print(datetime.datetime.utcnow())


if __name__ == "__main__":
    # execute only if run as a script
    main()
