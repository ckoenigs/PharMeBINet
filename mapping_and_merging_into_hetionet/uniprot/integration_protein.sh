#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate proteins with interaction into Hetionet'

#python3 integrate_into_hetionet_with_extra_relationships.py $path_to_project > output/output_integration_file_generation.txt
python3 integrate_protein_and_additional_relationships.py $path_to_project > output/output_protein.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'map uniprot disease'
python3 map_uniprot_disease_to_disease.py $path_to_project > uniprot_disease/output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate disease-gene association'

python3 generate_gene_disease_edge.py $path_to_project > uniprot_disease/output_protein.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'protein-protein interaction'
python3 prepare_interaction_edges.py $path_to_project > output/output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge.cypher > output/output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120
