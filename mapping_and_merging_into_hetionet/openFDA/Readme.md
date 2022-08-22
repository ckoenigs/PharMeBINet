Only some parts of openFDA are merged into PharMeBINet.

The script first mapped the nodes and then integrate the edges into PharMeBINEt.

First, remove the existing create side effect file if exists. And generate a cypher file for integrating new side effects into PharMeBINet.

This is not used because no further information about CEARSReport is mapped.
    Next, CAERSReport_reaction_openFDA is mapped to side effect:
        First, the CAERSReport_reaction_openFDA infos are loaded and add a dictionary of name and identifier into a list
        Then, The side effects are loaded and written into a dictionary with name as key and id and resource in a list.
        Next, the tsv file is generated.
        Next, the nodes are mapped with name and written into the TSV file. The not mapped are written into another TSV file.
        In the following, a connection to MySQL UMLS is generated.
        All, CUI and STR are returned and prepared as a dictionary with STR as key and UMLS Cui as value. The not mapped entries are loaded from the TSV file.  Transform the dictionary name to id, resource in dictionary id to the resource. Next, all newly generated side effects are loaded from the newly created file. Next, the new creation SE file is open and if the file did not exists before a header is written. The mapped file is open with added information and not mapped is overwritten. 
            For every not mapped node, a UMLS CUI is searched.
            Depending if the UMLS CUI is in the existing SE  or not it is written into mapped or newly create SE.
            If the name is not in UMLS then the node is written into the not mapped file.
        In the last step, the cypher query to map the existing SE is added to the cypher file.

Next, DrugAdverseEvent_drug_openfda_openFDA is mapped to chemical and product:
    First, the DrugAdverseEvent_drug_openfda_openFDA are loaded and written into different lists (with name, synonym, and product NDC).
    Next, the chemical information is loaded and written into different dictionaries with name/synonym as key and id and resource as a list value.
    Then, the tsv files are generated.
    In the following the DrugAdverseEvent_drug_openfda_openFDA is mapped with is generical name to name and synonyms of Chemical. And the nodes are written in the mapping or not mapping file.
    Generate cypher query for the mapping between chemical and DrugAdverseEvent_drug_openfda_openFDA.
    Next, the products are loaded and generate a dictionary from NDC product code to id and resource.
    Then, the DrugAdverseEvent_drug_openfda_openFDA are mapped to Product with product NDC and written into the TSV file.
    Last, is the generation of cypher query for the mapping between DrugAdverseEvent_drug_openfda_openFDA and product.

Then, DrugAdverseEvent_drug_indication_openFDA is mapped to Disease and Symptom:
    First, the DrugAdverseEvent_drug_indication_openFDA are loaded and written into different lists (with name and synonym).
    Next, the disease information is loaded and written into different dictionaries with name/synonym/UMLS Cui as key and id and resource as a list value.
    Then, the tsv files are generated.
    In the following, the DrugAdverseEvent_drug_openfda_openFDA is mapped with its name to name and synonyms of disease. And the nodes are written in the mapping or not mapping file.
    Generate cypher query for the mapping between disease and DrugAdverseEvent_drug_indication_openFDA.
    Then, the DrugAdverseEvent_drug_indication_openFDA are loaded from the not mapped file and written into different lists (with name and synonym).
    Next, the Symptoms are loaded and generated a dictionary of name(synonym) to id and resource.
    Then, the tsv files  are generated for DrugAdverseEvent_drug_indication_openFDA-symptom mapping.
    Then, the DrugAdverseEvent_drug_indication_openFDA are mapped to symptoms with name and synonym and written into the TSV file.
    In the following, the cypher query for the mapping between DrugAdverseEvent_drug_indication_openFDA and symptom.
    Next, the not mapped DrugAdverseEvent_drug_indication_openFDA are loaded from the tsv file and written into dictionary name to id.
    Then,  all STR and CUI are loaded from MRCONSO (UMLS) and written into a dictionary name to id.
    Next, the not mapped DrugAdverseEvent_drug_indication_openFDA are mapped with name to UMLS CUI and then to Disease. The mappings are added to the existing mapping file. The not mapped nodes are written into a new not mapped file.

Next, DrugAdverseEvent_reaction_openFDA is mapped to side effect:
        First, the DrugAdverseEvent_reaction_openFDA information is loaded, and add a dictionary of name and identifier into a list
        Then, the side effects are loaded and written into a dictionary with name as key and id and resource in the list.
        Next, the tsv file is generated.
        Next, the nodes are mapped with name and written into the TSV file. The not mapped are written into another TSV file.
        In the following, a connection to MySQL UMLS is generated.
        All, CUI and STR are returned and prepared as a dictionary with STR as key and UMLS CUI as value. The not mapped entries are loaded from the TSV file.  Transform the dictionary name to id, resource in dictionary id to the resource. Next, all newly generated side effects are loaded from the newly created file. Next, the new creation SE file is open and if the file did not exists before a header is written. The mapped file is open with added information and not mapped is overwritten. 
            For every not mapped node, a UMLS CUI is searched.
            Depending if the UMLS CUI is in the existing SE  or not it is written into mapped or newly create SE.
            If the name is not in UMLS then the node is written into the not mapped file.
        In the last step, the cypher query to map the existing SE is added to the cypher file.    

By DrugRecallEnforcementReport only the openFDA could be mapped to Chemical, however, no interesting edge information can be extracted.
The same goes for NationalDrugCodeDirectory. The also is a mapping to Chemical possible.


Next, SubstanceData_openFDA is mapped to chemical:
    First, the SubstanceData_openFDA are loaded and written into different lists (with unii, SMILES, name, and synonym).
    Next, the chemical information is loaded and written into different dictionaries with name/synonym/unii/SMILES as key and id and resource as a list value.
    Then, the tsv files are generated.
    In the following the SubstanceData_openFDA is mapped with is unii, SMILES and name to name and synonyms of chemical. And the nodes are written in the mapping or not mapping file.
    Generate cypher query for the mapping between chemical and SubstanceData_openFDA.

Then, SubstanceData_relationships_substance_openFDA is mapped to chemical:
    First, the SubstanceData_relationships_substance_openFDA are loaded and written into different lists (with unii, name, and synonym).
    Next, the chemical information is loaded and written into different dictionaries with name/synonym/unii as key and id and resource as a list value.
    Then, the tsv files are generated.
    In the following the SubstanceData_relationships_substance_openFDA is mapped with is unii and name to name and synonyms of chemical. And the nodes are written in the mapping or not mapping file.
    Generate cypher query for the mapping between chemical and SubstanceData_relationships_substance_openFDA.

The mapping number from SubstanceData_substance_openFDA and SubstanceData_moieties_openFDA is low.

Then the cypher shell executes the cypher file for the node mappings.

Next, the edge preparation is executed.

First, the edges between chemicals indicate diseases from DrugAdverseEvent are prepared:
    First, 2 TSV files are prepared one for existing TREATS edges and one for new edges.
    Then, all chemical-treats-disease are loaded and written into a dictionary.
    Next, in batches, the indication information from DrugAdverseEvent is extracted. This include the chemical and disease id and node information of the connected path ((c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)<-[e3:Event]-(r:DrugAdverseEvent_drug_indication_openFDA)<-[e4:name_synonym_merge]-(s:Disease))
        Then the pair is checked if it exists or not and the information is written in the fitting TSV file.
    In the end, the cypher queries to update the existing treat edges and generate new treat edges are generated and written into a cypher file.
    
Then, the edges between chemicals indicate symptoms from DrugAdverseEvent are prepared:
    First, a TSV file is prepared for the new edges.
    Next, in batches, the indication information from DrugAdverseEvent is extracted. This include the chemical and symptom id and node information of the connected path ((c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)<-[e3:Event]-(r:DrugAdverseEvent_drug_indication_openFDA)<-[e4:name_synonym_merge]-(s:Symptom))
        Then the information is written in the fitting TSV file.
    In the end, the cypher queries to generate new treat edges are generated and written into a cypher file.
    
The next one generates edges between chemical-chemical from SubstanceData:
    First, all pairs with edge information are loaded.
        The edge has a type that is split into an edge type and additional edge information.
        For each edge type, a TSV file and cypher query are generated. And the edge information is written into the TSV file.

The last program is the preparation of chemical-side effect edges:
    First, a TSV file is prepared for the new edges.
    Next, in batches, the edge information from DrugAdverseEvent is extracted. This include the chemical and side effect id and node information (DrugAdverseEvent_openFDA) of the connected path ((c:Chemical)-[e1:name_synonym_merge]->(o:DrugAdverseEvent_drug_openfda_openFDA)-[e2:Event]->(d:DrugAdverseEvent_drug_openFDA)-[e3:Event]->(p:DrugAdverseEvent_openFDA)<-[e4:Event]-(r:DrugAdverseEvent_reaction_openFDA)<-[e5:name_merge]-(s:SideEffect))
        Then the information is written in the fitting TSV file.
    In the end, the cypher queries to generate new treat edges are generated and written into a cypher file.

In the last step, the edges are integrated with the Neo4j cypher-shell and the cypher file.