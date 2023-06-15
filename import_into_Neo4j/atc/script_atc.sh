#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare ATC integration

# python3 prepare_german_atc.py $path_to_project > output/output.txt
python3 parse_kegg_atc_code.py $path_to_project > output/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target nodes into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher 

sleep 30

$path_neo4j/neo4j restart


sleep 30