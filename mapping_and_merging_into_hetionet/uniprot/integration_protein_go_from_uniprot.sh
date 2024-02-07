#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate proteins-go from uniprot'

python3 check_on_go_rela_and_integration.py $path_to_project > uniprot_go/output_protein_go.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo edge cypher

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge_go.cypher > output/cypher4.txt

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 60
