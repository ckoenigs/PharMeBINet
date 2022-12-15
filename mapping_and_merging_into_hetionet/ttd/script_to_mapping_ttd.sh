#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo smpdb


now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 map_pathway_ttd.py $path_to_project > pathway/output_integration_pathway.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3  map_protein_ttd.py $path_to_project > protein/output_mapping_proteins.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 map_drug_ttd.py $path_to_project > drug/output_integration_drug.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 map_compound_ttd.py $path_to_project > drug/output_integration_compound.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of smpdb mapping and nodes into hetionet

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 60
$path_neo4j/neo4j restart
sleep 120

