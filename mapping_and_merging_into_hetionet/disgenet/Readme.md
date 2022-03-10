The script to merge DisGeNET information into the database contains one script:
First, the DisGeNET proteins are mapped to Protein. 
    Therefore, first, the identifiers and alternative identifiers of protein are loaded.
    Then the TSV file and the cypher file are generated with the additional cypher query. 
    Next, the DIsGeNET proteins are loaded and mapped with the UniProt id to the identifier and alternative id. All mapped pairs are written into the TSV file.

Next, the DisGeNET variants are mapped to Variant:
    First, all variants with dbSNP as xref are loaded and written into a dictionary.
    Then the cypher queries are generated and written into the cypher file. Additionally, TSV files are prepared.
    Next, the DisGeNet variants are mapped to variants with dbSNP identifier and written into a TSV file. The not-mapped variants are written into the other TSV file.

Then the DisGeNET gene mapping:
    First, the genes are loaded and written into a dictionary.
    Then, the TSV file is prepared and the cypher query is written into the cypher file.
    In the last step, The DisGeNet genes are loaded and mapped to genes with NCBI identifiers. All mapping pairs are written into the TSV file.

The last mapping is DisGeNET disease to disease/symptom:
    TODO

Then the mapping information is integrated into the database with the Neo4j cypher shell.

Next, the DisGeNET gene-protein edges are prepared:
    First, a TSV file is prepared.
    Therefore, a cypher file is generated and a cypher query is added. It updates only existing pairs (because some information is not so accurate).
    Then all pairs of DisGeNET which are connected to PharMeBINet are written into a TSV file.

In the next step, the DisGeNet gene-variant edges are prepared:
    First, the existing gene-variant pairs are loaded and written into a dictionary.
    Next, the TSV file for existing edges and new edges are prepared.
    Then, the gene-variant pairs which are connected to PharMeBINet are loaded and written into the different TSV files depending on if they exist or not.
    In the last step, the cypher queries are generated and added to the cypher file.

The last program, prepare the DisGeNet gene/variant-disease/symptom edges:
    For each combination the same steps take place:
        First, the existing pairs from PharMeBINet are loaded and written into a dictionary.
        Then, the TSV files are prepared for existing edges and new edges.
        Next, all pairs from DisGeNET which are connected to PharMeBINet are loaded and combined for the same pairs with different information into a dictionary.
        In the next step, the pairs are checked if they exist or not and are written into the different TSV files.
        In the end, the cypher queries are prepared and added to the cypher file.


The last step is to integrate the different edge information into the database with the Neo4j cypher shell.