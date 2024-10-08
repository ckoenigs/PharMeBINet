#ClinVar Parser
https://www.ncbi.nlm.nih.gov/clinvar/

Version: 2024-01-19

The data are parsed to TSV and are integrated into Neo4j with cypher queries.

Go through 2 XML files:
https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/clinvar_variation/ClinVarVariationRelease_00-latest.xml.gz
Each entry is a Variation but it separated genotype, haplotype, and other variation and the links between each other. I use this too because not all variants are in full release! All the nodes are written into tsv file direct!

https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/ClinVarFullRelease_00-latest.xml.gz
This content the node information for variants and relationship between genotype, haplotype, and other variant and also the trait sets snd traits which are grouped the trait type.
Each entry in the XML is a relationship between a genotype, haplotype, and other variants and the different trait sets. All information is written into tsv files for the trait nodes and edges!

After all, files are run through the cypher files are prepared for each node and all different kinds of relationships!

The schema is shown here:

![er_diagram](clinvar.png)

License:https://www.ncbi.nlm.nih.gov/home/about/policies/

Download the latest version automatically.