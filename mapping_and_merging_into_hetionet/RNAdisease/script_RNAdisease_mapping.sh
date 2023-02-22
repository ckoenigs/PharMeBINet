#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo mapping rna and disease

python3 RNADisease_map.py $path_to_project > output/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30

$path_neo4j/neo4j restart


sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo perparation of edge merging

python3 RNADisease_edges.py $path_to_project > output/output_edge.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30

$path_neo4j/neo4j restart


sleep 60
