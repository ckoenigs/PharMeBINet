#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

now=$(date +"%F %T")
echo "Current time: $now"
echo add miRNA and pre-miRNA

python3 perpare_integration_miRNA.py $path_to_project > output/dna_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map genes

python3 map_gene_mirbase.py $path_to_project > output/protein_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 30

$path_neo4j/neo4j restart


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo create rna-gene edge

python3 perpare_gene_rna_edges.py $path_to_project > output/rna_edge.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 30

$path_neo4j/neo4j restart


sleep 60
