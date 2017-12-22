#!/bin/bash

echo $#
number_of_arguments=6

if test $# -ne $number_of_arguments 
then
    echo need 6 arguments:
    echo 1 path to neo4j bin
    echo 2 path to sider data
    echo 3 path to ctd data
    echo 4 path to ndf-rt data
    echo 5 path to aeolus data
    echo 6 path to disease ontology data
    exit 0
fi 


#define path to neo4j bin
path_neo4j=$1

# sider path
sider_path=$2

# ctd path
ctd_path=$3

# ndf-rt path
ndf_rt_path=$4

# aeolus path
aeolus_path=$5

# DO PATH with obo file
do_path=$6

now=$(date +"%F %T")
echo "Current time: $now"

echo integration of the database into hetionet
# ths python scripts executed on windows with python 3.5.3
cd import_into_Neo4j

./integration_shell.sh $path_neo4j $sider_path $ctd_path $ndf_rt_path $aeolus_apth $do_path

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

echo mapping and integration
cd mapping_and_merging_into_hetionet

./script_mapping.sh $path_neo4j

now=$(date +"%F %T")
echo "Current time: $now"



