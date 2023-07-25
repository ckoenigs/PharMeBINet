GO script contains multiple steps.
First, the GenCC Gene is mapped to               

The second script mapped the go protein to protein and gene.
    First, all genes and proteins from my database are loaded into dictionaries.
    Second, the files for mapping gene and protein as tsv are generated and the additional cypher queries are added to the cypher file. 
    All go proteins are loaded and mapped directly to genes and proteins. For the protein mapping the UniProt id where used. For the gene, the gene symbols were used first. Second, the go protein gene symbols were mapped to gene synonyms.
The cypher shell integrates the mapping connection between go protein, and protein and gene.

Next, the relationships between the Gene and Disease are prepared.

    Take only the relationships with classification: supportive, strong, definitive, moderate (https://thegencc.org/faq.html#validity-termsdelphi-survey) becuase have high evidence to be existing.

    First, get all relationships properties and prepare the header list of the TSV files and prepare the general cypher query to integrate the edge information.
    Then, for each label combination and relationship type a TSV file and a cypher query are added to the cypher file.
    Next, the pairs are loaded from Neo4j and combine existing pairs. This is not done if the gene_product_id or the with_from are different.
    All, combinations are written in the right TSV file with all edge information.
Last, the cypher shell integrates the edges into my database.