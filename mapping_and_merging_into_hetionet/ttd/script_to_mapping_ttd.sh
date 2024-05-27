#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

echo ttd

# prepare directories
if [ ! -d output ]; then
  mkdir output
  mkdir data
  mkdir drug
  mkdir edges
  mkdir disease
  mkdir protein
  mkdir pathway
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

# it has only connection to target and this edge information are from other source like Wikipathways
# but I have wikipathways included and there are edges which I do not have which might be because of 
# an older version. So, I decide against this.
# python3 map_pathway_ttd.py $path_to_project > pathway/output_integration_pathway.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo protein

python3  map_protein_ttd.py $path_to_project > protein/output_mapping_proteins.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug

python3 map_drug_ttd.py $path_to_project > drug/output_integration_drug.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo compound

python3 map_compound_ttd.py $path_to_project > drug/output_integration_compound.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo disease

python3 map_disease_ttd.py $path_to_project > disease/output_integration_compound.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ttd mapping and nodes into hetionet

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

sleep 40
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-disease treat

python3 merge_drug_disease_indicates_edges.py $path_to_project > edges/output_integration_compound_indicates.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo drug-target edge

python3 merge_chemical_target_edges.py $path_to_project > edges/output_integration_chemical_target.txt



now=$(date +"%F %T")
echo "Current time: $now"
echo integration of ttd edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edges.cypher > output/cypher2.txt

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 60

