#!/usr/bin/env bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir compound_interaction
  mkdir compound_pc
  mkdir compound_variant
  mkdir data
  mkdir protein
  mkdir protein/uniprot_gene
  mkdir gene_variant
  mkdir metabolite
  mkdir pathway
  mkdir pharmacological_class
  mkdir product
  mkdir reaction
  mkdir rela_protein
  mkdir salts
fi

license='Attribution-NonCommercial 4.0 International'



python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank drugs with interaction into Pharmebinet'

python3 addCompoundDrugBank.py $path_to_project > compound_interaction/output_integration_file_generation.txt

now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password compound_interaction/cypher.cypher > output/cypher.txt


python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank salts with interaction into Pharmebinet'

python3 salt_to_compound_mapping_connection_to_drugs.py $path_to_project > salts/output_integration_file_generation_salt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank product  with rela to compound into Pharmebinet'

python3 integrate_product_and_rela_to_compound.py $path_to_project > product/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank gene variant '

python3 mapping_gene_variant_to_variant.py $path_to_project > gene_variant/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank pathway'

python3 mapping_pathway.py $path_to_project > pathway/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank metabolite'

python3 mapping_drugbank_metabolite.py $path_to_project > metabolite/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher1.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py


now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrate Drugbank compound-variant edge'

python3 integrate_variant_compound_edge.py $path_to_project > gene_variant/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo rela

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher2.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py

