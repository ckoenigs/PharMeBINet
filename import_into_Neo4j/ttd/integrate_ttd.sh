#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3


echo load latest version of TTD and generat GraphML file

dir=./sources/

# prepare workspace and add TTD to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . TTD

fi

java -jar ../$biodwh2.jar -u .

echo $import_tool


echo integrate TTD into neo4j

java -jar ../$import_tool.jar -i sources/TTD/intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password test --label-prefix TTD_ > output/import_tool_output.txt

sleep 120

$path_neo4j/neo4j restart


sleep 120




