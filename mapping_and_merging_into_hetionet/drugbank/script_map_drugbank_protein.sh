#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map Drugbank protein '

python3 merging_protein_into_pharmebinet.py $path_to_project > protein/output_integration_file_generation.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map Drugbank pc '

python3 integrate_pc.py $path_to_project > pharmacological_class/output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"


python ../../execute_cypher_shell.py $path_neo4j $password protein/cypher_protein.cypher > output/cypher5.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank protein-compound rela '

python3 integrate_protein_compound_rela.py $path_to_project > rela_protein/output_integration_file_generation_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank reaction '

python3 prepare_drugbank_reaction.py $path_to_project > reaction/output_integration_file_generation_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank compound-pc '

python3 integrate_compound_pc_rela.py $path_to_project > compound_pc/output_integration_file_generation_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank complex_protein '

python3 add_complex_protein_edges.py $path_to_project > compound_pc/output_integration_file_generation_rela.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

python ../../execute_cypher_shell.py $path_neo4j $password rela_protein/cypher.cypher > output/cypher6.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py
