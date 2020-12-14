#!/bin/bash
python3 ../add_information_from_a_not_existing_node_to_existing_node.py DB00729 DBSALT002847 Compound
now=$(date +"%F %T")
 echo "Current time: $now"
python3 ../add_information_from_a_not_existing_node_to_existing_node.py DB01040 DBSALT002848 Compound
now=$(date +"%F %T")
 echo "Current time: $now"
