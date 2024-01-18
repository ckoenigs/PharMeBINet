#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

# define bioDWH2 tool
biodwh2=$3

#password
password=$4

#path other data source space
path_data_source=$5


echo load latest version of DrugCentral and generat GraphML file

dir=$path_data_source/drugcentral/sources/

# prepare workspace and add DrugCentral to bioDWB2 tool
if [ ! -d "$dir" ]; 
then
    echo generate workspace in directory
    java -jar ../$biodwh2.jar -c $path_data_source/drugcentral

    java -jar ../$biodwh2.jar --add-data-source $path_data_source/drugcentral DrugCentral
    # if not all is exported then the config need to be changed
    # dataSourceProperties: "DrugCentral" : { "forceExport" : false, "skipLINCSSignatures" : true, "skipFAERSReports" : true, "skipDrugLabelFullTexts" : true }

fi

java -jar ../$biodwh2.jar -u $path_data_source/drugcentral

echo $import_tool


echo integrate DurgCentral into neo4j

java -jar ../$import_tool.jar -i $path_data_source/drugcentral/sources/DrugCentral/intermediate.graphml  -e bolt://localhost:7687 --username neo4j --password $password --label-prefix DC_ --indices "DC_ATC.id;DC_ATCDDD.id;DC_ActionType.id;DC_ActiveIngredient.id;DC_Approval.id;DC_AttributeType.id;DC_Bioactivity.id;DC_DOTerm.id;DC_DOTermXref.id;DC_DataSource.id;DC_DbVersion.id;DC_DrugClass.id;DC_DrugLabel.id;DC_GOTerm.id;DC_Identifier.id;DC_IdentifierType.id;DC_InnStem.id;DC_OMOPConcept.id;DC_OrangeBookExclusivity.id;DC_OrangeBookPatent.id;DC_OrangeBookProduct.id;DC_PDB.id;DC_ParentDrugMolecule.id;DC_PharmaClass.id;DC_Product.id;DC_Property.id;DC_Reference.id;DC_Structure.id;DC_Synonyms.id;DC_Target.id;DC_TargetComponent.id;DC_TargetKeyword.id;DC_VetOmop.id;DC_VetProd.id" > output/import_tool_output.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > neo4.txt


sleep 30




