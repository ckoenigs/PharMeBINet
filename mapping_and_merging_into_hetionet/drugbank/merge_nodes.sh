#!/bin/bash
 #define path to neo4j bin
path_neo4j=$1

password=$2

python3 ../add_info_from_removed_node_to_other_node.py DB01398 DB00936 Compound
python ../../execute_cypher_shell.py $path_neo4j $password cypher_merge.cypher > cypher1.txt 

now=$(date +"%F %T")
                        echo "Current time: $now"
