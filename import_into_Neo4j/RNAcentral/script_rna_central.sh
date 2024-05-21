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
if [ ! -d json_homo ]; then
  mkdir json_homo
fi

now=$(date +"%F %T")
echo "Current time: $now"

echo prepare rnaCentral


python3 integrate_RNAcentral.py $path_to_project > output/output_integration_rnacentral.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnaCentral into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnaCentral into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher_edge.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60
