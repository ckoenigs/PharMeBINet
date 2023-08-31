The script starts with the mapping of RNAdisease disease to disease/symptom and RNA to RNA:
    First, a cypher file is generated.
    First, is the disease-to-disease/symptom mapping:
        First, load all diseases and write the information into dictionaries.
        Second, the symptoms are loaded and the information is written into dictionaries, too.
        Next, two TSV files are generated one for disease-disease mapping and one for disease-symptom.
        Then, all RNAdisease diseases are loaded and mapped:
            The first mapping is disease name to disease name/synonym.
            Next, is the mapping with name to symptom name/synonym.
            Then, it is a map with mesh ID to symptom identifier.
            The following mapping is with DOID to disease alternative identifiers.
            The last method is mapping with mesh id to symptom xref mesh id.
        All mapping pairs are written into the different TSV files.
        Next, two cypher queries are prepared and added to the cypher file to integrate the mappings.
    Next, the mapping between RNA and RNA:
        First, load all RNA nodes and write their information into dictionaries.
        Next, load gene-RNA pairs and write into a dictionary gene to RNA.
        Then, a TSV file is generated.
        In the following the RNAdisease RNA is mapped to RNA:
            First, the RNA symbol is mapped to the RNA name.
            Next, is the mapping between the symbol and the RNA product.
            The last mapping is with a symbol to gene gene-symbol to RNA.
        All mapping pairs are written into the TSV file.
        In the last step, the cypher query is generated and added to the cypher file.

Next, the cypher queries are executed with the Neo4j cypher-shell.

In the last program, add the RNA-disease/symptom edge:
    First, the cypher file is generated.
    For both disease and symptom, a TSV file is generated.
    Next, the edges (score >0.5) are loaded in batches because of collect the multiple edges between one pair. This information is combined and written into the TSV file.
    Next, the cypher query is prepared and written into the cypher file.

The last step is the integration of the edge into Neo4j with the cypher file and the Neo4j cypher-shell.