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
if [ ! -d data ]; then
  mkdir data
fi



now=$(date +"%F %T")
echo "Current time: $now"
echo parse disgenet to nodes and edges

python3 integrate_disgenet.py $path_to_project  > output/output.txt
#python3 new_disgenet_integration.py $path_to_project  > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate disgenet into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt
python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher.txt


sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 20