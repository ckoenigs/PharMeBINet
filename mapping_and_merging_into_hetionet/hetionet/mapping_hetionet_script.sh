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
  mkdir edges
fi


echo perparation

python3 map_gene_hetionet.py $path_to_project > output/output_map.txt


echo map disease
now=$(date +"%F %T")
echo "Current time: $now"


python3 map_disease_hetionet.py $path_to_project > output/output_map_disease.txt


echo map anatomy
now=$(date +"%F %T")
echo "Current time: $now"


python3 map_anatomy_hetionet.py $path_to_project > output/output_map_anatomy.txt


echo map symptom
now=$(date +"%F %T")
echo "Current time: $now"


python3 add_symptom_hetionet.py $path_to_project > output/output_map_disease.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30



echo add edges
now=$(date +"%F %T")
echo "Current time: $now"


python3 edge_add.py $path_to_project > edges/output_edges.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30