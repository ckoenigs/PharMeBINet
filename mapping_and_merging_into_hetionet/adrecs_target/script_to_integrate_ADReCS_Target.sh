#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

path_to_datasource="adrecs_target"

if [ ! -d output ]; then
  mkdir output
  mkdir chemical
  mkdir gene
  mkdir sideeffect
  mkdir protein
  mkdir variant
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo drug mapping
python3 mapping_drugs.py $path_to_project $path_to_datasource > chemical/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo gene and protein mapping


python3  mapping_gene_and_protein.py $path_to_project $path_to_datasource > gene/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo variant mapping


python3  mapping_variant.py $path_to_project $path_to_datasource > gene/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo SE mapping

python3 mapping_adr_adrecs_target.py $path_to_project $path_to_datasource > sideeffect/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30
