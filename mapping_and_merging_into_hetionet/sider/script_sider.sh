#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

#path to stich data directory
path_to_stich=$4

# prepare directories
if [ ! -d output ]; then
  mkdir output
  mkdir $path_to_stich/StitchData
  wget -P $path_to_stich/StitchData/ http://stitch.embl.de/download/chemicals.v5.0.tsv.gz
  wget -P $path_to_stich/StitchData/ http://stitch.embl.de/download/chemicals.inchikeys.v5.0.tsv.gz
  wget -P $path_to_stich/StitchData/ http://stitch.embl.de/download/chemical.sources.v5.0.tsv.gz
fi

echo se
python3 map_Sider_se.py $path_to_project > output/output_map_se.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo drug
python3 map_sider_drug.py $path_to_project $path_to_stich > output/output_map_drug.txt

echo integrate mapping with cypher shell
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 40

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-se edges
python3 integrate_rela_drug_side_effect.py $path_to_project > output/output_map_rela.txt

echo integrate relationships
now=$(date +"%F %T")
echo "Current time: $now"

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher2.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

