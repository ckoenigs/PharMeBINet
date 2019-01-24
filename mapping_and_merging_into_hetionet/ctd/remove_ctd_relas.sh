#!/usr/bin/env bash

#for i in {1..100}
#do
#    echo $i
#    now=$(date +"%F %T")
#    echo "Current time: $now"
#    ../../../../neo4j-community-3.2.9/bin/cypher-shell -u neo4j -p test 'MATCH ()-[r:associates_GD]->() With r  LIMIT 100000 Delete r;'
#done

for i in {1..60}
do
    echo $i
    now=$(date +"%F %T")
    echo "Current time: $now"
    ../../../../neo4j-community-3.2.9/bin/cypher-shell -u neo4j -p test 'MATCH ()-[r:associates_CD]->() With r  LIMIT 100000 Delete r;'
done