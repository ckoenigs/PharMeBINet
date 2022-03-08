https://uberon.github.io/

version:

First, the script downloads the latest version of UBERON.
Then the OBO file from the UBERON will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py data/ext.obo Uberon uberon_extend
All terms are a node in DO all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating a different kind of relationships of the OBO file.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j shell.

License: Attribution 3.0 Unported (CC BY 3.0)