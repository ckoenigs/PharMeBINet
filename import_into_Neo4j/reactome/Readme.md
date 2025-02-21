https://reactome.org/

Version: 2024-11-27

## Preparation of Neo4j :

1. Download latest Neo4j V4
2. Start reactome in Neo4j V4
   Therefore, java 11 is needed.
   JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/ ./restart_neo4j.sh reactome restart

3. Stop Neo4j.

4. Generate dump:
   JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/ ./neo4j-admin dump --database=reactome --to=reactome.dump

5. Delete existing reactome directories in data.

6. Load dump into Neo4j 5.3:

   ./neo4j-admin database load --from-path=/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.3.0 reactome

   ./neo4j-admin database migrate --force-btree-indexes-to-range reactome

   If after execute this command this error appeare: Failed to migrate database 'reactome': Failed to verify the transaction logs. This most likely means that the transaction logs are corrupted.
   The remove all transaction files!


## Perpare import into other Neo4j database

First, the script starts the Reactome Neo4j database.
Then get all constraints/indices from Reactome.
In the next step, the Reactome database is exported with APOC export as graphML.
Then my database is started and the Neo4j-GraphML-Importer-v1.1.3 (https://github.com/BioDWH2/Neo4j-GraphML-Importer) is used to import the data.
The Reactome node gets a suffix and the indices of Reactome are also integrated with the import tool.
java -jar Neo4j-GraphML-Importer-v1.0.0.jar -i reactome/pathwaydata.graphml  -e bolt://localhost:7687 --username neo4j --password test

License: Creative Commons Attribution 4.0 International (CC BY 4.0) License 