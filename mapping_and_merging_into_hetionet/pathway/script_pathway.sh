#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo perparation

python3 switch_identifier_pathway_to_newer_version.py $path_to_project > output/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120