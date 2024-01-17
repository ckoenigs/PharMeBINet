There is a script to merge DrugCentral into PharMeBINet.

First, the DrugCentral DC_Products are mapped to Product.
    First, the TSV files for mapped and not mapped nodes are prepared. Also, the cypher query is generated and added to the cypher file.
    Next, the Product nodes are loaded and the information is written into a dictionary.
    Then, the DC_Products are loaded and mapped with NDC identifiers. The mapped and not mapped nodes are written into the TSV files.

Next, a mapping between Target/bioactivity and protein takes place: 
    First, all mapping TSV files are generated.
    Second, all protein nodes are loaded and written into dictionaries.
    Next, all bioactivity nodes are loaded and mapped  (all mapping methods were used at the same time):
        They are mapped with DC bioactivity accession to the protein name and/or with DC SwissProt to the protein entry name.
    All mapping pairs are written into the TSV file.
    Then, the targetComponents are loaded and mapped  (all mapping methods were used at the same time):
        They have mapped with DC targetComponent accessions to protein name and/or with DC swissprot to protein entry name.
    All mapping pairs are written into the TSV file.
    In the last step, the cypher queries are prepared and added to the cypher file.


Then, the DrugCentral DC_GOTerms are mapped to Biological Process (BP), Molecular Function (MF), and Cellular Component (CC).
    First, for every mapping, a TSV file is prepared.
    Then, the BP, CC, and MF data are loaded from Neo4j and their information is written into dictionaries.
    Next, the DC_GOTerms are loaded. Then based on their type (P[BP], C[CC], F[MF]) they are mapped to BP, MF, CC with GO identifier to GO identifier or alternative GO identifier. Then, the mapped pairs are written into the different TSV files.
    In the last step, the different cypher queries are generated and written into the cypher file.

in the following, the DrugCentral DC_structures and DC_ParentDrugMolecules are mapped to chemicals:
    First, the TSV files for mapped and not mapped nodes are prepared.
    Next, the chemical nodes are loaded and the information is written into dictionaries.
    In the following, the xref of the structure is loaded from the connection to the DC-identifier. The information is written into dictionaries.
    Then, the DC_structurs are loaded and mapped to chemicals:
        The first mapping is between structure inchikey and chemical inchikey.
        Next, is the mapping between SMILEs and chemical SMILES.
        Then, the structure name is mapped to the chemical name.
        The last mapping is between name and chemical synonyms.
    The mapped and not mapped nodes are written into the TSV files.
    Next, the DC_ParentDrugMolecules are loaded and mapped to chemicals:
        The first mapping method is between DC_ParentDrugMolecule inchi and chemical inchi.
        The second mapping method is between DC_ParentDrugMolecule inchikey and chemical inchikey.
        Next, is the mapping between SMILES and chemical SMILES.
        The last mapping is with a name to chemical name.
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

First, the DrugCentral DC_ATCs are mapped to Pharmacological classes (PC):
    First, the TSV files for mapped and not mapped nodes are prepared. 
    Next, the PC nodes are loaded and the information is written into dictionaries.
    Then, the DC_ATC are loaded and mapped to PC:
        First, it maps with DC_ATC code (ATC-code) to PC ATC-codes.
        Next, map with name to name/synonym of PC.
    The mapped and not mapped nodes are written into the TSV files.
    Also, the cypher query is generated and added to the cypher file.

First, the DrugCentral DC_OMOPConcepts are mapped to disease/symptom:
    First, the TSV files for mapped and not mapped nodes are prepared. 
    Next, the disease and symptoms nodes are loaded and the information is written into dictionaries.
    Then, the DC_OMOPConcept is loaded and mapped to the disease/symptom:
        The first mapping is with UMLS CUI to disease UMLS CUI.
        Next, the UMLS CUI is mapped to the symptom xref UMLS CUI.
        Then, the SNOMED ID is mapped to the disease xref SNOMED ID.
        The SNOMED ID is mapped to the symptom xref SNOMED ID.
        Next, the concept-name is mapped to disease name/synonyms.
        The last mapping method is the concept-name mapped to symptom names/synonyms.
    The mapped and not mapped nodes are written into the TSV files.
    # TODO other mapping
    Also, the cypher queries are generated and added to the cypher file.


The different mappings are merged into PharMeBINet with the Neo4j cypher-shell.

The first edge program prepares a lot of different directed edges without information on the edge:
    First, a cypher file is generated, and a list with all edges that should be considered and their labels.
    For each edge entry, the following steps were executed:
        First, the TSV files and the additional cypher query are prepared and added. Also, existing pairs for this edge type are loaded into a dictionary.
        Next, all edge pairs of DC are loaded and written in the TSV file only for existing data are merged.

Next, the DC interaction edges are merged:
    First, existing drug-drug interaction pairs are loaded.
    Next, the TSV file is generated and the cypher query is added to the existing cypher file.
    Then, the interaction edges are loaded from DC:
        First, check if it is not a self-loop.
        Then, check if it is in the existing pairs, and if so write it into the TSV file.
        All the rest is written into the TSV file.

Then, the DC chemical-product edges are merged:
    First, load the existing edges into a dictionary.
    Next, the TSV files are generated and the cypher query is added to the existing cypher file.
    Then, the DC chemical-product edges connected through the node activeIngredient are loaded and written into a dictionary.
    In the following, the pairs are iterated and multiple pieces of information are merged and written into the TSV file.

The last program merges the DC chemical-protein edges:
    First, load, all DC action types for the DC bioactivity and written information into a dictionary.
    Next, all reference information of the DC bioactivity is loaded and written into a dictionary.
    Then, load all DC pairs where the act_source is not unknown, all edges are associates if they have no action type else it will renamed to the fitting edge type.
        Next, load the existing edge into a dictionary and generate TSV files and cypher queries to add to the cypher file.
        The pair's information is written into a dictionary.
    In the following, the DC edge pairs are iterated:
        First, it is checked if the pair exists in PharMeBINet. In this case, the DC information is merged, and then the information with PharMeBINet and written into the mapping TSV file.
        The not-mapping pairs get the edge information also merged and are written into the new TSV file.

The last step is the integration of the edge mapping into PharMeBINet with Neo4j cyher-shell and the cypher file.