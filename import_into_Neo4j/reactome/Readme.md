https://reactome.org/

Version: March 31, 2022

First, the script starts the Reactome Neo4j database.
Then get all constraints/indices from Reactome.
In the next step, the Reactome database is exported with APOC export as graphML.
Then my database is started and the Neo4j-GraphML-Importer-v1.1.3 (https://github.com/BioDWH2/Neo4j-GraphML-Importer) is used to import the data.
The Reactome node gets a suffix and the indices of Reactome are also integrated with the import tool.
java -jar Neo4j-GraphML-Importer-v1.0.0.jar -i reactome/pathwaydata.graphml  -e bolt://localhost:7687 --username neo4j --password test

License: Creative Commons Attribution 4.0 International (CC BY 4.0) License 