#!/bin/bash
file_line=$( grep -n '# Fields:' $1 | grep -Eo '^[^:]+')
echo $file_line
echo $(($file_line+1))
#tail -n +28 $1 > text.tsv
tail -n +$(($file_line+1)) $1 > text.tsv

# delete 2 line
sed -i '2d' text.tsv
#replace # wit nothing
sed -i 's/# //' text.tsv

head -2 text.tsv

cp text.tsv $1
