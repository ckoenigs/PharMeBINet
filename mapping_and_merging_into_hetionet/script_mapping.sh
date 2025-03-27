#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

#password
password=$3

# path to external save position of data
path_to_other_place_of_data=$4

cd monDO
now=$(date +"%F %T")
echo "Current time: $now"
echo 'add monDO'

./integration_of_mondo_new.sh $path_neo4j $path_to_project $password > output_mapping_and_integration.txt


cd ..


cd do
now=$(date +"%F %T")
echo "Current time: $now"
echo do

./script_do.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..


cd efo
now=$(date +"%F %T")
echo "Current time: $now"
echo efo

./script_efo.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..


cd ncbi_gene
now=$(date +"%F %T")
echo "Current time: $now"
echo Ncbi genes

./script_ncbi_new.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..



cd uberon
now=$(date +"%F %T")
echo "Current time: $now"
echo Uberon

./script_uberon.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..



cd hetionet
now=$(date +"%F %T")
echo "Current time: $now"
echo Map hetionet

./mapping_hetionet_script.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..


cd hgnc
now=$(date +"%F %T")
echo "Current time: $now"
echo Hgnc

./script_to_integrate_hgnc.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..


cd omim

now=$(date +"%F %T")
echo "Current time: $now"
echo OMIM

./script_omim.sh $path_neo4j $path_to_project  $password> output_script.txt



cd ..

cd pathway
now=$(date +"%F %T")
echo "Current time: $now"
echo pathway

./script_pathway.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..


cd uniprot
now=$(date +"%F %T")
echo "Current time: $now"
echo 'integrat uniprot proteins'

./integration_protein.sh $path_neo4j $path_to_project $password > output_mapping_and_integration.txt 

cd ..


# cd RNAcentral
# now=$(date +"%F %T")
# echo "Current time: $now"
# echo RNACentral

# ./script_rnaCentral.sh $path_neo4j $path_to_project $password > output_script.txt


# cd ..


cd refseq

now=$(date +"%F %T")
echo "Current time: $now" 
echo refseq

./script_refseq.sh $path_neo4j $path_to_project  $password> output_script.txt



cd ..


cd miRBase

now=$(date +"%F %T")
echo "Current time: $now" 
echo miRBase

./script_mirbase.sh $path_neo4j $path_to_project  $password> output_script.txt



cd ..

cd go
now=$(date +"%F %T")
echo "Current time: $now"
echo GO

./go_integration.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..

cd CL
now=$(date +"%F %T")
echo "Current time: $now"
echo cl

./cl_integration.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..


cd hippie
now=$(date +"%F %T")
echo "Current time: $now"
echo 'Hippie'

./script_hippie_mapping_and_merging.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..


cd iid
now=$(date +"%F %T")
echo "Current time: $now"
echo 'IID'

./script_iid.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..

cd reactome
now=$(date +"%F %T")
echo "Current time: $now"
echo reactome

./script_reactome.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd hmdb
now=$(date +"%F %T")
echo "Current time: $now"
echo hmdb protein, go, metabolite

./script_hmdb_mapping_and_merging.sh $path_neo4j $path_to_project $password > output_script_part_1.txt

cd ..

cd smpdb
now=$(date +"%F %T")
echo "Current time: $now"
echo smpdb

./script_to_mapping_smpdb.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo Clinvar 
cd clinvar

./script_clinvar.sh $path_neo4j $path_to_project $password #> output_mapping_and_integration.txt 

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo drugbank

cd drugbank

./script_mapping_drugbank_new.sh $path_neo4j/ $path_to_project $password > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo mapping table rxcui drugbank

cd RxNorm_to_DrugBank 

./execute_mapping_rxcui_to_drugbank.sh > output.txt

cd ..



cd hetionet
now=$(date +"%F %T")
echo "Current time: $now"
echo Map hetionet

./mapping_hetionet_compound.sh $path_neo4j $path_to_project $password > output_script_compound.txt


cd ..


cd hpo

now=$(date +"%F %T")
echo "Current time: $now"

echo HPO

./script_hpo.sh $path_neo4j/ $path_to_project $password > output_script.txt


cd ..

cd hmdb
now=$(date +"%F %T")
echo "Current time: $now"
echo hmdb pathway, disease

./script_hmdb_mapping_and_merging_part2.sh $path_neo4j $path_to_project  $password> output_script_part_2.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo ctd

cd ctd 

./script_ctd_mapping_and_integration.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo TTD
cd ttd

./script_to_mapping_ttd.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..


cd chebi
now=$(date +"%F %T")
echo "Current time: $now"
echo ChEBI

./merge_chebi.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..


cd foodon
now=$(date +"%F %T")
echo "Current time: $now"
echo FoodOn

./script_foodon_merge.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..


cd fideo
now=$(date +"%F %T")
echo "Current time: $now"
echo FIDEO

./script_fideo_merge.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo bindingDB
cd bindingDB

./script_merge_bindingDB.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd med_rt/
now=$(date +"%F %T")
echo "Current time: $now"
echo med-rt


./script_med_rt.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..

cd ndf-rt/
now=$(date +"%F %T")
echo "Current time: $now"
echo ndf-rt


./script_ndf_rt.sh $path_neo4j/ $path_to_project $password > output_script.txt


cd ..


cd DDinter
now=$(date +"%F %T")
echo "Current time: $now"
echo DDinter

./script_execute_DDinter.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd reactome
now=$(date +"%F %T")
echo "Current time: $now"
echo reactome drug

./script_reactome_drug.sh $path_neo4j $path_to_project $password > output_script_drug.txt

cd ..


cd clinvar

now=$(date +"%F %T")
echo "Current time: $now"
echo clinvar drug response

./script_clinvar_drug_response.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..

cd atc
now=$(date +"%F %T")
echo "Current time: $now"
echo 'atc'

./script_atc.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..



now=$(date +"%F %T")
echo "Current time: $now"
echo drugbank Protein

cd drugbank

./script_map_drugbank_protein.sh $path_neo4j/ $path_to_project $password > output_script_protein.txt

cd ..

cd sider
now=$(date +"%F %T")
echo "Current time: $now"
echo Sider

./script_sider.sh $path_neo4j/ $path_to_project $password $path_to_other_place_of_data > output_script.txt

cd ..


cd RNAinter
now=$(date +"%F %T")
echo "Current time: $now"
echo RNAinter

./script_rnaInter.sh $path_neo4j $path_to_project $password> output_script.txt


cd ..

cd RNAdisease
now=$(date +"%F %T")
echo "Current time: $now"
echo RNAdisease

./script_RNAdisease_mapping.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..

cd disgenet
now=$(date +"%F %T")
echo "Current time: $now"
echo DisGeNet

./script_to_integrate_disgenet.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo Aeolus  

cd aeolus

./script_aeolus.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo ADReCS  

cd adrecs

./script_to_integrate_ADReCS.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

#now=$(date +"%F %T")
#echo "Current time: $now"
#echo ADReCS-Target  

#cd adrecs_target

#./script_to_integrate_ADReCS_Target.sh $path_neo4j $path_to_project $password > output_script.txt

#cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo PharmGKB
cd pharmGKB

./script_pharmgkb.sh $path_neo4j/ $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo DrugCentral
cd drugcentral

./script_to_map_and_integrate_drug_central_information.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo bioGrid
cd bioGrid

./script_to_integrate_biogrid.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo gencc 
cd gencc

./script_gencc_mapping_and_merging.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

# now=$(date +"%F %T")
# echo "Current time: $now"
# echo openFDA
# cd openFDA

#./script_map_openFDA.sh $path_neo4j $path_to_project $password > output_script.txt

# cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo map symptoms to side effects
cd connect_equal_edges/

./script_phenotyp_mapping.sh $path_neo4j/ $path_to_project $password $path_to_other_place_of_data > output_script.txt


cd ..

cd markerdb
now=$(date +"%F %T")
echo "Current time: $now"
echo markerdb


./script_markerdb_mapping_and_integration.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd diseases
now=$(date +"%F %T")
echo "Current time: $now"
echo diseases


./script_DISEASES.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd PTMD
now=$(date +"%F %T")
echo "Current time: $now"
echo PTMD


./script_ptmd_mapping_and_integration.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd iPTMnet
now=$(date +"%F %T")
echo "Current time: $now"
echo iPTMnet


./script_iPTMnet_mapping_and_integration.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

cd qptm
now=$(date +"%F %T")
echo "Current time: $now"
echo qptm


./script_qptm_mapping_and_integration.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo gwas 
cd gwas

./script_gwas_mapping_and_merging.sh $path_neo4j $path_to_project $password > output_script.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo dbSNP
cd dbSNP

./script_to_get_dbSNPs_information.sh $path_neo4j $path_to_project $password $path_to_other_place_of_data > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
echo PharmGKB edges
cd pharmGKB

./script_pharmgkb_edges.sh $path_neo4j/ $path_to_project $password > output_script_edges.txt

cd ..


