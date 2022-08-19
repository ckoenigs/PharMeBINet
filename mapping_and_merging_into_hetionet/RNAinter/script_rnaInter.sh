#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo map dna to gene

python3 dna_RNAInter.py $path_to_project > output/dna_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map protein

python3 protein_RNAInter.py $path_to_project > output/protein_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map compound to chemical

python3 compound_RNAInter.py $path_to_project > output/compound_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map rna

# python3 rna_RNAInter.py $path_to_project > output/rna_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120
