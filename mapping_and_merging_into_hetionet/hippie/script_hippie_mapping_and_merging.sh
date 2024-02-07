#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo hippie

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3 map_protein_hippie.py $path_to_project > output/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hippie mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo protein-protein interaction

python3 prepare_edges_merging.py $path_to_project > output/output_integration_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hmdb mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt

sleep 60