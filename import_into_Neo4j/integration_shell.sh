#!/bin/bash

#define path to neo4j bin
path_neo4j=$1

#path to project
path_to_project=$2

# import tool
name_of_import_tool=$3

# password neo4j
password=$4

# path to external save position of data
path_to_other_place_of_data=$5

name_of_biodwh2_tool='BioDWH2-v0.6.7'

echo $name_of_import_tool


now=$(date +"%F %T")
echo "Current time: $now"

cd sider 
echo sider

./script_sider.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd bioGrid 
echo bioGrid

./script_biogrid.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd atc
echo atc

./script_atc.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd gwas
echo gwas

./integrate_gwas.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > output/script_output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd diseases
echo DISEASES

./integrate_DISEASES.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd gencc
echo gencc

./integrate_gencc.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt


cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd smpdb 
echo smpdb

./script_integrat_smpdb.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd DDinter 
echo DDinter

./script_integrated_ddinter.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd foodb 
echo Foodb

./script_foodb.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd hmdb 
echo HMDB

./script_integrate_hmdb.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd hippie 
echo HIPPIE

./script_hippie_integration.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  ndf_rt
echo ndf-rt

./script_import_ndf_rt.sh $path_neo4j $path_to_project $password > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  DisGeNET
echo disgenet

./script_integrated_disgenet.sh $path_neo4j $path_to_project $password > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"
cd  med_rt
echo med-rt

./script_med_rt_integration.sh $path_neo4j $path_to_project $password > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  do
echo do

./script_import_do.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  foodon
echo FoodOn

./script_import_foodon.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  FIDEO
echo FIDEO

./script_import_fideo.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  CO
echo co

./script_import_co.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  chebi_ontology
echo chebi_ontology

./script_import_chebi.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  Uberon
echo Uberon


./script_uberon.sh  $path_neo4j $path_to_project $password > output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  GO
echo go

./script_to_integrate_go.sh $path_neo4j $path_to_project $password > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"


cd  hpo
echo hpo

./hpo_integration.sh $path_neo4j $path_to_project $password > output_hpo.txt

cd ..


#now=$(date +"%F %T")
#echo "Current time: $now"


#cd  openFDA
#echo openFDA

#./script_open_fda.sh $path_neo4j $password $path_to_other_place_of_data > output_openFDA.txt

#cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd aeolus
echo aeolus

./script_aeolus.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..

#now=$(date +"%F %T")
#echo "Current time: $now"

#cd RNAcentral
#echo RNACentral

#./script_rna_central.sh $path_neo4j $path_to_project $password $path_to_other_place_of_data > output_script.txt


#cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  RNAdisease
echo RNAdisease

now=$(date +"%F %T")
echo "Current time: $now"

./script_rnadisease.sh $path_neo4j $path_to_project $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd uniProt
echo UniProt

./script_uniprot.sh $path_neo4j $path_to_project $password > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  drugbank
echo drugbank

./script_to_start_program_and_integrate_into_neo4j.sh $path_neo4j $path_to_project $password $path_to_other_place_of_data > output_script.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  EFO
echo EFO


./script_efo.sh $path_neo4j $path_to_project $password > output.txt

cd ..

# now=$(date +"%F %T")
# echo "Current time: $now"


# cd  adrecs_target
# echo adrecs-target

# ./script_adrecs_target.sh $path_neo4j $path_to_project $password > output_script.txt

# cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  ncbi_genes
echo NCBI

./script_ncbi_gene.sh $path_neo4j $path_to_project $password > output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  IID
echo IID

./script_iid.sh $path_neo4j $path_to_project $password > output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  rnainter
echo RNAinter

./script_integrate_rna_inter.sh $path_neo4j $path_to_project $password > output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  PharmGKB
echo PharmGKB

./script_pharmGKB.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  drugcentral
echo drugcentral

./integrate_drugcentral.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password $path_to_other_place_of_data > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  adrecs
echo ADReCS

./integrate_adrecs.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  ttd
echo TTD

./integrate_ttd.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  PTMD
echo PTMD

./integrate_ptmd.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  iPTMnet
echo iPTMnet

./integrate_iptmnet.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  qptm
echo qptm

./integrate_qptm.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  miRBase
echo miRBase

./integrate_mirbase.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  hgnc
echo HGNC

./integrate_hgnc.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  markerdb
echo markerdb

./integrate_markerdb.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  refseq
echo refseq

./integrate_refseq.sh $path_neo4j $name_of_import_tool $name_of_biodwh2_tool $password $path_to_other_place_of_data > script_output.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  pathway
echo pathway

./script_pathway.sh $path_neo4j $path_to_project $password > output.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  Hetionet
echo hetionet

./script_import_hetionet_with_graphml.sh $path_neo4j $name_of_import_tool $password $path_to_project > output_hetionet.txt

cd ..


now=$(date +"%F %T")
echo "Current time: $now"


cd  reactome
echo reactome

./script_import_recatome_with_graphml.sh $path_neo4j $name_of_import_tool $password $path_to_other_place_of_data > output_reactome.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd bindingDB 
echo bindingDB

./script_bindingdb.sh $path_neo4j $path_to_project $password > output.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  mondo
echo mondo


./new_mondo.sh $path_neo4j $path_to_project $password > output_integration_of_everything.txt


cd ..


now=$(date +"%F %T")
echo "Current time: $now"

cd  OMIM
echo omim


./script_to_execute_omim.sh $path_to_project $path_neo4j $password > output_integration_of_everything.txt


cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd  ClinVar
echo ClinVar

./script_clinvar.sh $path_neo4j $path_to_project $path_to_other_place_of_data $password > output_script.txt

cd ..

now=$(date +"%F %T")
echo "Current time: $now"

cd ctd
echo ctd

./script_ctd.sh $path_to_other_place_of_data $path_neo4j $password > output.txt


cd ..

