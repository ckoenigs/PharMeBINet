#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# prepare directories
if [ ! -d output ]; then
  mkdir output
fi

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

python3 rna_RNAInter.py $path_to_project > output/rna_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo map edge

python3 RNAedges.py $path_to_project > output/rna_edge.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60
