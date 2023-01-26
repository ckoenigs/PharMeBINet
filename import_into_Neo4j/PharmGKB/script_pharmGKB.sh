#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3

#password
password=$4


echo load latest version of pharmGKB and generat GraphML file

dir=./sources/

# prepare workspace and add pharmGKB to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c .

    java -jar ../$biodwh2.jar --add-data-source . PharmGKB

fi

java -jar ../$biodwh2.jar -u .

echo $import_tool

echo integrate PharmGKB into neo4j

java -jar ../$import_tool.jar -i sources/PharmGKB/intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix PharmGKB_ --indices "PharmGKB_Chemical.id;PharmGKB_ClinicalAnnotation.id;PharmGKB_DrugLabel.id;PharmGKB_Gene.id;PharmGKB_Haplotype.id;PharmGKB_HaplotypeSet.id;PharmGKB_Literature.id;PharmGKB_Pathway.id;PharmGKB_Phenotype.id;PharmGKB_StudyParameters.id;PharmGKB_Variant.id;PharmGKB_VariantAnnotation.id;PharmGKB_GuidelineAnnotation.id" > output/import_tool_output.txt


$path_neo4j/cypher-shell -u neo4j -p $password -f cypher_add_label.cypher

sleep 120

$path_neo4j/neo4j restart


sleep 120




