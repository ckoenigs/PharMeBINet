#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# prepare directories
if [ ! -d output ]; then
  mkdir output
  mkdir disease
  mkdir drug
  mkdir chemical_ingredient
  mkdir chemical_pharmacological
  mkdir ingredient
  mkdir pharmacologicClass
  mkdir relationships
fi

echo ndf-rt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 map_NDF-RT_disease_final.py $path_to_project > disease/output_map_ndf_rt_disease.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drugs

python3  map_NDF_RT_drug.py $path_to_project > drug/output_map_ndf_rt_drugs.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo ingredient

python3  mapping_ingredient_to_chemical.py $path_to_project > ingredient/output_map_ndf_rt.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo pharmacologic class mapping

python3  mapping_to_pc_ndf_rt.py $path_to_project > pharmacologicClass/output_map_ndf_rt.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ndf-rt connection into pharmebinet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30



now=$(date +"%F %T")
echo "Current time: $now"
echo drugs-disease rela

python3  integrate_ndf_rt_drug_disease_rela.py $path_to_project > relationships/output_map_ndf_rt_rela.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo pharmacologic class chemical rela

python3  integrate_rela_between_chemical_and_pharmacologicalClass.py $path_to_project > chemical_pharmacological/output_map_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo pharmacologic class chemical rela

python3  integrate_rela_between_chemical_ingredient.py $path_to_project > chemical_ingredient/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ndf-rt connection into pharmebinet

python ../../execute_cypher_shell.py $path_neo4j $password relationships/cypher.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 60
