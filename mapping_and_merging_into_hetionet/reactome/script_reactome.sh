#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# license
license="CC BY-SA 4.0"

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
echo ' merge two nodes '

# nodes which are double except of the dbid and id
python3 merge_nodes.py 2011833 1247632 Disease_reactome dbId True > output_merge.txt


python3 merge_nodes.py 9611565 3134792 Disease_reactome dbId True > output_merge.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo ' all nodes and relationships of Taxon/Species, which are not homo sapiens '

python3 deleteNodesSpecies.py > output_delete_species.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

python3 MappingPathway.py $path_to_project > pathway/output_map.txt

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
echo drug

python3 MappingDrug.py $path_to_project > drug/output_map.txt

echo integrate mapping node with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120

#//Delete douplication of relationships
#//MATCH (s:Disease)-[r:equal_to_reactome_disease]->(e:Disease_reactome)
#//WITH s,e,type(r) as typ, tail(collect(r)) as coll
#//foreach(x in coll | delete x)


now=$(date +"%F %T")
echo "Current time: $now"
echo other nodes integration

$path_neo4j/cypher-shell -u neo4j -p test -f other_reactome_node_integration.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120


# relationships!
now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Failedreaction integration

python3 CreateEdgeFailedReactionToNode.py $path_to_project $license > FailedReactionEdges/output_map.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Pathway integration

python3 CreateEdgePathwayToNode.py $path_to_project $license > PathwayEdges/output_map.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Reaction integration

python3 CreateEdgeReactionToNode.py $path_to_project $license > PathwayEdges/output_map.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_edge.cypher 

sleep 120

$path_neo4j/neo4j restart


sleep 120
