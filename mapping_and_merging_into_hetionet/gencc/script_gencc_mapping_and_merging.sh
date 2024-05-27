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
  mkdir rela
  mkdir disease
fi

echo gencc

now=$(date +"%F %T")
echo "Current time: $now"
echo map gene

python3 mapping_gene_gencc.py $path_to_project > gene/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map disease

python3 mapping_disease_gencc.py $path_to_project > disease/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of gencc mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo prepare edge integration disease

python3 merge_gene_disease_edges.py $path_to_project > output/output_edges.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of gencc mapping and new edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30


