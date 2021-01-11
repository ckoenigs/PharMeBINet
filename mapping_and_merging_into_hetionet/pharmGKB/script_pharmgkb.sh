#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map pahrmgkb gene'

python3 map_gene.py $path_to_project > gene/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'map chemical and drug'

python3 map_drug_chemical.py $path_to_project > chemical/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 180
$path_neo4j/neo4j restart
sleep 120

