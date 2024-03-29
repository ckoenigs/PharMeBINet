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
echo drug

python3 MappingDrug.py $path_to_project > drug/output_map.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3 MappingUniProtId.py $path_to_project > uniprotIDs/output_map.txt

echo integrate mapping node with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_mapping2.cypher > output/cypher4.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30


# relationships!

now=$(date +"%F %T")
echo "Current time: $now"
echo multi edges of Reaction integration

python3 TreatEdgeIntoNode.py $path_to_project "${license}" > PathwayEdges/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo edge physicalentity-reactionLikeEvent

python3 CreateEdgeReactionLikeEventToPhysicalEntity.py $path_to_project "${license}" > physikalEntityEdges/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Regulation relationships

python3 CreateEdgeRegulationToNode.py $path_to_project "${license}" > RegulationEdges/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Interaction relationships drug-drug/protein

python3 CreateEdgeInteraction.py $path_to_project "${license}" > interactions/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Interaction relationships

python3 MergeProteinProteinInteraction.py $path_to_project "${license}" > interactions/output_ppi.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Complex relationships

python3 CreateComplexEdges.py $path_to_project "${license}" > ComplexEdges/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Catalyst activity relationships

python3 CreateEdgeCatalystActivity.py $path_to_project "${license}" > CatalystActivityEdges/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Catalyst activity relationships to MF

python3 CreateEdgeCatalystActivityGO.py $path_to_project "${license}" > CatalystActivityEdges/GO_output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo Catalyst activity relationships to PE to PE

python3 CreateCatalystActivityPEtoPE.py $path_to_project "${license}" > CatalystActivityEdges/PE_PE_output.txt

echo integrate connection with neo4j shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_drug_edge.cypher > output/cypher5.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 60
