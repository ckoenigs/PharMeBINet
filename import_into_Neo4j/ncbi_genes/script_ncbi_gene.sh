#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

python3 integrate_ncbi_genes_which_are_already_in_hetionet.py $path_to_project > output_generate_integration_file.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ncbi into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher_node.cypher > output/cypher.txt

sleep 10

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 20