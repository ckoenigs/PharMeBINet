#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# hpo date annotated
hpo_annotated_date='2024-01-16'

# hpo date ontology
hpo_ontology_date='2024-01-16'

now=$(date +"%F %T")
echo "Current time: $now"


echo HPO
python3 map_and_integrate_hpo_info_into_hetionet.py $path_to_project > output/output_hpo_disease.txt


python3 map_hpo_symptoms_into_db.py $path_to_project $hpo_ontology_date > output/output_hpo_symptomes.txt

python ../../execute_cypher_shell.py $path_neo4j $password cypher/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

python3 integrat_hpo_disease_symptom_rela.py $path_to_project $hpo_annotated_date > output/output_hpo_symptomes_rela.txt

python ../../execute_cypher_shell.py $path_neo4j $password cypher/cypher_edge.cypher > output/cypher1.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

