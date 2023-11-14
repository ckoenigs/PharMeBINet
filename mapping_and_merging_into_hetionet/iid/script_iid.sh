#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo mapping

python3 mapping_protein.py $path_to_project > protein/output_mapping_and_integration.txt 


$path_neo4j/cypher-shell -u neo4j -p $password -f protein/cypher.cypher

sleep 30
python ../../restart_neo4j.py $path_neo4j > neo4.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo 'IID interaction'

python3 integrate_interaction_rela.py $path_to_project > interaction/outputintegration.txt 


$path_neo4j/cypher-shell -u neo4j -p $password -f interaction/cypher.cypher

sleep 30
python ../../restart_neo4j.py $path_neo4j > neo4.txt
sleep 60
