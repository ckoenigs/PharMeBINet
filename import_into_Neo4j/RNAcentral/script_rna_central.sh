#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3
now=$(date +"%F %T")
echo "Current time: $now"

echo prepare rnaCentral


python3 integrate_RNAcentral.py $path_to_project > output/output_integration_rnacentral.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnaCentral into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate rnaCentral into neo4j

$path_neo4j/cypher-shell -u neo4j -p $password -f cypher_edge.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60
