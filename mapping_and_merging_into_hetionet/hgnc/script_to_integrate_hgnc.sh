#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

if [ ! -d output ]; then
  mkdir output
  mkdir gene
fi

rm output/cypher.cypher


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map hgnc gene'

python3 map_gene_hgnc.py $path_to_project > gene/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

