Diseases script contains multiple steps.
The Diseases genes are mapped to genes:
    In the first step, all PharMeBINet genes are loaded and written into a dictionary.
    Next, a mapping TSV file and a cypher file with additiona cypher query are generated.
    Next all Disease genes which are connected to disease with experimental or data source as evidence type are loaded and mapped:
        First, map gene symbol to gene symbol.
        Next, map the Disease gene identifier to gene symbol.
        Then, map the gene symbol to alternative gene symbols.
        Last, map the identifier to alternative gene symbols.
    All mapping pairs are written into the TSV file.

Next mapped the Diseases disease to disease:
    First, the file for mapping disease as TSV is generated and the additional cypher query is added to the cypher file. 
    Second, all diseases from PharMeBINet database are loaded into dictionaries.
    All Diseases disease are loaded and mapped:
        First, map name to name.
        Then, map identifier to xref DOID.
    All mappings are written into the TSV file.


The cypher shell integrates mappings.

Next, the relationships between the disease and gene from Diseases are prepared:
   First, load existing PharMeBINet pairs and write information into a dictionary.
   Next, prepare TSV files for new edges and updated edges. The additional cypher queries are prepared and written into a new generated cypher file.
   Then, load all Diseases pairs with  experimental or data source as evidence type.
   The write the information into the mapped pairs TSV file or new TSV file.

Last, the cypher shell integrates or updates the edges into PharMeBINet database.