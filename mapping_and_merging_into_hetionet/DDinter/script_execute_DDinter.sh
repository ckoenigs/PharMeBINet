#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map DDinter node mapping'

python3 mapping_drug_ddinter.py $path_to_project > output/output_node_mapping.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 60
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map DDinter node mapping'

python3 map_drug_drug_interaction_DDinter.py $path_to_project "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International" > output/output_edge_mapping.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge.cypher 

sleep 60
$path_neo4j/neo4j restart
sleep 120
