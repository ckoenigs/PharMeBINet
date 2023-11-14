#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

python3 fooddb.py $path_to_project > output_generate_integration_file.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ncbi into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/fooddb_cypher.cypher

sleep 30

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30