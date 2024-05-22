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

echo prepare smpDB

python3 prepare_smpdb.py $path_to_project > output/outputfile.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate smpDB into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"