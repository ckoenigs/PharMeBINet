#!/bin/bash

#define path to neo4j bin
path_neo4j="/Users/ann-cathrin/Downloads/neo4j-community-5.19.0/bin"

# path to project
path_to_project="/Users/ann-cathrin/Documents/Master_4_Semester/Forschungsmodul_Heyer/Projekt_Cassandra/Test/"

#password
password="test1234"

#Map and integrate nodes
#Map pharmebinet genes to genes markerdb
# prepare directories

if [ ! -d gene ]; then
  mkdir gene
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate genes

#python3 mapping_genes_markerdb.py $path_to_project > gene/output_gene.txt

if [ ! -d chemical ]; then
  mkdir chemical
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate chemicals

#python3 mapping_metabolites_markerdb.py $path_to_project > chemical/output_chemcial.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate conditions

if [ ! -d condition ]; then
  mkdir condition
fi

#python3 mapping_conditions_markerdb.py $path_to_project > condition/output_condition_2.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate variants

if [ ! -d variant ]; then
  mkdir variant
fi

python3 mapping_variants_markerdb.py $path_to_project > variant/output_variant.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate proteins

if [ ! -d protein ]; then
  mkdir protein
fi

python3 mapping_proteins_markerdb.py $path_to_project > protein/output_protein.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo restarting neo4j

sleep 20
python restart_neo4j.py $path_neo4j > output/neo4j1.txt



#Integrate edges