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


$path_neo4j/restart_neo4j.sh graph stop

$path_neo4j/restart_neo4j.sh hetionet restart

sleep 30

suffix="_hetionet"

now=$(date +"%F %T")
echo "Current time: $now"
echo 'extract as graphml'

# create cypher file with query with variable path
echo 'CALL apoc.export.graphml.all("'$path_to_project'import_into_Neo4j/Hetionet/data/hetionet.graphml", {batchSize:10000, readLabels: true, storeNodeIds: false, useTypes: true});' > export_hetionet.cypher

python ../../execute_cypher_shell.py $path_neo4j $password export_hetionet.cypher > output/cypher.txt

sleep 30

$path_neo4j/neo4j stop


sleep 30

$path_neo4j/restart_neo4j.sh graph restart

sleep 30

now=$(date +"%F %T")
echo "Current time: $now"
echo 'import with tool'

java -jar ../$import_tool.jar -i $path_to_project"import_into_Neo4j/Hetionet/data/hetionet.graphml"  -e bolt://localhost:7687 --username neo4j --password $password --label-suffix $suffix --modify-edge-labels false --indices "Pathway_hetionet.identifier;SideEffect_hetionet.identifier;CellularComponent_hetionet.identifier;Anatomy_hetionet.identifier;Symptom_hetionet.identifier;Disease_hetionet.identifier;BiologicalProcess_hetionet.identifier;Gene_hetionet.identifier;PharmacologicClass_hetionet.identifier;MolecularFunction_hetionet.identifier;Compound_hetionet.identifier;CellularComponent_hetionet.name;BiologicalProcess_hetionet.name;PharmacologicClass_hetionet.name;Disease_hetionet.name;Gene_hetionet.name;SideEffect_hetionet.name;Pathway_hetionet.name;Compound_hetionet.name;MolecularFunction_hetionet.name;Symptom_hetionet.name;Anatomy_hetionet.name" > output/import_tool_output.txt

sleep 30

python ../../restart_neo4j.py $path_neo4j > output/neo4.txt

sleep 30


