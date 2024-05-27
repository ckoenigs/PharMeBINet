#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map DDinter node mapping'

python3 mapping_drug_ddinter.py $path_to_project > output/output_node_mapping.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map DDinter node mapping'

python3 map_drug_drug_interaction_DDinter.py $path_to_project "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International" > output/output_edge_mapping.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 40
