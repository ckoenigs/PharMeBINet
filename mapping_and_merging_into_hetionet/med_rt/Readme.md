The MED-RT script contains a lot of mapping scripts to merge the information into the database and also prepare the relationships for integration.


First, integrate from MED-RT Additional_Pharmacologic_Classes_MEDRT, FDA_Established_Pharmacologic_Classes_MEDRT, Mechanisms_of_Action_MEDRT, Physiologic_Effects_MEDRT, Pharmacokinetics_MEDRT and Therapeutic_Categories_MEDRT as Pharmacological Class (PC):
    First, cypher files are generated one for mapping and one for the edges. A cypher query is added to remove all PC nodes in the mapping cypher.
    Then, for each Med-RT label, the following steps were executed:
        First, generate a TSV file and add a cypher query to integrate these nodes.
        Then, load all nodes and fill the TSV file.
        Next, for each label combination, a TSV file and a cypher query are prepared for the parent of edges.
        In the last step, all pairs are loaded in written into the TSV file.

Then, the MED-RT chemical ingredients are mapped to the chemical.
    First, all important information for the mapping is extracted from chemicals and saved into different dictionaries.
    Then, a mapping TSV file is generated and a mapping cypher is added to the cypher file.
    Next, all med-rt chemical ingredients are loaded and mapped to chemical:
        The first mapping method uses the xref mesh ID and maps it to the chemical xref mesh ID.
        Next mapping is xref RxNorm id to chemical xref RxNorm id.
        Then, there is a manual mapping.
        Next, is the mapping between the RxNorm identifier to chemical xref RxNorm id.
        The following mapping is between name and chemical name/synonym.
        If they are still not mapped and have the xref mesh it tries to get a real mesh ID from RxNorm, because some mesh are SCUI IDs and not the normal Mesh ID. With the new mesh ID, it is tried to map to the chemical xref mesh.
        If this did not work it tried to map with the RxNorm ID from RxNorm to the xrefs of chemical.
        The following is mapping with the use of the RxNorm IDs from RxNorm and getting in RxNorm the drugbank ID. With the DrugBank ID, it is mapped to the chemical identifier.
        The xref with RxNorm ID tried to get the names from RxNorm and map the names to the names/synonyms of chemicals.
        Next, the synonyms are mapped to the chemical name/synonyms.
        In the case of a mesh xref which had RxNorm CUIs from RxNorm, it tried to get the RxNorm name and map it to the name/synonyms of the chemical.
        The last mapping method is for mesh it tries to get the rxnorm id from rxnorm with the name and map it to the xref rxnrom id of the chemical.
    All mapping pairs are written into the TSV file.


Next, the MED-RT other node is mapped to chemical:
    First, load all chemical information and write them into dictionaries.
    Next, a mapping TSV and cypher query are generated. The cypher query is written into the cypher file.
    Then, the other nodes are loaded and mapped to chemical:
        The first mapping method is with name to name/synonym of chemicals.
        The next mapping is with mesh id to mesh xref mesh id of chemical.
    All mapping pairs are written into the TSV file.

The following mapping is between MED-RT disease-finding/other and disease/symptom:
    First, load disease/symptom information and save it in dictionaries.
    Next, for disease finding/other are the following steps:
        First, generate mapping files for disease and symptom mapping with the additional mapping cypher queries which are added to the cypher file.
        Next, all nodes are loaded and mapped to disease/symptom:
            The first mapping is with name to name/synonym of disease.
            Next, with the name it is tried to get the UMLS CUI from UMLS and map it to disease xref UMLS cui.
            Then, it is mapped with name to name/synonyms of symptom.
            In the following, the mesh xref is mapped to the symptom xref mesh id.
            the last mapping method is using the umls cuis from umls and mapping with them to symptom xref umls cui.

Next, the cypher queries of the cypher mapping file are executed with Neo4j cypher-shell.

Then, the MED-RT chemical-PC edges are added:
    For MED-RT chemical ingredients/others are the following steps:
        For both directed edges all relationships of MED-RT between chemical and PC are loaded. It ignores self-loops.
        For each relationship type a TSV file is generated and a dictionary.
        Each edge is added to the dictionary of the same edge type, label, and direction.
        In the end, it runs through the dictionary and prepares the information, and writes it into the different TSV files.

Next, the MED-RT chemical-chemical edges are merged:
    First, load existing interaction relationship pairs and write information into dictionaries.
    Then, for chemical ingredients/others the following steps were executed:
        Load all chemical-chemical pairs with relationship information.
        Create for each relationship type own TSV file and add a cypher query to the cypher file and a dictionary.
        At each pair to the dictionary of the same relationship type.
        Afterward, pairs of dictionaries are checked if they are in the interaction list or not, and the information is combined and written into the TSV files.

The last program merges disease-chemical/pc edges:
    For chemical ingredients and FDA_Established_Pharmacologic_Classes_MEDRT of med-rt, the following steps are executed:
        For each label and relationship type a TSV, a cypher query, and a dictionary them is generated.
        Each pair is added to the different dictionaries.
        In the end, the different dictionaries are iterated, and written the combined information in the different TSV files.

In the last step, execute the cypher file with all relationships with Neo4j cypher-shell.

