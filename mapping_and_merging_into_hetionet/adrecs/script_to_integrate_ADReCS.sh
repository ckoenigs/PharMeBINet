#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

path_to_datasource="adrecs"

if [ ! -d output ]; then
  mkdir output
  mkdir chemical
  mkdir edge
  mkdir sideeffect
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo drug mapping
python3 mapping_drug_adrecs.py $path_to_project $path_to_datasource > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo SE mapping
python3 mapping_adr_adrecs.py $path_to_project $path_to_datasource > sideeffect/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo perpare edge merging
python3 merge_edge_integration.py $path_to_project > edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 30
