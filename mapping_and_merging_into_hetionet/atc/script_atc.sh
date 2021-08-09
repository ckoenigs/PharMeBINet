#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

echo perparation

python3 map_and_integrate_atc.py $path_to_project > output/output.txt 


$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher 

sleep 120
$path_neo4j/neo4j restart
sleep 120