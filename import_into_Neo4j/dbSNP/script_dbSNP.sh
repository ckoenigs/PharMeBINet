#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


#path to project
path_to_databases=$3

# prepare directories
if [ ! -d output ]; then
  mkdir output
fi

# prepare directories
if [ ! -d data ]; then
  mkdir data
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo parse dbSNP


python3 parse_json_to_tsv_dbsnp.py $path_to_databases"dbSNP" $path_to_project  > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate efo into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt

sleep 120