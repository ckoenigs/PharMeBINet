#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_clinvar_variation.py $path_to_project > output/output_map_variant.txt


now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_disease_clinvar.py $path_to_project > output/output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

