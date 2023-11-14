#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

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

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
python ../../restart_neo4j.py $path_neo4j > neo4.txt
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo prepare edge integration disease

python3 merge_gene_disease_edges.py $path_to_project > output/output_edges.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of gencc mapping and new edges

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
python ../../restart_neo4j.py $path_neo4j > neo4.txt
sleep 30


