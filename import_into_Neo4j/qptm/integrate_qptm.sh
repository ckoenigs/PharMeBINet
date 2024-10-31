#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3

#password
password=$4

# prepare directories
if [ ! -d output ]; then
  mkdir output
fi

echo load latest version of qPTM and generate GraphML file

dir=./sources/

if [ ! -d "$dir" ];
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . qPTM

    java -jar ../$biodwh2.jar --set-config . "dataSourceProperties.qPTM.downloadUrl"
fi

java -jar ../$biodwh2.jar -u .

echo $import_tool

echo integrate qPTM into neo4j

java -jar ../$import_tool.jar -i sources/qPTM/intermediate.graphml.gz  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix qPTM_ --indices "qPTM_Protein.uniprot_id;qPTM_ORGANISM.ncbi_taxid" > output/import_tool_output.txt

echo finished integration

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30