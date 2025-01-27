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
wget  -O data/fideo.owl "https://gitub.u-bordeaux.fr/erias/fideo/-/raw/master/fideo.owl?ref_type=heads&inline=false"

# convert OWL to obo with robot
../robot.sh convert -i data/fideo.owl --format obo -o data/fideo.obo --check false


python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/fideo.obo FIDEO FIDEO_Entry $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate FIDEO into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate FIDEO edges into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher_edge.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30