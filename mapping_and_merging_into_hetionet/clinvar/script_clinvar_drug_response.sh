#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo clinvar drug response

python3 mapping_clinvar_drug_response.py $path_to_project > output/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password drug/cypher_drug.cypher > output/cypher3.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 40

now=$(date +"%F %T")
echo "Current time: $now"
echo clinvar drug response - variant rela

python3 rela_variant_drug.py $path_to_project > variant_drug/output.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password variant_drug/cypher.cypher > output/cypher4.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 40