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


now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3 MappingUniProtId.py $path_to_project > uniprotIDs/output_map.txt

echo integrate mapping node with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_mapping2.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120


# relationships!

now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Reaction integration

python3 TreatEdgeIntoNode.py $path_to_project "${license}" > PathwayEdges/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo edge physicalentity-reactionLikeEvent

python3 CreateEdgeReactionToPhysicalEntity.py $path_to_project "${license}" > physikalEntityEdges/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-ReactionLikeEvent relationships

python3 CreateEdgeDrugToNode.py $path_to_project "${license}" > DrugEdges/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Regulation relationships

python3 CreateEdgeRegulationToNode.py $path_to_project "${license}" > RegulationEdges/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Interaction relationships

python3 CreateEdgeInteraction.py $path_to_project "${license}" > interactions/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Complex relationships

python3 CreateComplexEdges.py $path_to_project "${license}" > ComplexEdges/output.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j/cypher-shell -u neo4j -p test -f output/cypher_drug_edge.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120
