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

python3 importSideEffects_change_to_umls_meddra_final.py data/ $path_to_project > output/output_integration_sider.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate sider into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate sider into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30