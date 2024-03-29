#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo hmdb


now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 interagete_hmdb_metabolite.py $path_to_project > metabolite/output_integration_metabolite.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo GO

python3  mapping_hmdb_go.py $path_to_project > go/output_mapping_gos.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3  mapping_hmdb_protein.py $path_to_project > protein/output_map_protein.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hmdb mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

# relationships!