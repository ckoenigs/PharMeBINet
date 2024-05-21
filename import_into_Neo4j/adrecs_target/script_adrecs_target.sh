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
  wget  -O data/ALLDRUG_INFO.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/ALLDRUG_INFO.xlsx"
  wget  -O data/V_D_A.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/V_D_A.xlsx"
  wget  -O data/ADRAlert2GENE2ID.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/ADRAlert2GENE2ID.xlsx"
  wget  -O data/P_D_A.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/P_D_A.xlsx"
  wget  -O data/ALLTOXI_INFO.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/ALLTOXI_INFO.xlsx"
  wget  -O data/SNP_Variation_INFO.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/SNP_Variation_INFO.xlsx"
  wget  -O data/ADRAlert_LINCS_Gene_inf.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/ADRAlert_LINCS_Gene_inf.xlsx"
  wget  -O data/ADReCS_Target_INFO.xlsx "http://www.bio-add.org/ADReCS-Target/files/download/ADReCS_Target_INFO.xlsx"
fi


now=$(date +"%F %T")
echo "Current time: $now"

echo prepare ADReCS-Target integration

# run preparation adrecs-target
python3 prepare_files.py $path_to_project > output/output.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target nodes into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher.cypher > output/cypher.txt

# sleep 60

# python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


# sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

echo integrate adrecs target rela into neo4j

python ../../execute_cypher_shell.py $path_neo4j $password output/cypher_rela.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4j.txt


sleep 30