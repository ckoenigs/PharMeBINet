https://www.ncbi.nlm.nih.gov/gene/

Version: 2024-02-04

The program first tries to download the human data from NCBI Gene ('ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz').
Then the gzip is open and the cypher queries for the integration of the gene node are prepared.
It runs through the file and generates the content of the node TSV file. In this step, I still check if they are human genes.
In the last step, the information is integrated into Neo4j.

License: https://www.ncbi.nlm.nih.gov/home/about/policies/

This is automatically updated.