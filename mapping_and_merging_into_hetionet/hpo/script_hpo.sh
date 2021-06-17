#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# hpo date annotated
hpo_annotated_date='2021-06-08'

# hpo date ontology
hpo_ontology_date='2021-06-08'

now=$(date +"%F %T")
echo "Current time: $now"

echo HPO
python3 map_and_integrate_hpo_info_into_hetionet.py $path_to_project > output/output_hpo_disease.txt


python3 map_hpo_symptoms_into_db.py $path_to_project $hpo_ontology_date > output/output_hpo_symptomes.txt

$path_neo4j/cypher-shell -u neo4j -p test -f cypher/cypher.cypher

sleep 120
$path_neo4j/neo4j restart
sleep 120

python3 integrat_hpo_disease_symptom_rela.py $path_to_project $hpo_annotated_date > output/output_hpo_symptomes_rela.txt

$path_neo4j/cypher-shell -u neo4j -p test -f cypher/cypher_edge.cypher

sleep 120
$path_neo4j/neo4j restart
sleep 120

