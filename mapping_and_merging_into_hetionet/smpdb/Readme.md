The script first maps the different entities to my database.
The first mapping is from SMPDB pathway to pathway:
    First, all pathways from my database are loaded in dictionaries.
    Next, the mapped and not mapped TSV files are generated. Also, the cypher queries are generated and add to the generated cypher file.
    Then, the pathways are mapped with SMPDB id to the pathbank SMPDB id. Next, mapped from name to pathway name and synonyms. All mapped nodes are written into a TSV file.
    The not mapped pathways are combined by name and written into the not mapped TSV file to generate additional pathway nodes.

The next mapping is SMPDB protein to protein/compound:
    First, the protein and compound information is loaded into dictionaries.
    Next, the mapping files and cypher queries are generated for protein-protein and protein-compound.
    Then, the SMPDB proteins are mapped to protein with UniProt ids and Compound with DrugBank ids.

The following mapping is SMPDB metabolite to metabolite:
    First, the metabolites are load into dictionaries.
    Next, the mapping TSV file is generated and the fitting cypher query is added to the cypher file.
    Then, the SMPDB metabolites are loaded from Neo4j and is mapped to metabolite. 
    The first mapping method is based on HMDB identifiers.
    The second is based on the InChIKeys.
    All mapped pairs are written into the TSV file.

Then the different mappings and the new pathways are integrated into my database with the Neo4j cypher shell.

Next, the relationships between pathway-metabolite and pathway-protein are prepared:
    First, a cypher file is generated.
    Next, for each pair, a TSV file is generated with the additional cypher query which is added to the cypher file.
    Then, the pairs are loaded and written into the TSV file. But every connection appears only one time.

Last, the SMPDB relationships are integrated into my database with Neo4j cypher shell.
