#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate proteins with interaction into Hetionet'

python3 integrate_protein_and_additional_relationships.py $path_to_project > output/output_protein.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'map uniprot disease'
python3 map_uniprot_disease_to_disease.py $path_to_project > uniprot_disease/output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt
python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_gene.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 40

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate disease-gene association'

python3 generate_gene_disease_edge.py $path_to_project > uniprot_disease/output_protein.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'protein-protein interaction'
python3 prepare_interaction_edges.py $path_to_project > output/output_edges.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo node cypher

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher3.txt

sleep 20
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30
