#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3


if [ ! -d output ]; then
  mkdir output
  mkdir chemical
  mkdir disease
  mkdir gene
  mkdir GO
  mkdir interaction
fi

rm output/cypher.cypher


now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid gene'

python3 mapping_gene_bioGrid.py $path_to_project > gene/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid chemical'

python3 map_chemical_biogrid.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid disease'

python3 mapping_disease_biogrid.py $path_to_project > disease/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Map bioGrid chemical'

python3 map_go_bioGrid.py $path_to_project > GO/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate mappings into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 60



now=$(date +"%F %T")
echo "Current time: $now"
echo 'Merge ppi'

python3 merge_ppi.py $path_to_project > interaction/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'Merge biogrid protein-chemical'

python3 merge_protein_chemical_interaction.py $path_to_project > interaction/output_c_p.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate rela into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
sleep 60
