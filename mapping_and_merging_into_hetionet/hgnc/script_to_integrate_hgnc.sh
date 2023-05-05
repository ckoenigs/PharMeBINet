#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

rm output/cypher.cypher


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map hgnc gene'

python3 map_gene_hgnc.py $path_to_project > gene/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30

