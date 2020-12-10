#!/bin/bash

#search for the first line without  #
file_content_line=$( grep -nm1 '^[^#]' $1 | grep -Eo '^[^:]+')
# header is the line before
file_header=$(($file_content_line-1))
echo $file_header
echo $file_content_line

# take the line with the header
sed "${file_header}q;d" $1 > test.tsv
#add all other lines without a #
grep '^[^#]' $1 >> test.tsv

#removed second line
#sed -i '2d' text.tsv
sed -i 's/# //' test.tsv

test="_license_definition"
rest="$1$test"
echo $rest

grep '^[#]' $1 > $rest

cp test.tsv $1
