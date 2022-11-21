#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# path to clinvar saved data
path_to_clinvar_data=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo prepare clinvar data

python3 transform_xml_to_nodes_and_edges.py $path_to_project $path_to_clinvar_data > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate clinvar into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_file_node.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_file_edges.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120

