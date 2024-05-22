## Experimental Factor Ontology (EFO)

https://www.ebi.ac.uk/efo/

Version: 3.62.0 (2024-01-15)


First, the script downloads the latest version of EFO.

Then the OBO file from the EFO will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py data/efo.obo EFO efo
All terms are a node in efo all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating different kinds of relationships of the OBO file.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j shell.

License: Apache-2.0

EFO is automatically updated.