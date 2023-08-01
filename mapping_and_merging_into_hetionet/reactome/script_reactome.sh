#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# license
license="CC BY-SA 4.0"

now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 MappingPathway.py $path_to_project "${license}" > pathway/output_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 MappingDisease.py $path_to_project > disease/output_map.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo bp

python3 GO_BiolProcess.py $path_to_project > gobiolproc/output_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo cc

python3 GO_CellComp.py $path_to_project > gocellcomp/output_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo mf

python3 MappingGO_MolecularFunction.py $path_to_project > gomolfunc/output_map.txt

echo integrate mapping node with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60


now=$(date +"%F %T")
echo "Current time: $now"
echo other nodes integration

# version <=neo4j 4.x
# $path_neo4j/cypher-shell -u neo4j -p $password -f other_reactome_node_integration.cypher
# version neo4j 5
$path_neo4j/cypher-shell -u neo4j -p $password -f other_reactome_node_integration_neo4j_5.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60


# relationships!
now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Failedreaction integration

python3 CreateEdgeReactionLikeEventToNode.py $path_to_project "${license}" > reactionLikeEventEdge/output_map.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Pathway integration

python3 CreateEdgePathwayToNode.py $path_to_project "${license}" > PathwayEdges/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p $password -f output/cypher_edge.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 60
