#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo parse DDinter to nodes and edges

python3 integrate_ddinter.py $path_to_project  > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate DDinter into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt


sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60