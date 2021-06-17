#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo clinvar drug response

python3 mapping_clinvar_drug_response.py $path_to_project > output/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f drug/cypher_drug.cypher 

sleep 120

$path_neo4j/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo clinvar drug response - variant rela

python3 rela_variant_drug.py $path_to_project > variant_drug/output.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f variant_drug/cypher.cypher 

sleep 120

$path_neo4j/neo4j restart


sleep 120