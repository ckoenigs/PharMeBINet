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

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo protein-protein interaction

python3 prepare_edges_merging.py $path_to_project > output/output_integration_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hmdb mapping and nodes into hetionet

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 60