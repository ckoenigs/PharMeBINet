#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


now=$(date +"%F %T")
echo "Current time: $now"
echo gene and disease

python3 mapping_to_SideEffect.py $path_to_project > output/output_side_effect.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_DrugAdverseEvent_drug_openfda_openFDA.py $path_to_project > output/output_map_DAE_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_DrugAdverseEvent_drug_indication_openFDA.py $path_to_project > output/output_map_DAE_indication_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_DrugAdverseEvent_reaction_openfda_openFDA.py $path_to_project > output/output_map_DAE_reaction_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_SubstanceData_openFDA.py $path_to_project > output/output_SubstanceData_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_SubstanceData_relationships_substance_openFDA.py $path_to_project > output/output_SubstanceData_relationship_openFDA.txt

echo integrate mapping with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"


$path_neo4j/cypher-shell -u neo4j -p $password -f FDA_mappings/cypher.cypher

sleep 60

python ../../restart_neo4j.py $path_neo4j > neo4.txt

sleep 120

############################## edges #################################


now=$(date +"%F %T")
echo "Current time: $now"
echo disease-chemical

python3 DrugAdverseEvent_indication_Chemical_Disease_Edge.py $path_to_project > output/output_Ch_D_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo symptom-chemical


python3 DrugAdverseEvent_indication_Chemical_Symptom_Edge.py $path_to_project > output/output_Ch_S_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo chemical-chemical


python3 SubstanceData_Chemical_Chemical_Edge.py $path_to_project > output/output_Ch_Ch_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo chemical-output_side_effect

python3 DrugAdverseEvent_Chemical_SideEffect_Edge.py $path_to_project > output/output_Ch_SE_edge.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate connection with cypher shell


$path_neo4j/cypher-shell -u neo4j -p $password -f FDA_edges/edge_cypher.cypher

sleep 60

python ../../restart_neo4j.py $path_neo4j > neo4.txt

sleep 120

