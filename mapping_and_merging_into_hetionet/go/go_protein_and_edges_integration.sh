#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo map protein
now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_go_protein.py $path_to_project > protein/output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_protein.cypher

sleep 120

$path_neo4j/neo4j restart

sleep 120

python3 prepare_go_gene_and_protein_rela.py $path_to_project > edge_go_protein_gene/output.txt

echo delete nodes 
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher
sleep 60

$path_neo4j/neo4j restart

sleep 120