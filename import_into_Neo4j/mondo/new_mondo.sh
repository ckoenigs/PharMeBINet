#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#download obo file
wget  -O data/mondo.obo "http://purl.obolibrary.org/obo/mondo.obo"



python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/mondo.obo mondo disease $path_to_project > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate do into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120


