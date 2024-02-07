#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo med-rt

now=$(date +"%F %T")
echo "Current time: $now"
echo pharmacologic class mapping

python3  create_new_pc_med_rt.py $path_to_project > pharmacological_class/output_map_med_rt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo chemical mapping

python3  map_chemical_med_rt.py $path_to_project > chemical/output_map_med_rt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo chemical mapping

python3  map_other_to_chemical.py $path_to_project > chemical/output_map_med_rt_other.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease mapping

python3  map_disease_med_rt.py $path_to_project > disease/output_map_med_rt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of med-rt connection into pharmebinet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo merge pc-chemical edges mapping

python3  merge_chemical_pc_edges_med_rt.py $path_to_project > chemical_pharmacological/output_map_med_rt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo merge chemical-chemical edges mapping

python3  merge_chemical_chemical_edge.py $path_to_project > chemical_edge/output_map_med_rt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo merge chemical-disease edges mapping

python3  map_disease_chemical_edge.py $path_to_project > chemical_edge/output_map_med_rt_disease.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration edges of med-rt into pharmebinet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30



