#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2


now=$(date +"%F %T")
echo "Current time: $now"
echo gene and disease

python3 mapping_to_SideEffect.py $path_to_project > output/output_side_effect.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo gene and disease

python3 mapping_CAERSReport_reaction_openFDA.py $path_to_project > output/output_map_CAERSReport.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_DrugAdverseEvent_drug_openfda_openFDA.py $path_to_project > output/output_map_DAE_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_DrugAdverseEvent_reaction_openfda_openFDA.py $path_to_project > output/output_map_DAE_reaction_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_DrugRecallEnforcementReport_openfda_openFDA.py $path_to_project > output/output_map_DrugRecall.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_NationalDrugCodeDirectory_openFDA.py $path_to_project > output/output_mapping_National.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_SubstanceData_openFDA.py $path_to_project > output/output_SubstanceData_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_SubstanceData_relationships_substance_openFDA.py $path_to_project > output/output_SubstanceData_relationship_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_SubstanceData_substance_openFDA.py $path_to_project > output/output_SubstanceData_openFDA.txt

now=$(date +"%F %T")
echo "Current time: $now"

python3 mapping_SubstanceData_moieties_openFDA.py $path_to_project > output/output_SubstanceData_moieties_openFDA.txt

echo integrate connection with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"


$path_neo4j/cypher-shell -u neo4j -p test -f FDA_mappings/cypher.cypher

sleep 60

$path_neo4j/neo4j restart

sleep 120
