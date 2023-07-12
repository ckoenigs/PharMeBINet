#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"

echo EFO disease mapping
python3 map_disease_efo.py $path_to_project > output/output_efo_disease.txt


$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"

echo EFO disease is_a mapping
python3 merge_is_a_relationships_efo.py $path_to_project > output/output_efo_disease.txt


$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30
