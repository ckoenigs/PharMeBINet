For ClinVar exists multiple scripts. One is for integration of variants and internal relationships and mapping of disease. The other is for mapping drug response to chemicals and integration of drug-variant relationships. 

First script:
First the preparation of the ClinVar Variant information. The database does not contain any variant information until now.
    First, it loads the gene information from the neo4j database.
    Next, all properties of the Clinvar variant nodes (execpt the variants with review status: "no assertion provided") are extracted to add the information to the database. Therefore, it prepares the properties in the cypher query. 
    Next, the variant nodes are loaded in batches and prepared. This means for every label combination they have their own TSV file and prepare the external references. Additionally, the cypher query for this label combination is generated. Also, the gene information of a ClinVar variant nod has the NCBI gene id and the connection is written into an own TSV file. The gene ids are checked if they exist in PharMeBiNet.
    Then, it generates queries for generating a constrain on variant and a query for gene-variant integration. All queries are added to the cypher file.
    In the last step, the relationships between the different variants are written in TSV files and the cypher queries are generated and written into cypher files.

Next, is the mapping of disease. However, the mapping is not finished. But in general, all mapped pairs are written in a TSV file and a cypher query is generated to integrate the disease information into the disease node. The cypher query is added to the same cypher file as the variant file.

The last step of the first script is the integration of variant nodes and disease information into the database.

Second script:

First, is the mapping of drug response to chemicals:
    In the script, the name is mapped to the name and synonyms of chemicals. However, to get the name of the drug response some preparation is needed because the name sometimes includes the effect of the drug. 
    The mapped pair is written into a TSV file and for the integration of the drug response information, a cypher file is generated with the cypher query to integrate the information.

Next, the cypher file is executed with the cypher shell.

In the following, the relationship between drug-variant is prepared.
    First, all relationships between variant-trait_set of mapped drug response are extracted. The JSON structure of a lot of information a transformed into other structures for better reading. All this information is written in a dictionary.
    The last step is to combine the information of pairs that appear multiple times and all all-pairs information is written into a TSV file. For each relationship type an own TSV file is generated. In addition to the file, a cypher query is generated and added to a cypher file.

In the last step, the relationship information is integrated into the database with the cypher file and cypher-shell.
