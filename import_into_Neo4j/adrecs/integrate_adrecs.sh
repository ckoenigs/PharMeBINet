#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3

#password
password=$4


echo load latest version of ADReCS and generat GraphML file

dir=./sources/

# prepare workspace and add ADReCS to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . ADReCS

fi

java -jar ../$biodwh2.jar -u .

echo $import_tool


echo integrate ADReCS into neo4j

java -jar ../$import_tool.jar -i sources/ADReCS/intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix ADReCS_ --indices "ADReCS_Drug.id;ADReCS_ADR.id" > output/import_tool_output.txt

sleep 30

$path_neo4j/neo4j restart


sleep 30




