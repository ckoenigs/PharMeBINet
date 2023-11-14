#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

python3 prepare_ndf_rt_to_neo4j_integration.py $path_to_project > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ndf-rt into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_file.cypher
$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_file_edge.cypher

sleep 20

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30
echo delete ndf-rt nodes without relaionships

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_file_delete.cypher

sleep 30

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30