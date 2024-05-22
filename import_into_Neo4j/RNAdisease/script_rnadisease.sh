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
  cd data
  wget http://www.rnadisease.org/static/download/RNADiseasev4.0_RNA-disease_experiment_all.zip
  cd ..
fi

python3 RNAdisease.py $path_to_project > output/output_integration_rnadisease.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnadisease into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30
