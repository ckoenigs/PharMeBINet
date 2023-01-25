#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

#download do
wget  -O data/HumanDO.obo "https://raw.githubusercontent.com/DiseaseOntology/HumanDiseaseOntology/main/src/ontology/doid.obo"


python3 ../EFO/transform_obo_to_tsv_and_cypher_file.py data/HumanDO.obo do diseaseontology $path_to_project > output/output_generate_integration_file.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate do into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120