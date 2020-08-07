#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

license='CC BY-NC 4.0'

now=$(date +"%F %T")
echo "Current time: $now"
echo 'mapp Drugbank protein '

python3 merging_protein_into_hetionet.py "${license}" $path_to_project > output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f protein/cypher_protein.cypher > protein/output_cypher.txt

sleep 180
$path_neo4j/neo4j restart
sleep 120