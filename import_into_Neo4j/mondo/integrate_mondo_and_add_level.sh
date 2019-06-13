#!/bin/bash

mondo="mondo.cypher"
echo $mondo



#define path to neo4j bin
#path_neo4j=/home/cassandra/Dokumente/hetionet/neo4j-community-3.1.6/bin
path_neo4j=$1
if [[ $# -eq 0 ]]
then
    echo "path to neo4j is missing"
    exit 1
fi

now=$(date +"%F %T")
echo "Current time: $now"
read -p "Press any key if monarch scigraph in neo4j is started (APOC is needed as a plugin)" -n1 -s
echo ''

echo -n "Enter path to dictionary to save the cypher files (with / at the end):"
read  var_path
echo ''

#generate the cypher files from the neo4j database with apoc
python generate_cypher_file.py $var_path > output_program.txt
echo $var_path


now=$(date +"%F %T")
echo "Current time: $now"
read -p "Press any key if the original database in neo4j is started " -n1 -s
echo ''


#integrate the mondo information into the other database
path_mondo="$var_path/$mondo"
$path_neo4j/neo4j-shell -file $path_mondo > output_cypher_integration.txt
echo $path_mondo

now=$(date +"%F %T")
echo "Current time: $now"

path_singel="$var_path/single_node_without_connection.cypher"
$path_neo4j/neo4j-shell -file $path_singel > output_cypher_integration_singel.txt

sleep 180j

$path_neo4j/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo nodes without parents
python nodes_without_a_upper_node.py > output_nodes_without_parents.txt


now=$(date +"%F %T")
echo "Current time: $now"
read -p "Press any key if monarch scigraph in neo4j is started" -n1 -s
echo ''
echo found parents

python find_connection_for_nodes_without_upper_nodes.py > output_found_parents.txt

now=$(date +"%F %T")
echo "Current time: $now"
read -p "Press any key if in original database in neo4j is started" -n1 -s
echo ''
_hi
now=$(date +"%F %T")
echo "Current time: $now"
echo hierarchy
python get_hierarchy_mondo.py > output_hierarchy.txt

now=$(date +"%F %T")
echo "Current time: $now"

path_singel="$var_path/single_node_without_connection.cypher"
$path_neo4j/neo4j-shell -file integrate_level.cypher > output_cypher_integration_hierarchy.txt

sleep 180

$path_neo4j/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"




