#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# prepare directories
if [ ! -d output ]; then
  mkdir output
fi
if [ ! -d aeolus_v1 ]; then
  mkdir aeolus_v1
fi

python3 importAeolus_final.py aeolus_v1/ $path_to_project > output/output_integration_aeolus.txt 

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate aeolus into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30
now=$(date +"%F %T")
echo "Current time: $now"

echo integrate aeolus into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30