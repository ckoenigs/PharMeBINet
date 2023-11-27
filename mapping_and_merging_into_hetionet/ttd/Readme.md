The script starts with TTD pathway mapping to the pathway:
    First, the mapping TSV file is generated.
    Then, all PharMeBINet pathways are loaded, and prepare different dictionaries.
    Next, the TTD pathways are loaded and tried to map:
        The first mapping is with the TTD id of the source Reactome/panther/wikipaths/pathwhiz to the xrefs of the pathways.
        Next, is the mapping with the name.
    All mapping pairs are written into the TSV file.
    In the last step, a cypher file with the additional cypher query is generated.

The next program mapped the TTD target to protein:
    In the first step, the protein information is loaded and written into different dictionaries.
    Next, load all gene-protein pairs to get a connection between gene symbol and protein.
    Then, the mapping TSV is generated, and the additional cypher query is added to the cypher file.
    In the last step, the TTD targets are loaded and mapped to protein:
        The first mapping is with the use of the UniProt accession to the protein entry name.
        The next mapping is using name mapping.
        The last mapping uses the TTD gene name to the gene symbol to protein.
    All mapping pairs are written into the TSV file.

The following program map TTD drug to Chemical:
    First, the Chemicals are loaded and the information is added to dictionaries.
    Then, the mapping TSV file is generated.
    Next, all TTD drugs which have a connection to another node are loaded and mapped:
        The first mapping method uses Inchikey mapping.
        Then it is mapped with SMILES.
        The next mapping is with PubChem CID to the xrefs of the chemical. But only entries are mapped where the name is not a combination of multiple drugs.
        The last mapping is with name mapping to the name/synonyms of the chemicals.
    All mapped nodes are written into the TSV file.
    From the not-mapped nodes, the ones with only one PubChem ID are added to a dictionary and got the synonyms from PubChem.
    Next, the cypher queries for the mapping and the newly generated nodes are prepared and added to the cypher file.
    In the last step, a TSV file is opened for the new nodes and the information from the dictionary is added to the TSV file.

The next program mapped the TTD compounds to chemicals:
    In the first step, the chemical information is loaded and written into different dictionaries.
    Then, the mapping TSV is generated.
    In the following step, the TTD compounds are loaded and mapped to chemical:
        The only mapping is with the PubChem CID to the xrefs of the chemical.
    All mapping pairs are written into the TSV file.
    In the last step, the cypher query is prepared and written into the cypher file.


The next program mapped the TTD disease to disease and symptoms:
    In the first step, the disease and symptom information are loaded and written into different dictionaries.
    Then, the mapping TSV files are generated.
    In the following step, the TTD diseases are loaded and mapped to disease/symptom:
        The first mapping method is with a name-to-disease name/synonyms.
        Next, mapping with name to symptom name/synonym.
        Then, the ICD11 ID is mapped to the xref icd11 ID of the disease.
        In the following, the ICD 10 id is mapped to the symptom xref ICD 10 id.
        The last mapping method is using the ICD9 ID to the xrefs ICD9 ID from the symptom.
    All mapping pairs are written into the different TSV files.
    In the last step, the cypher queries are prepared and written into the cypher file.


Then the cypher file is executed with Neo4j cypher-shell.

In the following, the chemical-disease-indicates are merged:
    First, the cypher file is generated.
    Then, the existing pairs are loaded and written into a dictionary.
    For disease/symptom first the TSV file and the cypher query is prepared and added to the cypher file.
    Next, all TTD edge information is loaded and checked if they exist or not and both are written into the same TSV file.

In the last program, chemical-target connections are merged into PharMeBINet:
    First, load moa to edge type file (manually defined) and add information into the dictionary.
    Next, load all protein-chemical pairs with the relationship information.
    Depending on the moa information they are added to the different dictionaries.
    Then, for each relationship type a TSV file is prepared and a cypher query is added to the cypher file.
    Additionally, the relationship information of a pair is combined and the information is written into the TSV file.

In the last step, the cypher queries are executed with the Neo4j cypher-shell.
