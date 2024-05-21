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

now=$(date +"%F %T")
echo "Current time: $now"

echo prepare biogrid

python3 prepare_biogrid_data.py $path_to_project > output/outputfile.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate biogrid into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 10

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 20

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edges.cypher > output/cypher2.txt

sleep 10

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 20