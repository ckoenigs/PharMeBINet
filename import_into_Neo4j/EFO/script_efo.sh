#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

#download do
wget  -O data/efo.obo "https://www.ebi.ac.uk/efo/efo.obo"


python3 transform_obo_to_tsv_and_cypher_file.py data/efo.obo EFO efo $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate do into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher.cypher

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate do into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher_edge.cypher

sleep 20

$path_neo4j/neo4j restart


sleep 30