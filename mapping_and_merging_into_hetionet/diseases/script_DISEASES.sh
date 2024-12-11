#!/bin/bash


#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# prepare directories
if [ ! -d output ]; then
  mkdir output
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map gene'

python3 map_gene_diseases.py $path_to_project > output/output_node_mapping.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map disease'

python3 map_disease_diseases.py $path_to_project > output/output_disease.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 30
