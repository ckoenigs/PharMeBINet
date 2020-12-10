#!/usr/bin/env bash


for i in {1..40}
do
    echo $i
    now=$(date +"%F %T")
    echo "Current time: $now"
    ../../../../neo4j-community-3.2.9/bin/cypher-shell -u neo4j -p test 'Match p=(:Chemical)-[r]-(:Gene) Where r.ctd="yes" and r.hetionet="no" With r Limit 10000 Delete r;'
done