#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo hippie

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3 map_protein_hippie.py $path_to_project > output/output_integration_metabolite.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hmdb mapping and nodes into hetionet

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 60
$path_neo4j/neo4j restart
sleep 120

# relationships!