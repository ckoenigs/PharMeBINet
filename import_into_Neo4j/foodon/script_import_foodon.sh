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


#download do
wget  -O data/foodon.owl "https://raw.githubusercontent.com/FoodOntology/foodon/master/foodon.owl"

# convert OWL to obo with robot
../robot.sh convert -i data/foodon.owl --format obo -o data/foodon.obo --check false


python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/foodon.obo foodon FoodOn_Food $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate FO into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate FO into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher_edge.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30