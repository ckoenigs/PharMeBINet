#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo smpdb
# prepare directories
if [ ! -d output ]; then
  mkdir output
  mkdir edge_pathways
  mkdir metabolite
  mkdir protein
  mkdir pathway
fi


now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 mapping_smpdb_pathway.py $path_to_project > pathway/output_integration_pathway.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3  mapping_smpdb_protein.py $path_to_project > protein/output_mapping_proteins.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo metabolite

python3 mapping_smpdb_metabolite.py $path_to_project > metabolite/output_integration_metabolite.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of smpdb mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30


now=$(date +"%F %T")
echo "Current time: $now"
echo prepare edges

python3 generate_connection_from_pathway_smpdb.py $path_to_project > edge_pathways/output_integration.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of smpdb mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 40
