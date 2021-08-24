#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo smpdb


now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 mapping_smpdb_pathway.py $path_to_project > pathway/output_integration_metabolite.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3  mapping_smpdb_protein.py $path_to_project > protein/output_mapping_proteins.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 mapping_smpdb_metabolite.py $path_to_project > pathway/output_integration_metabolite.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of smpdb mapping and nodes into hetionet

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 60
$path_neo4j/neo4j restart
sleep 120

# relationships!