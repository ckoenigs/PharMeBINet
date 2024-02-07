#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"
echo protein mapping
python3 map_protein_bindingdb.py $path_to_project > protein/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug mapping
python3 map_chemical_bindingdb.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 100
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 200



now=$(date +"%F %T")
echo "Current time: $now"
echo complex integration
python3 prepare_complex_edge.py $path_to_project > protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate complex

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo ers integration
python3 prepare_ERS_edge.py $path_to_project > ERS/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map ers and the edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge_2.cypher > output/cypher3.txt

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j2.txt
sleep 120
