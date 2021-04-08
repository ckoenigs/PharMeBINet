#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# license
license="CC BY-SA 4.0"


now=$(date +"%F %T")
echo "Current time: $now"
echo drug

python3 MappingDrug.py $path_to_project > drug/output_map.txt

echo integrate mapping node with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_drug.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120


# relationships!

now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Reaction integration

python3 TreatEdgeIntoNode.py $path_to_project $license > PathwayEdges/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f treatment/cypher.cypher.cypher 

sleep 60

$path_neo4j/neo4j restart


sleep 120
