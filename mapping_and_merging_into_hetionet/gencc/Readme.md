GenCC script contains multiple steps.
First, the GenCC Gene is mapped to the gene:
    First, the mapping TSV and a cypher file are generated and a cypher query is added to the cypher file.
    Next, all genes from PharMeBINet are loaded and added to dictionaries.
    Last, the GenCC genes are loaded and mapped to the gene:
        First, mapping is with the GenCC id (HGNC id) to the gene HGNC id.
        Next, is the mapping between the GenCC gene symbol and gene gene symbols.
    All mapping pairs are written into the TSV file.

The second program mapped the GenCC disease to disease:
    First, all diseases from my database are loaded into dictionaries. Also, load the MONDO disease nodes which are obsolete but have a replacement ID.
    Then, load all disease-gene edges and write disease-edge information into a dictionary.
    Next, the TSV file for the mapping pair and a cypher query is generated. The cypher query is added to the cypher file.
    In the last step, the GenCC disease is loaded and mapped to the disease:
        First, the GenCC disease ID is mapped to the disease identifier (both MONDO identifiers).
        Next, the GenCC disease ID is mapped from the obsolete Mondo ID to the replaced ID (sometimes not existing anymore) to the disease identifier.
        The last mapping is between GenCC disease name and disease name/synonym.
    All mapping pairs are written into the TSV file.


The cypher shell integrates the mapping connection between the Gencc gene and disease, and gene and disease.

Next, the relationships of GenCC between the Gene and Disease are prepared:
    First, load existing pairs and write information into a dictionary.
    Next, load all GenCC gene-disease pairs. Take only the relationships with classification: supportive, strong, definitive, moderate (https://thegencc.org/faq.html#validity-termsdelphi-survey) because have high evidence to be existing. Also, the edges need to have PubMed IDs.
    The pairs are checked if they are already in PharMeBINet or not and depending on the information are written in different dictionaries and the information is merged.
    In the last step, the TSV files for mapping and new edges and the cypher file with the additional cypher queries are generated. Last, the information on the different dictionaries is prepared and written into the right TSV file.
    
Last, the cypher shell integrates the edges into my database.