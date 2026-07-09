#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
fi

now=$(date +"%F %T")
echo "Current time: $now"

echo EFO disease mapping
python map_disease_efo.py $path_to_project > output/output_efo_disease.txt


python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

now=$(date +"%F %T")
echo "Current time: $now"

echo EFO disease is_a mapping
python merge_is_a_relationships_efo.py $path_to_project > output/output_efo_disease.txt


python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

