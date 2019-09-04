#!/bin/bash

mondo="mondo.cypher"
echo $mondo


if [[ $# -ne 2 ]]
then
    echo "path to neo4j is missing path to newest neo4j and save path"
    exit 1
fi
#define path to neo4j bin
#path_neo4j=/home/cassandra/Dokumente/hetionet/neo4j-community-3.1.6/bin
path_neo4j_original=$1
path_neo4j_newest_version=$2



now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j stop
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo start the newerst version

$path_neo4j_newest_version graph restart 

sleep 180

#generate the cypher files from the neo4j database with apoc
#python generate_cypher_file.py > output_program.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_newest_version graph stop
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo start the original version

$path_neo4j_original/neo4j start

sleep 120

#integrate the mondo information into the other database
cat $mondo | $path_neo4j_original/cypher-shell -u neo4j -p test > output_cypher_integration.txt
echo integrated

now=$(date +"%F %T")
echo "Current time: $now"

cat single_node_without_connection.cypher |  $path_neo4j_original/cypher-shell -u neo4j -p test > output_cypher_integration_singel.txt

sleep 180

$path_neo4j_original/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo nodes without parents
python nodes_without_a_upper_node.py > output_nodes_without_parents.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j stop

now=$(date +"%F %T")
echo "Current time: $now"
echo start the newerst version

$path_neo4j_newest_version graph restart

sleep 120

echo get a parent
python find_connection_for_nodes_without_upper_nodes.py > output_found_parents.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_newest_version graph stop

sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo start the newerst version

$path_neo4j_original/neo4j start

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo prepare subclass relationships

python prepare_relationship_subclass.py > output_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j-shell -file cypher_rela.cypher > output_cypher_integration_rela.txt

sleep 180

$path_neo4j_original/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo hierarchy
python get_hierarchy_mondo.py > output_hierarchy.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j-shell -file integrate_level.cypher > output_cypher_integration_hierarchy.txt

sleep 180

$path_neo4j_original/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"




