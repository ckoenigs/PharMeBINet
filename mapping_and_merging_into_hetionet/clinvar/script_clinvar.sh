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
  mkdir disease
  mkdir variant_drug
fi

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_clinvar_variation.py $path_to_project > output/output_map_variant.txt


now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_disease_clinvar.py $path_to_project > output/output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4j3.txt

sleep 180

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4j3.txt

sleep 180

now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 60

python ../../restart_neo4j.py $path_neo4j > output/neo4j2.txt


sleep 120

