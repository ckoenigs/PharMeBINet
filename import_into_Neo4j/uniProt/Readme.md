https://www.uniprot.org/

Version: 2021_04

Parse a part of the SwissProt xml file to a TSV file and generate a cypher file. However, only human proteins are prepared and integrated into Noe4j with neo4j cypher-shell.
It extracts information such as the ID, entry, status, sequence length, all AC-numbers, synonyms, general function, pathways, subcellular location, protein existence, external references, gene name, gene id, GO classifier, AS sequence, and more. Additionally information about diseases, keywords, and evidences is extracted as nodes. Also, edge TSV files for protein-disease/evidence/keyword/protein are generated with additional cypher queries.

The schema is shown here:

![er_diagram](uniprot.png)

License: CC BY 4.0