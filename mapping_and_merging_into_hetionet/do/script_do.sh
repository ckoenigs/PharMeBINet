#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
fi

echo 'Mapping Disease Ontology into PharMeBINet'

python3 map_disease_ontology_to_disease.py $path_to_project > output/output_do.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30
