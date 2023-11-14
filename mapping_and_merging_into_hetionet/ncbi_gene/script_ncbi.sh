#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo perparation

python3 integrate_and_update_the_hetionet_gene.py $path_to_project > output_data/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output_data/cypher_merge.cypher

sleep 20

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30