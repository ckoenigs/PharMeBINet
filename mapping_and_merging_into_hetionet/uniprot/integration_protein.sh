#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate proteins with interaction into Hetionet'

python3 integrate_into_hetionet_with_extra_relationships.py $path_to_project > output/output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120
