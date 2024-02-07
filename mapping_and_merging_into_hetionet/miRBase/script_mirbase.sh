#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo map genes

python3 map_gene_mirbase.py $path_to_project > output/protein_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map miRNA and pre-miRNA

python3 map_rna_mirbase.py $path_to_project > output/dna_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 40

now=$(date +"%F %T")
echo "Current time: $now"
echo create rna-gene edge

python3 perpare_gene_rna_edges.py $path_to_project > output/rna_edge.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 60
