#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

python3 prepare_human_data_IID.py $path_to_project > output/outputfile.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120