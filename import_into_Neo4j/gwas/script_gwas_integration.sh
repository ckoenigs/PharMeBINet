#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare TSV files

python3 gwas_perparation.py $path_to_project > output/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate bindingDB nodes into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher 

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate bindingDB index into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher 

sleep 20

$path_neo4j/neo4j restart

sleep 60

cd data 

rm *

cd ..

now=$(date +"%F %T")
echo "Current time: $now"