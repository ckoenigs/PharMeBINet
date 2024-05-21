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

echo prepare ADReCS-Target integration

# run preparation adrecs-target
python3 prepare_files.py $path_to_project > output/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target nodes into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

# sleep 60

# python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


# sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target rela into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 30