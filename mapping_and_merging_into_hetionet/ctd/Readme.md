The script mapped all CTD nodes to the fitting opposite in my database. Additionally, the relationships with references are integrated into my database.
First, map CTD gene to genes:
               The genes can be easily mapped because both have the same identifier. However, in case it did not map it also uses the CTD alternative gene ids.
               The CTD gene gets as additional pharmGKB ids and bioGrid ids to the external references.
               All mapping pairs are written into a TSV file.
               Additionally, a cypher file is generated and wrote in a cypher query to integrate the CTD gene information into the gene node.

Next, the CTD GO is mapped to Biological Process (BP), Cellular Component (CC), and Molecular Function (MF):
               They have both the same identifier (GO ID). So it was only important to check if it maps to the BP, CC, or MF. Additionally, the alternative identifiers of BP, CC, and MF are used for mapping.
               All mapping pairs are written into a TSV file. Also, the different cypher queries for the different mappings are generated and written into the cypher file from before.

Then the focus on mapping on CTD pathway:
               The pathway in CTD has only KEGG and Reactome identifier. The Reactome identifiers are tried to map to the pathway external references. If this did not work it tries to map CTD pathway name to name and synonyms of pathways.
               The CTD pathways with the KEGG identifier are ignored because KEGG has some specific license.
               All mapping pairs are written into a TSV file and a cypher query is generated to integrate the information.

Then CTD disease to disease and symptom:
                This needs different mapping methods because CTD disease has OMIM or MESH as an identifier:
                First, mapped with MESH and OMIM to disease external identifier
                Next, use the alternative MESH and OMIM CTD identifier to disease external identifier
                CTD disease also contains DOIDs and they are mapped to disease DOIDs.
                For the one that still did not map in UMLS, they search for a UMLS CUI for MESH or OMIM identifier and map it to disease external references.
                The last mapping possibility to disease is mapping the CTD disease name to the disease names and synonyms.
                Next, it is tried to map the not mapped CTD disease to symptom with name.
                If this is not working, the it is mapped to symptom with the MESh id.
                For all mapping pairs, a TSV file is generated and a cypher query to integrate this information into the disease.


The last label is CTD chemical to compound and all not mapped chemicals generate new nodes with label chemical:
    There are different mapping methods used:
        1.	map CTD chemical cas-number with compound cas-number
        2.	Map the MESH ID to UMLS Cui with UMLS, which contains MESH ID. Further UMLS contains DrugBank IDs, so the UMLS Cui is mapped to DrugBank ID.
        3.	Map the Mesh ID to RxNorm CUI with RxNorm, which contains a MESH identifier. In RxNorm the RxNorm Cui is mapped to DrugBank IDs, which are also in RxNorm.
        4.	Use the RxNorm-DrugBank table, which is constructed with unii and InChIKey, to map.
        5.	Map with name and synonyms of CTD to name and synonyms of DrugBank.
    The mapped pairs are written into TSV files. Additionally, all not mapped are written also in a TSV file. For both is a cypher query generated and add to the cypher file.

Now, all node mapping information is integrated into the database with the cypher shell.

Next, the different relationships are prepared:
               Gene-participates pathway: it takes all pairs where gene and pathway are mapped and wrote it into a TSV file. With neo4j merge, the information is integrated into the database
               Gene participates GO: The same goes for this pair only that it generates 3 files and 3 queries for BP, CC, and MF.
               Chemical-disease (): From the chemical-disease pairs are only the mapped ones and the relationships with evidence and pubmed ids used. They combine multiple information of the same pair with the same direct evidence and all pair is written into TSV file for the different direct evidence. The queries for the edge chemical-induces-disease and chemical-treats-disease are generated to merge this information into the database. They are added to the cypher file.
               Chemical-gene: For this pair, only the human edge pairs which have pubmed ids are used (addition to mapped node). The edge label depends on the actions and only if the action is direct between the chemical and the gene (check in interaction_text if they are in the same []). All other edges are only association edges.  All pairs are written in the right edge label TSV file and for each edge label, a cypher query is generated and add to the cypher file.
               Chemical-phenotype: Like before only human pairs are used. Also, the relationship type depends on the interaction actions. If increase^phenotype/decrease and like before in the same [] with the chemical they get the relationship Increase/Decrease else it is associated. The rest is like before.
               Gene-disease: This is like chemical-disease relationships only all relationships are Associates.

As the last step, the different relationships are integrated into the database with the cypher shell.
