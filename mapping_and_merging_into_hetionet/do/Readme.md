The script executes first the mapping of the DO disease to Disease:
    First, the cypher file for the mapping of the DO disease and the merging of the is_a relationships is prepared. Also, the TSV files for the mapping pairs and the is_a edges are prepared.
    Then, the Disease information is loaded and generated dictionaries for DOID, name, and synonyms to MONDO id. Also, Only for the hierarchical disease leaf, a dictionary OMIM to mondo ids is generated. This is because in DO are the OMIM xrefs sometimes too general and sometimes too specific for the given node. 
    Next, First ol DO leaves are extracted in a set and then the DO diseases are loaded and are mapped to diseases:
        1. Mapping from DO disease DOID or alternative DOID to the DOID in disease.
        2. Mapping from DO disease name to name/synonym in disease
        3. Mapping synonyms from DO disease to name/synonym in disease
        4. Mapping from DO disease OMIM (were in the xrefs are only one OMIM id and DO leaves and sometimes OMIM was manual mapped) to the OMIM of the disease leaves 
    In the next step, the mapping pair data are prepared and written into the TSV. If multiple mapping exists the information is combined. (DO mapping is preferred and remove the other.)
    In the last step, the hierarchical information of DO is extracted and written into the TSV file.

The data are integrated with the Neo4j cypher-shell and the cypher file.
    

