#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

python3 RNAdisease.py $path_to_project > output/output_integration_rnadisease.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnadisease into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120
