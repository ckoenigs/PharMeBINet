#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

python3 parse_med_rt_to_csv.py $path_to_project > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate med-rt into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_med.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120
echo delete med-rt nodes without relaionships

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_delete.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120