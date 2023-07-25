#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare TSV files

python3 merge_and_save.py $path_to_project > output/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare TSV files

python3 prepare_queries.py $path_to_project > output/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target nodes into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/create_nodes.cypher 

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target nodes into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/create_index.cypher 

sleep 20

# $path_neo4j/neo4j restart


# sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target rela into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/create_edges.cypher 

sleep 30

$path_neo4j/neo4j restart


sleep 30


now=$(date +"%F %T")
echo "Current time: $now"