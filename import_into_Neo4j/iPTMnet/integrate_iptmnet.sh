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

echo load latest version of iPTMnet and generate GraphML file

dir=./sources/

# prepare workspace and add TTD to bioDWB2 tool
if [ ! -d "$dir" ];
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . iPTMnet

fi

java -jar ../$biodwh2.jar -u .

echo $import_tool

echo integrate iPTMnet into neo4j

java -jar ../$import_tool.jar -i sources/iPTMnet/intermediate.graphml.gz  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix iPTMnet_ --indices "iPTMnet_Protein.uniprot_id;iPTMnet_Protein.uniprot_accession;iPTMnet_Organism.ncbi_taxid" > output/import_tool_output.txt

echo finished integration

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30