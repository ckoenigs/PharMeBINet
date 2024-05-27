#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir edge_go_protein_gene
  mkdir protein
fi

python3 combine_with_new_go.py $path_to_project > output/output_map.txt


echo map protein
now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_go_protein.py $path_to_project > protein/output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 40

python3 prepare_go_gene_and_protein_rela.py $path_to_project > edge_go_protein_gene/output.txt

echo integrate edges
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt
sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt

sleep 40