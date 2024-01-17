#!/bin/bash

for filename in ./*.zip; do
    echo $filename
    delimiter="."
    declare -a array=($(echo $filename | tr "$delimiter" " "))
    echo ${array}
    mkdir .${array[0]}.fasta
    unzip $filename -d .${array[0]}.fasta
done