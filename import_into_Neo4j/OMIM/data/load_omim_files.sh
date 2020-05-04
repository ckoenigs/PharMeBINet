#!/bin/bash

source key_omim.sh

echo $OMIM_KEY


#download omim files
wget  -O mim2gene.txt "https://omim.org/static/omim/data/mim2gene.txt"

wget  -O mim2gene.txt "https://data.omim.org/downloads/"+$OMIM_KEY+"/mimTitles.txt"

wget  -O mim2gene.txt "https://data.omim.org/downloads/"+$OMIM_KEY+"/genemap2.txt"

wget  -O mim2gene.txt "https://data.omim.org/downloads/"+$OMIM_KEY+"/morbidmap.txt"
