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
echo Pathway

python3  mapping_hmdb_pathway.py $path_to_project > pathway/output_mappings.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo Metabolite-Compound edge

python3  create_connection_between_metabolite_and_compound.py $path_to_project > metabolite_compound_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 mapping_hmdb_disease.py $path_to_project > disease/output_integration.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hmdb mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_part2.cypher > output/cypher1.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 40

# relationships!

now=$(date +"%F %T")
echo "Current time: $now"
echo prepare edges without any own information between metabolite/protein and pathway/BP/CC/MF

python3 edge_protein_without_infos.py $path_to_project > edge_protein_metabolite_without_info/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo prepare edges without any own information between metabolite and disease/protein

python3 integrated_edge_between_disease_or_protein_and_metabolite.py $path_to_project > metabolite_disease_protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of hmdb edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 140