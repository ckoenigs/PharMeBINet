#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

python3 parse_med_rt_to_tsv.py $path_to_project > output/output_integration_med_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate med-rt into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_med.cypher

sleep 30

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30
echo delete med-rt nodes without relaionships

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_med_edge.cypher
$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_delete.cypher

sleep 30

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30