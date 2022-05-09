#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2
now=$(date +"%F %T")
echo "Current time: $now"

echo prepare gencc

python3 gencc_integration_preparation.py $path_to_project > output/outputfile.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate gencc into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 


sleep 60

$path_neo4j/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"