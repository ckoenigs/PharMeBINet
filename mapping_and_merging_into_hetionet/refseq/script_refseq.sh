#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

if [ ! -d output ]; then
  mkdir output
  mkdir rna
  mkdir gene
  mkdir protein
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo add RNA

python3 integrate_RNA_refseq.py $path_to_project > output/RNA_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map genes

python3 map_gene_refseq.py $path_to_project > output/gene_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map cds

python3 map_cds_to_protein_refseq.py $path_to_project > output/protein_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo create rna-gene edge

python3 prepare_gene_rna_edges.py $path_to_project > output/rna_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo create rna-protein edge

python3 create_rna_protein_edge.py $path_to_project > output/rna_edge.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60
