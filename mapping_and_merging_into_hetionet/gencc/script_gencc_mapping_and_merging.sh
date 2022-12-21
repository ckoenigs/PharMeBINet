#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo gencc

now=$(date +"%F %T")
echo "Current time: $now"
echo map gene

python3 mapping_gene_gencc.py $path_to_project > gene/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map disease

python3 mapping_disease_gencc.py $path_to_project > disease/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of gencc mapping and nodes into hetionet

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 60
$path_neo4j/neo4j restart
sleep 120


