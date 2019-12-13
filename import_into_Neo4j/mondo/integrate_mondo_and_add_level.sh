#!/bin/bash

mondo="mondo.cypher"
echo $mondo


if [[ $# -ne 3 ]]
then
    echo "path to neo4j is missing path to newest neo4j and save path"
    exit 1
fi
#define path to neo4j bin
#path_neo4j=/home/cassandra/Dokumente/hetionet/neo4j-community-3.1.6/bin
path_neo4j_original=$1
path_neo4j_newest_version=$2
#path to project
path_to_project=$3



now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j stop
sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo start the newerst version

$path_neo4j_newest_version scigraph/graph restart

sleep 180

#generate the cypher files from the neo4j database with apoc
python3 generate_cypher_file.py > output_program.txt
#cat cypher_extract_information.cypher | $path_neo4j_original/cypher-shell -u neo4j -p test

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_newest_version scigraph/graph stop
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

# remove the disease nodes which do not contains mondo identifier
cat remove_nodes_without_mondo.cypher |  $path_neo4j_original/cypher-shell -u neo4j -p test > output_cypher_integration_singel.txt

sleep 180

$path_neo4j_original/neo4j restart


sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo nodes without parents
python3 nodes_without_a_upper_node.py > output_nodes_without_parents.txt


now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j stop

now=$(date +"%F %T")
echo "Current time: $now"
echo start the newerst version

$path_neo4j_newest_version scigraph/graph restart

sleep 120

echo get a parent
python3 find_connection_for_nodes_without_upper_nodes.py $path_to_project > output_found_parents.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_newest_version scigraph/graph stop

sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo start the newerst version

$path_neo4j_original/neo4j start

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo prepare subclass relationships

python3 prepare_relationship_subclass.py $path_to_project > output_rela.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j-shell -file cypher_rela.cypher > output_cypher_integration_rela.txt

sleep 180

$path_neo4j_original/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo hierarchy
python3 get_hierarchy_mondo.py $path_to_project > output_hierarchy.txt

now=$(date +"%F %T")
echo "Current time: $now"

$path_neo4j_original/neo4j-shell -file integrate_level.cypher > output_cypher_integration_hierarchy.txt

sleep 180

$path_neo4j_original/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"




