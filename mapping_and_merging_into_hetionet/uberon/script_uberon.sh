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

now=$(date +"%F %T")
echo "Current time: $now"

echo Uberon anatomy mapping
python3 map_anatomy_uberon.py $path_to_project > output/output_anatomy.txt


python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 20
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

