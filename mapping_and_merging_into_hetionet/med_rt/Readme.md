The MED-RT script contains a lot of mapping script merge the information into the database and also prepared the relationships for the integration.


First, integrate from MED-RT Additional_Pharmacologic_Classes_MEDRT, FDA_Established_Pharmacologic_Classes_MEDRT, Mechanisms_of_Action_MEDRT, Physiologic_Effects_MEDRT, Pharmacokinetics_MEDRT and Therapeutic_Categories_MEDRT as Pharmacological Class (PC):
    First, cypher files are generated one for mapping and on for the edges. A cypher query is add to remove all PC nodes in the mapping cypher.
    Then, for each Med-RT label the following steps were executed:
        First, generate a TSV file and add a cypher query to integrate this nodes.
        Then, load all nodes and fill the TSV file.
        Next, for each labe combination a TSV file and a cypher query is prepared for the parent of edges.
        In the last step, all pairs are loaded in written into the TSV file.

Then, the MED-RT chemical ingredient are mapped to the chemical.
    First, all important information for the mapping is extracted from chemicals and saved into different dictionaries.
    Then, a mapping TSV file is generated and a mapping cypher is added to the cypher file.
    Next, all med-rt chemical ingredient are loaded and mapped to checmical:
        The first mapping method use the xref mesh id and map it to chemical xref mesh id.
        Next mapping is xref rxnorm id to chemical xref rxnorm id.
        Then, ther is a manual mapping.
        Next, is the mapping between the rxnorm identifier to chemical xref rxnorm id.
        The following mapping is between name and chemical name/synonym.
        If they still not mapped and have the xref mesh the it try to get a real mesh id from RxNorm, because some mesh are scui ids and not the normal Mesh id. With the new mesh id it is tried to map to the chemical xref mesh.
        If this did not work it tried to map with the rxnorm id from rxnorm to the xrefs of chemical.
        The following is mapping with use of the rxnorm ids from rxnorm and get in rxnorm the drugbank id. With the drugbank id it is mapped to the chemical identifier.
        The xref with rxnorm id tried to get the names from rxnorm and map the name to the name/synonyms of chemical.
        Next, the synonyms are maped to the chemical name/synonyms.
        In case of a mesh xref and it had rxnorm cuis from rxnorm the it try to get rxnorm name and map it to the name/synonyms of the chemical.
        The last mapping method is for mesh it rtry to get the rxnorm id from rxnorm with the name and map it to the xref rxnrom id of chemical.
    All mapping pairs are written into the TSV file.


Next, the MED-RT other node are mapped to chemical:
    First, load all chemicals information and write them into dictionaries.
    Next, a mapping TSV and cypher query are generated. The cypher query is written into the cypher file.
    Then, the other nodes are loaded and mapped to chemical:
        The first mapping method is with name to name/synonym of chemicals.
        The next mapping is with mesh id to mesh xref mesh id of chemical.
    All mapping pairs are written into the TSV file.

The following mapping is between MED-RT disease-finding/other and disease/symptom:
    First, load disease/symptom information ad save them in dictionries.
    Next, for disease finding/other are the following steps:
        First, generate mapping files for disease and symptom mapping with the additional mapping cypher queries which are add to the cypher file.
        Next, all nodes are loaded and are maped to disease/symptom:
            The first mappingt is with name to name/synonym of disease.
            Next, with name the it is tried to get the UMLS CUI from UMLS and map it to disease xref umls cui.
            Then, it is mapped with name to name/synonyms of symptom.
            In thefollowing, the mesh xref is mapped to the symptom xref mesh id.
            the last mapping method is using the umls cuis from umls and map with them to symptom xref umls cui.

Next, the cypher queries of the cypher mapping file are executed with Neo4j cypher-shell.

Then, the MED-RT chemical-PC edges are added:
    For MED-RT chemical ingredient/other are the folowwing steps:
        For both directed edges all relationships of MED-RT between chemical and PC are loaded. It ignore selfloops.
        For each relationship type a TSV file is generated and a dictionary.
        Each edge is add to the dictionary of the same edge type, label and direction.
        In the end it run through the dictionary and prepare the information and write it into the different TSV files.

Next, the MED-RT chemical-chemical edges are merged:
    First, load existing interaction relationship pairs and write infomration into dictionaries.
    Then, for chemical ingredient/other the folowing steps were executed:
        Load all chemical-chemical pair with relationship information.
        Create for each relationship type an own TSV file and add an additional cypher query to the cypher file and a dictionary.
        At each pair to the dictionary of the same relationship type.
        Afterwards, pairs of the dictionary are check if they are in the interaction list or not and the information are combined and written into the TSV files.

The last program merge disease-chemical/pc edges:
    For chemical ingredient and FDA_Established_Pharmacologic_Classes_MEDRT of med-rt the following steps are executed:
        For each label and relationship type a TSV, a cypher query and a dictionary for them is generated.
        The each pair is add to the different dictionaries.
        In the end, the different dictionaries are iterated and write the combined information in the different TSV files.

In the last step, execute the cypher file with all realtionships with Neo4j chypher-shell.

