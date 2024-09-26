#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# define import tool
import_tool=$2

#password
password=$3

#path other data source space
path_to_project=$4


# prepare directories
if [ ! -d output ]; then
  mkdir output
fi

# if reactome is with another version
# JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/ 
# path_neo4j_other='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/neo4j/neo4j-community-4.4.16/bin'
path_neo4j_other=$path_neo4j

$path_neo4j/restart_neo4j.sh graph stop

#$path_neo4j_other/restart_neo4j.sh reactome restart
$path_neo4j/restart_neo4j.sh hetionet restart

sleep 30

suffix="_hetionet"

now=$(date +"%F %T")
echo "Current time: $now"
echo 'extract as graphml'

# $path_neo4j_other/cypher-shell -u neo4j -p $password -f export_reactome.cypher
python ../../execute_cypher_shell.py $path_neo4j $password export_hetionet.cypher > output/cypher.txt

sleep 30

#$path_neo4j_other/neo4j stop
$path_neo4j/neo4j stop


sleep 30

$path_neo4j/restart_neo4j.sh graph restart

sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo 'import with tool'

java -jar ../$import_tool.jar -i $path_to_project"import_into_Neo4j/Hetionet/data/pathwaydata.graphml"  -e bolt://localhost:7687 --username neo4j --password $password --label-suffix $suffix --modify-edge-labels false --indices "Pathway_hetionet.identifier;SideEffect_hetionet.identifier;CellularComponent_hetionet.identifier;Anatomy_hetionet.identifier;Symptom_hetionet.identifier;Disease_hetionet.identifier;BiologicalProcess_hetionet.identifier;Gene_hetionet.identifier;PharmacologicClass_hetionet.identifier;MolecularFunction_hetionet.identifier;Compound_hetionet.identifier;CellularComponent_hetionet.name;BiologicalProcess_hetionet.name;PharmacologicClass_hetionet.name;Disease_hetionet.name;Gene_hetionet.name;SideEffect_hetionet.name;Pathway_hetionet.name;Compound_hetionet.name;MolecularFunction_hetionet.name;Symptom_hetionet.name;Anatomy_hetionet.name" > output/import_tool_output.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 30


