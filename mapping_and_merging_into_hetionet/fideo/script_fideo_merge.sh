#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir edges
fi
echo map food
now=$(date +"%F %T")
echo "Current time: $now"

python3 map_food_fideo.py $path_to_project > output/output_food.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map chemical

python3 map_chebi_to_chemical_fideo.py $path_to_project > output/output_chemical.txt



echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 40

echo add edges
now=$(date +"%F %T")
echo "Current time: $now"


python3 prepare_edge.py $path_to_project > output/output_edge.txt


now=$(date +"%F %T")
echo "Current time: $now"


python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt
sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt

sleep 40