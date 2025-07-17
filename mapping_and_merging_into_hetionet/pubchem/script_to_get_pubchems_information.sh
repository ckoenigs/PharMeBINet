#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to project
path_to_project=$2

#password
password=$3

# path to data
path_to_data=$4

# license
license="https://www.ncbi.nlm.nih.gov/home/about/policies/"


if [ ! -d output ]; then
  mkdir output
  mkdir data
  mkdir chemical
fi

sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4.txt
sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo "snp information for integrated dbSNP nodes"

python3 get_pubchem_from_api.py $path_to_project  > output/output.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo integrat dbSNP information into Neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

now=$(date +"%F %T")
echo "Current time: $now"


sleep 60
python ../../restart_neo4j.py $path_neo4j > output/neo4j1.txt
sleep 60



now=$(date +"%F %T")
echo "Current time: $now"
echo map and integrate dbSNP

python3 merge_pubchem_compounds.py $path_to_project > chemical/output.txt


now=$(date +"%F %T")
echo "Current time: $now"
echo integrat mapping dbSNP information into Neo4j

python ../../execute_cypher_shell.py $path_neo4j $password chemical/cypher.cypher > output/cypher4.txt


sleep 30
python ../../restart_neo4j.py $path_neo4j > output/neo4j2.txt

sleep 60
