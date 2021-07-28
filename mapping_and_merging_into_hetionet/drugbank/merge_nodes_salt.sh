#!/bin/bash
#define path to neo4j bin
path_neo4j=$1

python3 ../add_info_from_removed_node_to_other_node.py DB00729 DBSALT002847 Compound
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
 echo "Current time: $now"
python3 ../add_info_from_removed_node_to_other_node.py DB01040 DBSALT002848 Compound
$path_neo4j/cypher-shell -u neo4j -p test -f cypher_merge.cypher 

now=$(date +"%F %T")
 echo "Current time: $now"
