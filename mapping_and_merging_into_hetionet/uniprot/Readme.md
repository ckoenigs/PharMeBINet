The script starts only one program from prepare protein nodes and relationships to the different other entities.
The program starts loading all gene information into dictionaries.
Then, disease information is loaded into a dictionary.
The cypher file is generated. Additionally, the cypher query to integrate the protein nodes into the database is added. Furthermore, the queries for protein-gene, protein-BP, protein-CC, protein-MF, and gene-disease. Also, a query is generated to remove the UniProt identifier that does not exist of the gene's external references.
Next, the TSV files for the different queries are generated.
Then the UniProt proteins are loaded.
First, the connection to the gene is checked. UniProt protein contains a gene identifier. The first mapping is the UniProt gene identifier and gene symbol to gene identifier and gene symbol. Then, UniProt gene identifier and protein name to gene identifier and gene name. Next, the UniProt protein name is used to the gene name.  The last is the use of the UniProt gene symbol to gene symbols. All pairs are written into the TSV file.
If at least one gene is found then the UniProt disease OMIM id is mapped to the disease external references. If a mapping is found the gene-disease pair is written into a dictionary.

Then, the disease-gene pairs are written into a TSV file.

Finally, the cypher-shell integrates the protein nodes and the different edges into the database.


