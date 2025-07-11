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

#download go
wget  -O data/go-basic.obo "purl.obolibrary.org/obo/go/go-basic.obo"

now=$(date +"%F %T")
echo "Current time: $now"
echo parse obo file

python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/go-basic.obo GO go $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo parse annotation file

python3 parsing_go_annotition.py $path_to_project  > output/output_annotation.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate go into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate go rela into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher_edge.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30

cd data
rm *
cd ..