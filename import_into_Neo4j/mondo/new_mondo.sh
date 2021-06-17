#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#download json file
wget  -O data/mondo.json "http://purl.obolibrary.org/obo/mondo.json"

echo generation of csv from json file
python3 parse_mondo_json_to_csv.py $path_to_project > output_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate mondo into neo4j

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 

sleep 180

$path_neo4j/neo4j restart


sleep 120

