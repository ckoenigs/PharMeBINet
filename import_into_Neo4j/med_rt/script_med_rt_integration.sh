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

python3 parse_med_rt_to_tsv.py $path_to_project > output/output_integration_med_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate med-rt into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_med.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30
echo delete med-rt nodes without relaionships

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_med_edge.cypher > output/cypher2.txt
python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_delete.cypher > output/cypher3.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30