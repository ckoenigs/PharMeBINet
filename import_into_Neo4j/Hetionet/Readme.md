https://het.io/

Version: 2017-02-03

## Preparation of Neo4j :

The Neo4j version was downloaded and updated from Neo4j v3 to v4 and then to v5.

## Perpare import into other Neo4j database

First, the script starts the Hetionet Neo4j database.
Then a cypher file is generate with the apoc query to extract Hetionet.
In the next step, the Hetionet database is exported with APOC export as graphML.
Then my database is started and the Neo4j-GraphML-Importer (https://github.com/BioDWH2/Neo4j-GraphML-Importer) is used to import the data.
The Hetionet node gets a suffix and the indices of Hetionet are also integrated with the import tool.
java -jar Neo4j-GraphML-Importer-v1.0.0.jar -i data/pathwaydata.graphml  -e bolt://localhost:7687 --username neo4j --password test

License: CC0 1.0 Universal + https://github.com/dhimmel/integrate/blob/d482033bcaa913a976faf4a6ee08497281c739c3/licenses/README.md