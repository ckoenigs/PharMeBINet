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
fi
if [ ! -d data ]; then
  mkdir data
  cd data
  wget "https://evs.nci.nih.gov/ftp1/NDF-RT/Archive/NDFRT_Public_All 2018-02-05.zip"
  unzip "NDFRT_Public_All 2018-02-05.zip"
  mv NDFRT_Public_2018.02.05/NDFRT_Public_2018.02.05_TDE.xml ./
  rm "NDFRT_Public_All 2018-02-05.zip"
  rm -r NDFRT_Public_2018.02.05
  cd ..
fi
if [ ! -d results ]; then
  mkdir results
fi

python3 prepare_ndf_rt_to_neo4j_integration.py $path_to_project > output_integration_ndf_rt.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate ndf-rt into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_file.cypher > output/cypher.txt
python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_file_edge.cypher > output/cypher2.txt

sleep 20

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30
echo delete ndf-rt nodes without relaionships

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_file_delete.cypher > output/cypher1.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30