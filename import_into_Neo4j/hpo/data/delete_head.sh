#!/bin/bash
file_line=$( grep  -n 'database_id' $1 | grep -Eo '^[^:]+')
# header is the line 
echo $file_line
#tail -n +28 $1 > text.tsv
tail -n +$(($file_line)) $1 > text.tsv

#replace # with nothing
sed -i 's/^#//' text.tsv

head -1 text.tsv

head -n +$(($file_line-1)) $1 > version_phenotype.txt

cp text.tsv $1