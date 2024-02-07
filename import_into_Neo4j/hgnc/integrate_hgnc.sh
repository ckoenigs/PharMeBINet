#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3

#password
password=$4


echo load latest version of hgnc and generat GraphML file

dir=./sources/

# prepare workspace and add TTD to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . HGNC

fi

java -jar ../$biodwh2.jar -u .

echo $import_tool


echo integrate hgnc into neo4j

java -jar ../$import_tool.jar -i sources/HGNC/intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix hgnc_ --indices "hgnc_Gene.id;hgnc_miRNA.mirbase_accession;hgnc_Protein.uniprot_id" > output/import_tool_output.txt

echo finished integration

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30
