#!/bin/bash

counter_of_connection_tries=0
worked_url=false
now=$(date +"%F %T")
echo "Current time: $now"
echo down load fda file
#$counter_of_connection_tries -lt 11 && 
while  ! $worked_url && (("$counter_of_connection_tries" < "11")) ; do
    wget -O ./UNII_Data.zip "https://fdasis.nlm.nih.gov/srs/download/srs/UNII_Data.zip" 
    worked_url=true
    counter_of_connection_tries=$((counter_of_connection_tries+1))
    echo $counter_of_connection_tries
done
if (("$counter_of_connection_tries" >= "11"))
    then
        echo could not download the file
        exit 1;
fi
unzip UNII_Data.zip -d unii/
cd unii
mv UNII* unii_data.txt
cd ..


now=$(date +"%F %T")
echo "Current time: $now"
echo load drugbank information 
python3 generate_unii_drugbank_table_with_drugbank.py > output_drugbank_info.txt


now=$(date +"%F %T")
echo "Current time: $now"

echo rxnorm cui to dugbank id with use of inchikey and unii

echo first rxnorm to unii
python3 map_rxnorm_to_unii_final.py > output_map_rxnorm_to_unii.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo second unii to rxnorm
python3 unii_to_rxnorm_cui_final.py > output_unii_to_rxnorm_cui.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo third combine both information and add the unii inchikeys 
python3 combine_rxnorm_and_fda_srs_to_a_rxnorm_unii_inchkey_file.py > output_combine.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo fourth map rxnorm to drugbank with unii and inchikey

python3 map_rxcui_to_drugbank_with_unii_inchikey_final.py >  output_map_rxcui_to_drugbank_with_unii_inchikey.txt

now=$(date +"%F %T")
echo "Current time: $now"

echo map drugbank to rxnorm with names
#take a lot of time
python3 map_drugbank_to_rxnorm_with_name_final.py >  output_map_drugbank_to_rxnorm_with_name.txt


now=$(date +"%F %T")
echo "Current time: $now"

rm unii/*
