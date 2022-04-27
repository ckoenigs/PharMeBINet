#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo 'Mapping Disease Ontology into PharMeBINet'

python3 map_disease_ontology_to_disease.py $path_to_project > output_do.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher 

sleep 60
$path_neo4j/neo4j restart
sleep 120
