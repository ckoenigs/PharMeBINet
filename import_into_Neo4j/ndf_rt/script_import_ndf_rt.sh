#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

python3 prepare_ndf_rt_to_neo4j_integration.py $path_to_project > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ndf-rt into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120
echo delete ndf-rt nodes without relaionships

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_file_delete.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120