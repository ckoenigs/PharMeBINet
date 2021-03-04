#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo 'Integrate Disease Ontology into Hetionet'

python3 fusion_of_disease_ontology_in_hetionet_final_2.py $path_to_project > output_do.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120
