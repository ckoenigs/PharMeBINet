FIDEO script contains multiple steps.
    First, the file for mapping food as tsv are generated and the additional cypher query is added to the generated cypher file. 
    Second, all foods from PharMeBINet database are loaded into dictionaries.
    Next, all FIDEO food nodes (nodes with identifier FOODON) are loaded and mapped with FOODON id. All mapping pairs are written into the TSV file.


The cypher shell integrates the addition and mappings.


Last, the cypher shell integrates the edges into PharMeBINet database.