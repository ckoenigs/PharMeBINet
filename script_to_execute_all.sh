#!/bin/bash

echo $#
number_of_arguments=1

if test $# -ne $number_of_arguments 
then
    echo need 1 arguments:
    # /home/cassandra/Dokumente/neo4j-community-3.2.9/bin
    echo 1 path to neo4j bin
    exit 0
fi 


#define path to neo4j bin
path_neo4j=$1


now=$(date +"%F %T")
echo "Current time: $now"

echo integration of the database into hetionet
# ths python scripts executed on windows with python 3.5.3
cd import_into_Neo4j

./integration_shell.sh $path_neo4j > output_all_integration.txt

cd ..

echo cp database

#cp -r /home/cassandra/Dokumente/neo4j-community-3.2.9/data/databases/graph.db /home/cassandra/Dokumente/neo4j-community-3.2.9/data/databases/inte.db

now=$(date +"%F %T")
echo "Current time: $now"

echo mapping and integration
cd mapping_and_merging_into_hetionet

./script_mapping.sh $path_neo4j > output_mapping.txt

now=$(date +"%F %T")
echo "Current time: $now"



