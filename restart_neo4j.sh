#!/bin/bash
#echo $#
if test $# -eq 2
then
    echo $1
    #../../../../../mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j_databases/
    sed "/initial.dbms.default_database=/c initial.dbms.default_database=$1" < /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j.conf > /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j_2.conf

    cp /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j_2.conf /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j.conf

    /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/bin/neo4j $2
else
    
    sed "/initial.dbms.default_database=/c initial.dbms.default_database=neo4j" < /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j.conf > /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j_2.conf 

    cp /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j_2.conf /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/conf/neo4j.conf

    /mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-5.15.0/bin/neo4j $1

fi 


