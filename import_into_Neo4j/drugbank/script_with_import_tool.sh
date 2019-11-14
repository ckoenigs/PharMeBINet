#!/bin/bash

now=$(date +"%F %T")
echo "Current time: $now"
echo program

python file_preperation.py "/media/cassandra/Seagate Backup Plus Drive/Promotion/All_databases/Drugbank_database/drugbank_files_without_preperation/" drug_sequences/ external_links/ Protein_identifiers/ structure/ target_sequences/

now=$(date +"%F %T")
echo "Current time: $now"
echo integration

./script_import_tool.sh
