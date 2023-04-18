#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo se
python3 map_Sider_se.py $path_to_project > output/output_map_se.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo drug
python3 map_sider_drug.py $path_to_project > output/output_map_drug.txt

echo integrate mapping with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30

$path_neo4j/neo4j restart
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-se edges
python3 integrate_rela_drug_side_effect.py $path_to_project > output/output_map_rela.txt

echo integrate relationships
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_rela.cypher

sleep 30

$path_neo4j/neo4j restart
sleep 30

