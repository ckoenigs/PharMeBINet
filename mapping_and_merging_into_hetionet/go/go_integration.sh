#!/bin/bash

path_neo4j=$1

#path to project
path_to_project=$2

python3 combine_with_new_go.py $path_to_project > output/output_map.txt

echo integrate connection with ne4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher.cypher > output/output_cypher_integration.txt

sleep 120

$path_neo4j/neo4j restart

sleep 120

echo merge nodes 
now=$(date +"%F %T")
echo "Current time: $now"
chmod 775 merge_nodes.sh

./merge_nodes.sh > output_merge.txt

sleep 120

$path_neo4j/neo4j restart

sleep 120
echo delete nodes 
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f cypher_delete.cypher > output_cypher_delete.txt
sleep 120

$path_neo4j/neo4j restart

sleep 120