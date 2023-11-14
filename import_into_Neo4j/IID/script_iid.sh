#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo start preparation

python3 prepare_human_data_IID.py $path_to_project exp > output/outputfile.txt

echo rm gz file
rm data/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate iid nodes into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 20

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30
now=$(date +"%F %T")
echo "Current time: $now"

echo integrate iid edge into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 20

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30