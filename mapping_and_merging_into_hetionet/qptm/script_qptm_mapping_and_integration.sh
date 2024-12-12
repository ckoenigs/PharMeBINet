#!/bin/bash

#define path to neo4j bin
#path_neo4j="/Users/ann-cathrin/Downloads/neo4j-community-5.19.0/bin"
path_neo4j=$1

# path to project
#path_to_project="/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/PharMeBINet/"
path_to_project=$2

#password
#password="test1234"
password=$3




now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate proteins

if [ ! -d protein ]; then
  mkdir protein
fi

python3 mapping_protein_qptm.py $path_to_project > protein/output_protein.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate proteins

if [ ! -d protein ]; then
  mkdir ptm
fi

#python3 integrate_ptm_qptm.py $path_to_project > ptm/output_ptm.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Edge qptm ptm-phenotype'

if [ ! -d ptm_phenotype_edge ]; then
  mkdir ptm_phenotype_edge
fi

#python3 mapping_ptm_phenotype.py $path_to_project > ptm_phenotype_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Edge qptm ptm-protein'

if [ ! -d ptm_protein_edge ]; then
  mkdir ptm_protein_edge
fi

#python3 mapping_ptm_protein.py $path_to_project > ptm_protein_edge/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate edges into neo4j

#python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher_edge.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo restarting neo4j

sleep 10
# python restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 10

