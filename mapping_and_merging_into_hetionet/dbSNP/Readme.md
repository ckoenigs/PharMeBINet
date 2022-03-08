https://www.ncbi.nlm.nih.gov/snp/

Version: 2020-05-13

The script of dbSNP is different from the other. It is because dbSNP is too big. 

This has two parts first get the dbSNP information from an API:
So only for the dbSNP integrated Variants of the other source dbSNP information are downloaded. To download it the API of NCBI is asked. To avoid asking too often all found database information is added to a file. This file information is the first load into the program. 
Every node is own JSON entry. So the information is parsed into a dictionary of information. The information is separated into multiple nodes. Because an entry does not only contain the SNP information but also the connection to diseases, genes, RNAs, and proteins.
Schema:

All nodes and edges are written into TSV files. Additionally, a cypher file is generated to integrate the nodes of dbSNP into Neo4j with a cypher shell.

This information is first integrated into the database.
Next, the dbSNP SNP information should be integrated into the database. Therefore, the information is prepared with a program, and additional another label is added depending on the variant type. It prepares on TSV file for integrating the information and multiple other TSV files to give the different nodes the different labels. Besides, a cypher file is generated with different queries to integrate the information and the labels.
All are integrated with cypher-shell.

License:https://www.ncbi.nlm.nih.gov/home/about/policies/
