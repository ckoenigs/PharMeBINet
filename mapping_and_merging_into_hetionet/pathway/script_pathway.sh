#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo perparation

python3 switch_identifier_pathway_to_newer_version.py $path_to_project > output/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output/output_cypher_integration.txt

sleep 120

$path_neo4j/neo4j restart


sleep 120