#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo mapp se, symptom, disease and phenotypes to each other

python3 connect_sideeffect_symptom_disease.py $path_to_project > output/output_symptoms_to_sideEffects_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of equal relationship between disease, side effect and symptom

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher > output/output_cypher.txt

sleep 120
$path_neo4j/neo4j restart
sleep 120