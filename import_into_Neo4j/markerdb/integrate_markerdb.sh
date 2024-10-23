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

echo load latest version of MarkerDB and generate GraphML file

dir=./sources/

# prepare workspace and add TTD to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . MarkerDB

fi

java -jar ../$biodwh2.jar -u .

echo $import_tool

echo Unpacking GraphML files

echo integrate markerdb into neo4j

java -jar ../$import_tool.jar -i sources/MarkerDB/intermediate.graphml.gz  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix MarkerDB_ --indices "MarkerDB_Chemical.hmdb_id;MarkerDB_Condition.name;MarkerDB_Gene.id;MarkerDB_Protein.uniprot_id;MarkerDB_Protein.id;MarkerDB_SequenceVariant.variation;MarkerDB_SequenceVariant.id" > output/import_tool_output.txt

echo finished integration

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30
