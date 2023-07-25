#!/bin/bash

echo $#
number_of_arguments=2

if test $# -ne $number_of_arguments 
then
    echo need 2 arguments:
    # /home/cassandra/Dokumente/neo4j-community-3.2.9/bin
    echo 1 path to neo4j bin
    echo 2 path to project
    exit 0
fi 


#define path to neo4j bin
path_neo4j=$1

#path to project
path_project=$2

# path to import tool
name_of_import_tool='../Neo4j-GraphML-Importer-v1.2.0'

password='test1234'

echo $path_project

now=$(date +"%F %T")
echo "Current time: $now"

echo integration of the database into hetionet
# ths python scripts executed on windows with python 3.5.3
cd import_into_Neo4j

./integration_shell.sh $path_neo4j $path_project $name_of_import_tool $password #> output_all_integration.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo cp database

$path_neo4j/neo4j stop

sleep 120

cp -r /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j_databases/graph /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j_databases/inte.db

$path_neo4j/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"

echo mapping and integration
cd mapping_and_merging_into_hetionet

./script_mapping.sh $path_neo4j $path_project $password #> output_mapping.txt

cd ..


exit 1
now=$(date +"%F %T")
echo "Current time: $now"
echo cp database
sleep 120

$path_neo4j/neo4j stop

sleep 180

echo delete source nodes
now=$(date +"%F %T")
echo "Current time: $now"

cd final_preparation

./new_preparation_script.sh $path_neo4j $name_of_import_tool $password #> output_delete_source.txt

now=$(date +"%F %T")
echo "Current time: $now"

#[ ]*[0-9]+K[\. ]+[0-9]+\%[ ]+[0-9,]+M[ =][0-9,ms]+\n



