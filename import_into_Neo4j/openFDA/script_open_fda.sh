#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#password
password=$2

# path to external data directory
path_to_external_data=$3

path= $path_to_external_data/openFDA

# prepare directories
if [ ! -d output ]; then
  mkdir output
fi

if [ ! -d $path ]; then
  mkdir $path;
fi

python3 import_openFDA.py $path/ > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate pathway into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password $path/load-cypher.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

python ../../execute_cypher_shell.py $path_neo4j $password $path/load-cypher-edge.cypher > output/cypher2.txt

sleep 60

$path_neo4j/neo4j restart


sleep 60