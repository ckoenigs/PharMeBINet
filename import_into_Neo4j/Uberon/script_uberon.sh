#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

#download uberon
# old used http://purl.obolibrary.org/obo/uberon/ext.obo 
# I think this http://purl.obolibrary.org/obo/uberon/uberon-full.obo is similar but I will test
wget  -O data/ext.obo "http://purl.obolibrary.org/obo/uberon/uberon-simple.obo"



python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/ext.obo Uberon uberon_extend $path_to_project > output/output_generate_integration_file.txt

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
