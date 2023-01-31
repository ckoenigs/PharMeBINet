#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"

python3 parse_uniprot_xml_file_to_tsv.py $path_to_project > output/output_integration.txt

rm database/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate uniprot into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60
now=$(date +"%F %T")
echo "Current time: $now"

echo integrate uniprot edge into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60