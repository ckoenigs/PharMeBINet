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

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher_node.cypher

sleep 30

$path_neo4j/neo4j restart


sleep 30