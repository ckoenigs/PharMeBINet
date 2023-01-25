#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

#download go
wget  -O data/go-basic.obo "purl.obolibrary.org/obo/go/go-basic.obo"

now=$(date +"%F %T")
echo "Current time: $now"
echo parse obo file

python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/go-basic.obo GO go $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo parse annotation file

python3 parsing_go_annotition.py $path_to_project  > output/output_annotation.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate go into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher.cypher

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120