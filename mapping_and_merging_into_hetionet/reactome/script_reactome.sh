#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

now=$(date +"%F %T")
echo "Current time: $now"
echo 'modification as of data'

$path_neo4j/cypher-shell -u neo4j -p test -f pathway_modification.cypher

sleep 180

$path_neo4j/neo4j restart


sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo 'delete some nodes'

python3 deleteNodes.py > output_delete.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo ' merge tow nodes '

python3 merge_nodes.py 2011833 1247632 Disease_reactome dbId True > output_merge.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo ' all nodes and relationships of Taxon/Species, which are not homo sapiens '

python3 deleteNodesSpecies.py > output_delete_species.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 MappingPathway.py $path_to_project > pathway/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f pathway/cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 MappingDisease.py $path_to_project > disease/output_map.txt


#//Delete douplication of relationships
#//MATCH (s:Disease)-[r:equal_to_reactome_disease]->(e:Disease_reactome)
#//WITH s,e,type(r) as typ, tail(collect(r)) as coll
#//foreach(x in coll | delete x)

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f disease/cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo bp

python3 GO_BiolProcess.py $path_to_project > gobiolproc/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f gobiolproc/cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo cc

python3 GO_CellComp.py $path_to_project > gocellcomp/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f gocellcomp/cypher.cypher > output_cypher_integration.txt

sleep 180

$path_neo4j/neo4j restart


sleep 120


now=$(date +"%F %T")
echo "Current time: $now"
echo other nodes integration

$path_neo4j/cypher-shell -u neo4j -p test -f other_reactome_node_integration.cypher

sleep 180

$path_neo4j/neo4j restart


sleep 120


# relationships!