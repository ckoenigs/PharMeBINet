#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo gene and disease

python3 integrate_omim_genes_phenotypes.py $path_to_project > output/output_map_gene_phenotype.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 integrate_omim_predominantly_phenotypes.py $path_to_project > output/output_map_phenotype.txt

echo integrate connection with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_gene_phenotype.cypher > output/output_cypher_integration_gene_disease.txt

sleep 120

$path_neo4j/neo4j restart

sleep 120

echo integrate connection with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_phenotype.cypher > output/output_cypher_integration_disease.txt

sleep 120

$path_neo4j/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo gene and disease

python3 integrate_gene_relationships.py $path_to_project > output/output_rela.txt

echo integrate connection with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_rela.cypher > output/output_cypher_rela.txt

sleep 120

$path_neo4j/neo4j restart

sleep 120
