# HPO

https://hpo.jax.org/app/

Version: 2023-04-05
<!--- Version change need to be done also in the mapping script --->

The script first download the hpo.obo and the phenotype_annotation.hpoa files.

Then the OBO file from the HPO OBO will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py hpo.obo hpo HPO_symptom
All terms are a node in HPO symptom all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating a different kind of relationships of the OBO file.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j shell.

Next the the phenotype_anotation file is handled. There a file for the disease nodes is generated and files for the relationships between disease ['id', 'name', 'source'] and symptom ['disease_id', 'phenotype_id', 'qualifier', 'evidence_code', 'source', 'frequency_modifier','aspect', 'onset', 'sex', 'modifier', 'biocuration'].
Therefore it runs through all lines and combines the information of equal disease symptom pairs.

In the last step, the nodes and relationships are integrated into Neo4j with the cypher queries from the different programs!

License: This service/product uses the Human Phenotype Ontology (version information). Find out more at http://www.human-phenotype-ontology.org We request that the HPO logo be included as well. 