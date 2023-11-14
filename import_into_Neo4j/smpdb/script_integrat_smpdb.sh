#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"

echo prepare smpDB

python3 prepare_smpdb.py $path_to_project > output/outputfile.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate smpDB into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"