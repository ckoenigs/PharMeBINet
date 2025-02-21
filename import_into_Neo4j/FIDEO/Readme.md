Food Interactions with Drugs Evidence Ontology (FIDEO) https://gitub.u-bordeaux.fr/erias/fideo/.

version: 2023-12-18

First, the script downloads the latest version of FIDEO (https://gitub.u-bordeaux.fr/erias/fideo/) as OWL file.
The parse the OWL to OBO with robot¹.
Then the OBO file from the FO will be transformed into node and relationship TSV with the program of EFO/transform_obo_to_tsv_and_cypher_file.py data/fideo.obo FIDEO FIDEO_Entry
All terms are a node in FO all property-value pairs in OBO are a property in the node except for property key='is_a' and 'relationship'. They are for generating a different kind of relationships of the OBO file.
Additionally, the cypher queries for the node and the different kinds of relationships are generated. After this, the data will be integrated into Neo4j with the Neo4j cypher-shell.

License: CC BY 4.0

FIDEO is automatically updated.

1 R.C. Jackson, J.P. Balhoff, E. Douglass, N.L. Harris, C.J. Mungall, and J.A. Overton. ROBOT: A tool for automating ontology workflows. BMC Bioinformatics, vol. 20, July 2019.