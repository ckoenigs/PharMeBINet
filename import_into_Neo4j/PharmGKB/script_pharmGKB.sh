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

echo load latest version of pharmGKB and generat GraphML file

dir=./sources

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

java -jar ../$import_tool.jar -i sources/PharmGKB/intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix PharmGKB_ --indices "PharmGKB_Chemical.id;PharmGKB_ClinicalAnnotation.id;PharmGKB_DrugLabel.id;PharmGKB_Gene.id;PharmGKB_Haplotype.id;PharmGKB_HaplotypeSet.id;PharmGKB_Literature.id;PharmGKB_Pathway.id;PharmGKB_Phenotype.id;PharmGKB_StudyParameters.id;PharmGKB_Variant.id;PharmGKB_VariantAnnotation.id;PharmGKB_GuidelineAnnotation.id" #> output/import_tool_output.txt
#java -jar ../$import_tool.jar -i sources/PharmGKB/intermediate.graphml.gz  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix PharmGKB_ --indices "PharmGKB_Chemical.id;PharmGKB_ClinicalAnnotation.id;PharmGKB_DrugLabel.id;PharmGKB_Gene.id;PharmGKB_Haplotype.id;PharmGKB_HaplotypeSet.id;PharmGKB_Literature.id;PharmGKB_Pathway.id;PharmGKB_Phenotype.id;PharmGKB_StudyParameters.id;PharmGKB_Variant.id;PharmGKB_VariantAnnotation.id;PharmGKB_GuidelineAnnotation.id" #> output/import_tool_output.txt

python ../../execute_cypher_shell.py $path_neo4j $password cypher_add_label.cypher > output/cypher.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt


sleep 30




