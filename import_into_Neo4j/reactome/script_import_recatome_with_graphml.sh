#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

# path to reactome graphml
path_to_reactome='/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/reactome/'

$path_neo4j/restart_neo4j.sh reactome restart

sleep 60

suffix="_reactome"

now=$(date +"%F %T")
echo "Current time: $now"
echo 'extract as property types'

python3 get_property_types.py $suffix > output/output_preparation.txt

now=$(date +"%F %T")
echo "Current time: $now"
echo 'extract as graphml'

$path_neo4j/cypher-shell -u neo4j -p test -f export_reactome.cypher

sleep 60

$path_neo4j/neo4j restart


sleep 120

$path_neo4j/restart_neo4j.sh graph restart

sleep 60

now=$(date +"%F %T")
echo "Current time: $now"
echo 'import with tool'

java -jar ../Neo4j-GraphML-Importer-v1.1.4.jar -i $path_to_reactome"pathwaydata.graphml"  -e bolt://localhost:7687 --username neo4j --password test --label-suffix $suffix --modify-edge-labels false --indices "DatabaseObject_reactome.dbId;EntitySet_reactome.dbId;DatabaseObject_reactome.stId;PhysicalEntity_reactome.stId;Species_reactome.taxId;DatabaseObject_reactome.oldStId;Taxon_reactome.taxId;Reaction_reactome.stId;ReactionLikeEvent_reactome.stId;EntitySet_reactome.stId;PhysicalEntity_reactome.dbId;ReactionLikeEvent_reactome.dbId;ReferenceEntity_reactome.stId;Complex_reactome.stId;Pathway_reactome.dbId;Event_reactome.dbId;ReferenceEntity_reactome.dbId;Pathway_reactome.stId;Event_reactome.stId;GenomeEncodedEntity_reactome.stId;Reaction_reactome.dbId;GenomeEncodedEntity_reactome.dbId;Complex_reactome.dbId;LiteratureReference_reactome.pubMedIdentifier;Person_reactome.orcidId;ReferenceEntity_reactome.variantIdentifier;ReferenceIsoform_reactome.variantIdentifier;ReferenceEntity_reactome.identifier;ReferenceIsoform_reactome.identifier" > output/import_tool_output.txt

sleep 60

$path_neo4j/neo4j restart

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"