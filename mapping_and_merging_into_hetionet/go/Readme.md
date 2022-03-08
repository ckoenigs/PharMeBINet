GO script contains multiple steps.
First, the old GOs (biological process, cellular component, and molecular function) are removed and the new GOs nodes are prepared :
               First, all properties are extracted from the GO nodes and prepared in a cypher string. Also, a cypher file is generated for the cypher query to delete old GO nodes which do not exists anymore.
               The next step is to generate for each label  (BP, CC, MF) a new node TSV file, and the fitting cypher file is generated and add to the cypher file.
               In the following, the BP, CC, and MF information from the database is added to a dictionary. Also, the is_a relationships of GO are extracted and wrote into TSV files. Additionally, cypher queries for integrate these relationships are generated and add to the cypher file.
               All nodes are written into the new node TSV file.
Then the old nodes are deleted and the new information is integrated into the database with the cypher-shell.
In the last step, the delete nodes cypher is executed to remove all BP, CC, or MF which did not map to GO.

The second script mapped the go protein to protein and gene.
    First, all genes and proteins from my database are loaded into dictionaries.
    Second, the files for mapping gene and protein as tsv are generated and the additional cypher queries are added to the cypher file. 
    All go proteins are loaded and mapped directly to genes and proteins. For the protein mapping the UniProt id where used. For the gene, the gene symbols were used first. Second, the go protein gene symbols were mapped to gene synonyms.
The cypher shell integrates the mapping connection between go protein, and protein and gene.

Next, the relationships between the GOs and protein/Gene are prepared.
    First, get all relationships properties and prepare the header list of the TSV files and prepare the general cypher query to integrate the edge information.
    Then, for each label combination and relationship type a TSV file and a cypher query are added to the cypher file.
    Next, the pairs are loaded from Neo4j and combine existing pairs. This is not done if the gene_product_id or the with_from are different.
    All, combinations are written in the right TSV file with all edge information.
Last, the cypher shell integrates the edges into my database.