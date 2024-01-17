#!/bin/bash

for filename in ./*.zip; do
    echo $filename
    delimiter="_"
    declare -a array=($(echo $filename | tr "$delimiter" " "))
    echo ${array[1]}
    unzip $filename 
    mv 'drug sequences.fasta' ${array[1]}.fasta
done