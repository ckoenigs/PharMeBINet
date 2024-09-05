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
if [ ! -d data ]; then
  mkdir data
fi

#python3 reconstruct_pathway.py $path_to_project > output/output_generate_integration_file.txt
python3 new_pathway_preparation.py $path_to_project > output/output_generate_integration_file.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 10

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 20