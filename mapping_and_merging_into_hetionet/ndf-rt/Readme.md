The NDF-RT script contains a lot of mapping script merge the information into the database and also prepared the relationships for the integration.

First, the NDF-RT disease is mapped by disease and symptom.
    First, all information for mapping is loaded from NDF-RT disease, disease, and symptom.
        Then the first mapping is the NDF-RT disease external reference UMLS Cui and MESH id to disease external reference UMLS Cui and MESH id.
        The next mapping method is based on NDF-RT disease name to disease name and synonyms.
        The following mapping is with NDF-RT disease name to symptom name and synonyms.
        The last mapping method is the NDF-RT disease external reference UMLS Cui and MESH id to symptom external reference UMLS Cui and MESH id.
    In the last step, the cypher query that integrates NDF-RT information into the database is added to the cypher file.

Then, the NDF-RT drugs are mapped to the chemical.
    First, all important information for the mapping is extracted from chemicals. The UMLS Cuis are load from UMLS by their identifier.
    Then all important information for the mapping of the NDF-RT drugs is extracted. If a drug has no RxNorm Cui then they get the RxCui from RxNorm with the name.
    The first mapping is based on the external reference RxCui of chemical with the RxCui of external reference or RxNorm RxCui of NDF-RT drug.
    Next, with RxNorm the RxCui is mapped to DrugBank or MESH id of the chemical.
    Then they are mapped based on the UNII that are external references of NDF-RT drug and the UNII of Chemical.
    Next, the mapping table of RxCui to DrugBank from RxNorm to FDA UNII to DrugBank based on InChIKey and UNII is used.
    Then the mapping of NDF-RT drug name to chemical name, synonyms, and brands.
    The last mapping is UMLS CUI mapping based on NDF-RT external UMLS CUI to chemical UMLS Cuis of UMLS.
    In the last step, the cypher query for the mapping is generated and added to the cypher file. Also, the mapping TSV file is generated and filled with the pairs.

In the following, the NDF-RT ingredients are mapped to chemicals.
    First, the mapping TSV is generated, the fitting cypher query is created and added to the cypher file.
    The chemicals are loaded with the important information for mapping and get the UMLS Cuis from UMLS with DrugBank or MESH id.
    Next, the ingredients are extracted into the program. Also, they are mapped NDF-RT ingredient names to chemical names and synonyms. If this did not work then with NDF-RT ingredient synonyms to chemical name and synonyms.
    In the last step, all mapped pairs are written into the TSV file.
               

The last mapping, is the NDF-RT drug, mechanism of action, physiologic effect, and pharmacokinetics are mapped to pharmacological class.
    First, a query is added to the cypher file which deletes all PC from the database.
    Then for all of the labels (except for drug) the TSF file is generated. Additionally, the cypher query to integrate the information into the database is added to the cypher file. Then the information is loaded into the program and prepared to add to the TSV file.
    The drug is similar with the exception that the drug is also mapped to the other PC by name. So, instead of one TSV file, there are two one for mapped and one for new nodes.
               
Then the mapping information and new nodes are integrated into the database with the cypher-shell.

Next, the drug/PC-disease relationships are prepared for integration.
    For both labels, chemical and PC where the NDF-RT drug is mapped before the information of the relationship and the disease is extracted.
    For each relationship type an own TSV file is generated and an additional cypher query. Either the cypher query is a merge or a create depending if the relationship types already exist. All the pairs are written in the TSV files.

Then the relationships between chemical/PC and PC are prepared.
    For chemical and PC, the relationships between the mapped NDF-RT drug and NDF-RT mechanism of action/pharmacokinetics/physiologic effect/therapeutic category are extracted. For each relationship type, a new TSV file is generated and a fitting cypher query is added to the cypher file.
    All pairs are written into dictionaries for the different relationship types. After all pairs for one label, chemical or PC are extracted the information is written into the different TSV files.

The relationships of NDF-RT between drug and ingredients are prepared to chemical/PC and chemical.
    For chemical and PC, the NDF-RT drug-ingredient edges are extracted. For each edge type a TSV file is generated and a cypher query is added to the cypher file. 
    Each pair is added to one of the different TSV files.

In the last step, the relationship information is integrated with the cypher shell.
