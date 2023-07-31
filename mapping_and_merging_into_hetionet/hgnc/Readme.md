The script starts with the mapping program.

The HGNC gene mapping to gene:
    First, load all genes from PharMeBINet and write the information into the dictionaries.
    Then, prepare the mapping TSV file and create the cypher file with the additional cypher query to map the data.
    Next, the HGNC genes are loaded and mapped with Entrez id to the genes. The gene symbol information and the xrefs are updated. All this information is written into the TSV file.

In the last step, the Neo4j cypher shell integrates the mapping with the use of the cypher file.