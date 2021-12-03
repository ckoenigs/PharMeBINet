#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2


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

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 60
$path_neo4j/neo4j restart
sleep 120
