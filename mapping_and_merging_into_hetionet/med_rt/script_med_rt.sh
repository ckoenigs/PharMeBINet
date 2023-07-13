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

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo integration edges of med-rt into pharmebinet

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30
$path_neo4j/neo4j restart
sleep 30



