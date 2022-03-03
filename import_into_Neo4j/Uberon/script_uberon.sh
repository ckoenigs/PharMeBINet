#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#download uberon
wget -O data/ext.obo "http://purl.obolibrary.org/obo/uberon/ext.obo"


python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/ext.obo Uberon uberon_extend $path_to_project > output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate uberon into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher_integration.txt 2>&1

sleep 60

$path_neo4j/neo4j restart


sleep 120