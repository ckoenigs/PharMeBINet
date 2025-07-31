#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir variant
  mkdir trail
fi

echo gencc

now=$(date +"%F %T")
echo "Current time: $now"
echo map trail

python3 map_trait_to_phenotype_gwas.py $path_to_project > trail/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map variant

python3 map_association_to_variant_single_gwas.py $path_to_project > variant/output_integration.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of gwas mapping and nodes into pharmebinet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30



now=$(date +"%F %T")
echo "Current time: $now"
echo map variant

python3 add_variant_disease_edge.py $path_to_project > edge/output_integration.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of gwas edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher_edge.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30
