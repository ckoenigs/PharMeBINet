#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

license='Attribution-NonCommercial 4.0 International'

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map Drugbank protein '

python3 merging_protein_into_hetionet.py "${license}" $path_to_project > protein/output_integration_file_generation.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'map Drugbank pc '

python3 integrate_pc.py $path_to_project "${license}" > pharmacological_class/output_integration_file_generation.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f protein/cypher_protein.cypher

sleep 30
python ../../restart_neo4j.py $path_neo4j > neo4j1.txt
sleep 40

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank protein-compound rela '

python3 integrate_protein_compound_rela.py "${license}" $path_to_project > rela_protein/output_integration_file_generation_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank reaction '

python3 prepare_drugbank_reaction.py "${license}" $path_to_project > reaction/output_integration_file_generation_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank compound-pc '

python3 integrate_compound_pc_rela.py $path_to_project "${license}" > compound_pc/output_integration_file_generation_rela.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f rela_protein/cypher.cypher

sleep 30
python ../../restart_neo4j.py $path_neo4j > neo4j1.txt
sleep 40
