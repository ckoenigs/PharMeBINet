The script starts one program from prepare protein nodes and relationships to the different other entities.
    The program starts with generating the TSV file for the protein-gene edge
    Then, the program loading all gene information into dictionaries.
    Next, the different cypher files are generated and the fitting queries are prepared to create the protein nodes and create the gene-protein edge.
    In the following, the TSV for the creation of edges is generated. The protein information is prepared for the TSV file and written into the TSV file.
    The mapping to genes for the edge is done with:
        The first mapping is with Entrez id to Gene identifier, but most time in combination with the gene symbol.
        The second mapping is with the HGNC identifier.
        Next, is the mapping with the primary gene symbol.
        The last mapping method is mapping the gene name to the gene symbol/gene synonyms.
    For each UniProt gene pair an entry in the TSV file is added.

Next, is the UniProt disease mapping to disease:
    First, all diseases of PharMeBINet are loaded in and written into dictionaries.
    Next, the mapping TSV file is prepared and the cypher query to integrate the mapping is added to the existing TSV file.
    In the last step, the Uniprot disease is loaded and mapped:
        The first mapping is with the OMIM identifier of the xrefs of Uniprot to the OMIM ids of PharMeBINet xrefs. To reduce inaccuracies if some of the mapped diseases have the same name take only them else take all.
        The other mapping is only name mapping to name/synonyms of PharMeBINet.
    All mapping pairs are written into the TSV file.

Next, the Neo4j cypher-shell integrates the Uniprot proteins and the disease mapping. In the following, it integrated the protein-gene edges.

Then, the Uniprot gene-disease edges are merged to PharMeBINet:
    First, load PubMed ids for all proteins which are connected to a disease.
    Next, generate the TSV file for the disease-gene pairs and generate the cypher file and add different cypher queries.
    Then, all pairs are loaded with the relationship information of Uniprot only the one with a reference is written in a dictionary.
    In the last step, all pairs are written into the TSV file.


The last program executed is the preparation of protein-protein interaction edges.
    First, it loads all protein-protein pairs and writes the information into a dictionary with their iso forms, and combines similar pairs.
    Next, the TSV file for the new edges is prepared, and the fitting cypher file with the query to integrate the edges and the node edge.
    In the last step, the TSV file is filled with the information from the dictionary.

The last step of the script is to integrate the interaction edge into PharMeBINet with the cypher file and the NEO4j cypher-shell.


The GO mapping and edge integration are removed because GO has the information.
