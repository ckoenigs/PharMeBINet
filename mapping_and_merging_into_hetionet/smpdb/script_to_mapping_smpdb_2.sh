#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo smpdb

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python  mapping_smpdb_protein.py $path_to_project > protein/output_mapping_proteins.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of smpdb mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_2.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo prepare edges

python3 generate_connection_from_pathway_smpdb.py $path_to_project > edge_pathways/output_integration.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of smpdb edges into pharmebinet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo42.txt
sleep 40
