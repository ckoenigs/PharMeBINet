https://reactome.org/

Version: 2025-03-25

## Preparation of Neo4j :

1. Download Reactome dump und remove the '.graph' of the name.
2. Delete existing reactome directories in Neo4j data.
3. Load dump into Neo4j 5.26.4:

   ./neo4j-admin database migrate --force-btree-indexes-to-range reactome

   If after execute this command this error appeare: Failed to migrate database 'reactome': Failed to verify the transaction logs. This most likely means that the transaction logs are corrupted.
   The remove all transaction files!


## Perpare import into other Neo4j database

First, the script starts the Reactome Neo4j database.
Then get all constraints/indices from Reactome.
Then a cypher file is generate with the apoc query to extract Reactome.
In the next step, the Reactome database is exported with APOC export as graphML.
Then my database is started and the Neo4j-GraphML-Importer (https://github.com/BioDWH2/Neo4j-GraphML-Importer) is used to import the data.
The Reactome node gets a suffix and the indices of Reactome are also integrated with the import tool.
java -jar Neo4j-GraphML-Importer-v1.0.0.jar -i reactome/pathwaydata.graphml  -e bolt://localhost:7687 --username neo4j --password test

License: Creative Commons Attribution 4.0 International (CC BY 4.0) License 