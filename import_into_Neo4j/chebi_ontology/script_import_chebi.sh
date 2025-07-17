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



#download co
# wget  -O data/chebi.obo "https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.obo"
python3 download_chebi.py > output/download.txt


python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/chebi.obo chebi_ontology Chemical_ChebiOntology $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate chebi nodes into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate chebi edges into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher_edge.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30