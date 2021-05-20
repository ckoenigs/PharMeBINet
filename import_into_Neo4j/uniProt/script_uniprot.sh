#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"

# python3 parse_uniprot_flat_file_to_tsv.py database/uniprot_sprot.dat $path_to_project > output_integration.txt
# python3 parse_uniprot_flat_file_to_tsv.py $path_to_project > output/output_integration.txt
python3 parse_uniprot_xml_file_to_tsv.py $path_to_project > output/output_integration.txt

rm database/*

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate uniprot into neo4j

# $path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_protein.cypher > output/output_cypher_integration.txt 2>&1
$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120