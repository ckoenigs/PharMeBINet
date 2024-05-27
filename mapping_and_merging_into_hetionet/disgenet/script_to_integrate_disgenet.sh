#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir gene
  mkdir disease
  mkdir gene_disease_edge
  mkdir gene_protein_edge
  mkdir protein
  mkdir variant
  mkdir variant_disease_edge
  mkdir gene_variant_edge
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map disgenet protein'

python3 mapping_proteins_disgenet.py $path_to_project > protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map disgenet variant'

python3 mapping_variants_disgenet.py $path_to_project > variant/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map disgenet gene'

python3 mapping_genes_disgenet.py $path_to_project > gene/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map disgenet disease'

python3 mapping_diseases_disgenet.py $path_to_project > disease/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 120
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 200


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Edge disgenet gene-protein'

python3 mapping_gene_protein_edge_disgenet.py $path_to_project > gene_protein_edge/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Edge disgenet gene-variant'

python3 mapping_gene_variant_edge_disgenet.py $path_to_project > gene_variant_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Edge disgenet gene/variant-disease'

python3 mapping_gene_variant_to_disease_symptome_edge_disgenet.py $path_to_project > gene_disease_edge/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate edges into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j2.txt
sleep 120
