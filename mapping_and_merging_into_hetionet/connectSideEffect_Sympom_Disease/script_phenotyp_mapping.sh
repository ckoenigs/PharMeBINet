#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir mapping_disease_mapping
  mkdir mapping_phenotype_mapping
  mkdir mapping_symptom_sideeffect
fi

echo mapp se, symptom, disease and phenotypes to each other

python3 connect_sideeffect_symptom_disease.py $path_to_project > output/output_symptoms_to_sideEffects_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of equal relationship between disease, side effect and symptom

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 30