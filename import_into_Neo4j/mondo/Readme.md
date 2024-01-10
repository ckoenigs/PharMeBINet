The JSON file of MONDO is downloaded from http://purl.obolibrary.org/obo/mondo.json.

Version: 2024-01-03

The script first downloads the latest version of MONDO as a OBO file.
Then the OBO file from the Disease Ontology will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py data/mondo.obo mondo disease
All terms are a node in MONDO all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating a different kind of relationships of the OBO file. Xrefs were stands behind MONDO:superclass are ignored.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j cypher-shell.

License: CC BY 4.0