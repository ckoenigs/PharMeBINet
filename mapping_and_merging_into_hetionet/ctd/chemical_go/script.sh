#!/bin/bash

now=$(date +"%F %T")
echo "Current time: $now"
echo python chemical gene
#cd ..
#cd chemical_gene/

#now=$(date +"%F %T")
#echo "Current time: $now"
#echo integration of chemical-gene
#../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher.cypher > output_cypher_26_10.txt

#now=$(date +"%F %T")
#echo "Current time: $now"
#../../../../../neo4j-community-3.2.9/bin/neo4j restart

#cd ..
now=$(date +"%F %T")
echo "Current time: $now"
echo python chemical go

#python integration_chemical_go.py > chemical_go/output_05_10.txt

#cd chemical_go

now=$(date +"%F %T")
echo "Current time: $now"
echo integration of chemical-go
echo integration bp
../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher_bp.cypher > output_cypher_bp_09_11.txt

now=$(date +"%F %T")
echo "Current time: $now"
../../../../../neo4j-community-3.2.9/bin/neo4j restart

sleep 180
# cp -r ../../../../../neo4j-community-3.2.9/data/databases/graph_09_11_18_EFO_HPO_switch_pathway_ids_integrated_mondo_march_CTD_cmf_cg_dg_cp_cd_gpw_ggo_dp_dgo_GO_pathways_disease_chemical_update_gene_and_updated_drugbank_do_rest_update.db ../../../../../neo4j-community-3.2.9/data/databases/graph_09_11_18_EFO_HPO_switch_pathway_ids_integrated_mondo_march_CTD_cbp_cmf_cg_dg_cp_cd_gpw_ggo_dp_dgo_GO_pathways_disease_chemical_update_gene_and_updated_drugbank_do_rest_update.db

sleep 120

now=$(date +"%F %T")
echo "Current time: $now"
echo integration mf
#../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher_mf.cypher > output_cypher_bp_26_10.txt

now=$(date +"%F %T")
echo "Current time: $now"
#../../../../../neo4j-community-3.2.9/bin/neo4j restart

now=$(date +"%F %T")
echo "Current time: $now"
echo integration cc
#../../../../../neo4j-community-3.2.9/bin/neo4j-shell -file cypher_cc.cypher > output_cypher_bp_09_11.txt

now=$(date +"%F %T")
echo "Current time: $now"
#../../../../../neo4j-community-3.2.9/bin/neo4j restart

now=$(date +"%F %T")
echo "Current time: $now"
sudo shutdown -h 60


