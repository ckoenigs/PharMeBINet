#!/usr/bin/env bash


for i in {1..10}
do
    echo $i
    now=$(date +"%F %T")
    echo "Current time: $now"
    ../../../../neo4j-community-3.2.9/bin/cypher-shell -u neo4j -p test 'MATCH ()-[r:CAUSES_CcSE]->() Where r.aeolus="yes" and r.sider="no" and r.hetionet="no" and r.ctd="no" With r  LIMIT 100000 Delete r;'
done
#
