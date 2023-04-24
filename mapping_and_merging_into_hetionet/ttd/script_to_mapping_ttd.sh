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
echo pathway

python3 map_pathway_ttd.py $path_to_project > pathway/output_integration_pathway.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3  map_protein_ttd.py $path_to_project > protein/output_mapping_proteins.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug

python3 map_drug_ttd.py $path_to_project > drug/output_integration_drug.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo compound

python3 map_compound_ttd.py $path_to_project > drug/output_integration_compound.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 map_disease_ttd.py $path_to_project > disease/output_integration_compound.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ttd mapping and nodes into hetionet

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-disease treat

python3 merge_drug_disease_indicates_edges.py $path_to_project > edges/output_integration_compound_indicates.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-target edge

python3 merge_chemical_target_edges.py $path_to_project > edges/output_integration_chemical_target.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ttd edges

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edges.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30

