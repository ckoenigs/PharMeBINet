#!/bin/bash

for filename in ./*.zip; do
    echo $filename
    delimiter="_"
    declare -a array=($(echo $filename | tr "$delimiter" " "))
    echo ${array[2]}
    unzip $filename 

    if [[ 'drug' == ${array[2]} ]]; then
        echo 'uhuhu'
    else
        echo uniprot_links_${array[2]}.csv
        mv 'uniprot links.csv' uniprot_links_${array[2]}.csv
    fi
done