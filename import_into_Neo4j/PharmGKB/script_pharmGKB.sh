#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

echo integrate PharmGKB into neo4j

#$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 

java -jar ../Neo4j-GraphML-Importer-v1.0.2.jar -i merged.graphml  -e bolt://localhost:7687 --username neo4j --password test

sleep 120

$path_neo4j/neo4j restart


sleep 120




