#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

echo $import_tool

echo integrate DurgCentral into neo4j

java -jar ../$import_tool.jar -i intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password test --label-prefix DC_ > output/import_tool_output.txt
#  --indices "PharmGKB_Chemical.id;PharmGKB_ClinicalAnnotation.id;PharmGKB_ClinicalAnnotationMetadata.id;PharmGKB_DrugLabel.id;PharmGKB_Gene.id;PharmGKB_Haplotype.id;PharmGKB_HaplotypeSet.id;PharmGKB_Literature.id;PharmGKB_Pathway.id;PharmGKB_Phenotype.id;PharmGKB_StudyParameters.id;PharmGKB_Variant.id;PharmGKB_VariantAnnotation.id"

sleep 120

$path_neo4j/neo4j restart


sleep 120




