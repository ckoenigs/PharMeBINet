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
  wget https://foodb.ca/public/system/downloads/foodb_2020_4_7_csv.tar.gz
  tar -xf foodb_2020_4_7_csv.tar.gz
  rm foodb_2020_4_7_csv.tar.gz
  cd ..
fi

python3 fooddb.py $path_to_project > output_generate_integration_file.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate foodb into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/fooddb_cypher.cypher > output/cypher.txt

sleep 30

echo restart

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30