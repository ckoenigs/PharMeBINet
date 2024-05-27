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
  mkdir disease
  mkdir gene
  mkdir rela
fi

echo gene and disease

python3 integrate_omim_genes_phenotypes.py $path_to_project > output/output_map_gene_phenotype.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 integrate_omim_predominantly_phenotypes.py $path_to_project > output/output_map_phenotype.txt

echo integrate connection with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo gene and disease

python3 integrate_gene_relationships.py $path_to_project > output/output_rela.txt

echo integrate connection with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher2.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 40
