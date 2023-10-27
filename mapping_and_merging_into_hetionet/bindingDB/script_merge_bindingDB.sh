#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"
echo protein mapping
python3 map_protein_bindingdb.py $path_to_project > protein/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug mapping
python3 map_chemical_bindingdb.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 60

sleep 60
$path_neo4j/neo4j restart
sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo complex integration
python3 prepare_complex_edge.py $path_to_project > protein/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 50
