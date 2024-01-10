There is a script to merge DrugCentral into PharMeBINet.

First, the DrugCentral DC_Products are mapped to Product.
    First, the TSV files for mapped and not mapped nodes are prepared. Also, the cypher query is generated and added to the cypher file.
    Next, the Product nodes are loaded and the information is written into a dictionary.
    Then, the DC_Products are loaded and mapped with NDC identifiers. The mapped and not mapped nodes are written into the TSV files.

Next, a mapping between Target/bioactivity and protein takes place: 
    First, all mapping TSV files are generated.
    Second, all protein nodes are loaded and written into dictionaries.
    Next, all bioactivity nodes are loaded and mapped  (all mapping method were use at the same time):
        They are mapped with DC bioactivity accession to protein name and/or with DC swissprot to protein entry name.
    All mapping pairs are written into the TSV file.
    Then, the targetComponents are loaded and mapped  (all mapping method were use at the same time):
        They are mapped with DC targetComponent accessions to protein name and/or with DC swissprot to protein entry name.
    All mapping pairs are written into the TSV file.
    In the last step, the cypher queries are prepared and add to the cypher file.


Then, the DrugCentral DC_GOTerm are mapped to Biological Process (BP), Molecular Function (MF), and Cellular Component (CC).
    First, for every mapping, a TSV file is prepared.
    Then, the BP, CC, and MF data are loaded from Neo4j and their information is written into dictionaries.
    Next, the DC_GOTerms are loaded. Then based on their type (P[BP], C[CC], F[MF]) they are mapped to BP, MF, CC with GO identifier to GO identifier or alternative GO identifier. Then, the mapped pairs are written into the different TSV files.
    In the last step, the different cypher queries are generated and written into the cypher file.

in the following, the DrugCentral DC_structures and DC_ParentDrugMolecules are mapped to chemicals:
    First, the TSV files for mapped and not mapped nodes are prepared.
    Next, the chemicals nodes are loaded and the information is written into a dictionaries.
    In the following, the xref of structur are loaded from the connetion to DC-identifier. The information is written into dictionaries.
    Then, the DC_structurs are loaded and mapped to chemicals:
        The first mapping is between structure inchikey and chemical inchikey.
        Next, is the mapping between SMILEs and chemical SMILES.
        Then, the structure name is mapped to chemical name.
        The last mapping is between name and chemical synonyms.
    The mapped and not mapped nodes are written into the TSV files.
    Next, the DC_ParentDrugMolecules are loaded and mapped to chemicals:
        The first mapping method is between DC_ParentDrugMolecule inchi and chemical inchi.
        The second mapping method is between DC_ParentDrugMolecule inchikey and chemical inchikey.
        Next, is the mapping between SMILES and chemical SMILES.
        The last mapping is with name to chemical name.
    The mapped and not mapped nodes are written into the TSV files.
    Also, the cypher queries are generated and added to the cypher file.

First, the DrugCentral DC_PharmaClasses are mapped to Pharmacological class (PC):
    First, the TSV files for mapped and not mapped nodes are prepared. 
    Next, the PC nodes are loaded and the information is written into dictionaries.
    Then, the DC_PharmaClass (exclude the FDA because they are already integrated with this pipeline and might be more up-to-date than them) are loaded and mapped to PC (all mapping methods were used at the same time):
        It maps with DC_PharmaClass source MESH the code (Mesh ID) to PC xref Mesh ID.
        Also, with the source FDA, the code is mapped to the PC identifier.
        Additionally, the name is mapped to the PC name.
        The last mapping method is using the synonyms to map to the PC name.
    The mapped and not mapped nodes are written into the TSV files.
    Also, the cypher query is generated and added to the cypher file.

First, the DrugCentral DC_ATC are mapped to Pharmacological class (PC):
    First, the TSV files for mapped and not mapped nodes are prepared. 
    Next, the PC nodes are loaded and the information is written into a dictionaries.
    Then, the DC_ATC are loaded and mapped to PC:
        First, it map with DC_ATC code (ATC-code) to PC ATC-codes.
        Next, map with name to name/synonym of PC.
    The mapped and not mapped nodes are written into the TSV files.
    Also, the cypher query is generated and added to the cypher file.

First, the DrugCentral DC_OMOPConcepts are mapped to disease/symptom:
    First, the TSV files for mapped and not mapped nodes are prepared. 
    Next, the disease and symptoms nodes are loaded and the information is written into dictionaries.
    Then, the DC_OMOPConcept are loaded and mapped to disease/symptom:
        The first mapping is with UMLS CUI to disease UMLS CUI.
        Next, the UMLS CUI is mapped to the symptom xref UMLS CUI.
        Then, the SNOMED ID is mapped to the disease xref SNOMED ID.
        The SNOMED ID is mapped to the symptom xref SNOMED ID.
        Next, the concept-name is mapped to disease name/synonyms.
        The last mapping method is the concept-name mapped to symptom name/synonyms.
    The mapped and not mapped nodes are written into the TSV files.
    # TODO other mapping
    Also, the cypher queries are generated and added to the cypher file.


The different mappings are merged into PharMeBINet with the Neo4j cypher-shell.

