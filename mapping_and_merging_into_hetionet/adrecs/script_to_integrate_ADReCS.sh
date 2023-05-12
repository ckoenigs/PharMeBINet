#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

path_to_datasource="adrecs"


now=$(date +"%F %T")
echo "Current time: $now"
echo drug mapping
python3 mapping_drug_adrecs.py $path_to_project $path_to_datasource > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo SE mapping
python3 mapping_adr_adrecs.py $path_to_project $path_to_datasource > sideeffect/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 40

now=$(date +"%F %T")
echo "Current time: $now"
echo perpare edge merging
python3 merge_edge_integration.py $path_to_project > edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate edges

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30
