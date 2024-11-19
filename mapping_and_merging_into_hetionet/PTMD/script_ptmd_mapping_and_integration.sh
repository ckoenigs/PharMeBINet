#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate disease

if [ ! -d disease ]; then
  mkdir disease
fi

python3 mapping_disease_ptmd.py $path_to_project > disease/output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate proteins

if [ ! -d protein ]; then
  mkdir protein
fi

python3 mapping_protein_ptmd.py $path_to_project > protein/output_protein.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo restarting neo4j

sleep 20
python restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 20

