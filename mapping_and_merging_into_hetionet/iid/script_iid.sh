#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo mapping

python3 mapping_protein.py $path_to_project > protein/output_mapping_and_integration.txt 


$path_neo4j/cypher-shell -u neo4j -p test -f protein/cypher.cypher > protein/output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo 'IID interaction'

python3 integrate_interaction_rela.py $path_to_project > interaction/outputintegration.txt 


$path_neo4j/cypher-shell -u neo4j -p test -f interaction/cypher.cypher > interaction/output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120
