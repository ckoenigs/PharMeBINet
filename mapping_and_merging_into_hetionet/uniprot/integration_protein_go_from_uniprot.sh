#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate proteins-go from uniprot'

python3 check_on_go_rela_and_integration.py $path_to_project > uniprot_go/output_protein_go.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge_go.cypher 

sleep 120
$path_neo4j/neo4j restart
sleep 120
