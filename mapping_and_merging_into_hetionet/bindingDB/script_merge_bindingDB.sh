#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# path to data
path_to_data=$4

if [ ! -d output ]; then
  mkdir output
  mkdir chemical
  mkdir complex
  mkdir ERS
  mkdir protein
fi


if [ ! -f ../pubchem/output/inchikey_to_pubchem.tsv ]; then
  echo "not found"
  cd ../pubchem
  python download_files_and_prepare_inchikey_to_pubchem_file.py $path_to_data > output/pubchem_prep.txt
  cd ../bindingDB
fi

now=$(date +"%F %T")
echo "Current time: $now"
echo protein mapping
python3 map_protein_bindingdb.py $path_to_project > protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo drug mapping
python3 map_chemical_bindingdb.py $path_to_project > chemical/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map drug and outcome

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt
python ../../check_indices.py



now=$(date +"%F %T")
echo "Current time: $now"
echo complex integration
python3 prepare_complex_edge.py $path_to_project > protein/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrate complex

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge.cypher > output/cypher2.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
python ../../check_indices.py


now=$(date +"%F %T")
echo "Current time: $now"
echo ers integration
python3 prepare_ERS_edge.py $path_to_project > ERS/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrate map ers and the edges

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_edge_2.cypher > output/cypher3.txt

python ../../check_indices.py

python ../../restart_neo4j.py $path_neo4j > output/neo4j2.txt
python ../../check_indices.py

