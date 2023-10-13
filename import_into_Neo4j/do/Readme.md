Disease Ontology (DO) was downloaded from http://disease-ontology.org/downloads/ human disease ontology.

version: 2023-03-31

First, the script downloads the latest version of DO.
Then the OBO file from the Disease Ontology will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py data/HumanDO.obo do diseaseontology
All terms are a node in DO all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating a different kind of relationships of the OBO file.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j cypher-shell.

License: CC0 1.0 Universal