ChEBI ontology from https://www.ebi.ac.uk/chebi/.

version: 2025-08-01

First, the script downloads the latest version of ChEBI ontology.
Then the OBO file from the ChEBI ontology will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py.
All terms are a node in ChEBI ontology all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating a different kind of relationships of the OBO file.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j cypher-shell.

License: Creative Commons License (CC BY 4.0)

ChEBI ontology is automatically updated.