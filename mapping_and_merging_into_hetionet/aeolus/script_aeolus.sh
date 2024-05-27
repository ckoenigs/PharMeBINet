#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

if [ ! -d output ]; then
  mkdir output
  mkdir drug
  mkdir cypher_map
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo aeolus outcome mapping
python3 map_aeolus_outcome_final.py $path_to_project > output/output_map_aeolus_outcome.txt



echo Aeolus drugs

now=$(date +"%F %T")
echo "Current time: $now"


python3  map_aeolus_drugs_final.py $path_to_project > output/output_aeolus_drug.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 60

echo relationships
python3  integrate_aeolus_relationships.py $path_to_project > output/output_aeolus_rela.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher1.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 60
