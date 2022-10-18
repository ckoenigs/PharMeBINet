https://rnacentral.org/

Version: RNAcentral relase 20

The files from JSON, id_mapping, and genome_coordinates (bed) are used to get RNAcentral information.
First, the human genome_coordinates bed file is transformed into a TSV file.
Next, the JSON files are downloaded. Therefore, first, all file names are extracted from the web page. Then each file is downloaded and transformed into a pandas dataframe. Then the frame is filtered of human data and written into TSV files.
Next, the information from the bed file and the JSON files are merged based on the RNAcentral ID.
Then the id_mapping data are run through. Therefore only the human rows are considered and all information is written into a dictionary.
In the next step, the merged information of JSON and bed are combined with the id_mapping. Then the information are separated into RNA nodes with information: 'rnacentral_id', 'score', 'itemRgb', 'type', 'databases', 'description', 'sequence', 'md5','geneName', 'xrefs'
RNA subnodes:'id','chromName','chromStart','chromEnd', 'strand', 'thickStart','thickEnd', 'blockCount', 'blockSizes','blockStarts'
and edge TSV file which connects RNA nodes with RNA subnodes. In the last step, the cpher file with the cypher queries is generated.

Then the script executes the Neo4j cypher-shell to execute the cypher file to integrate the RNAcentral information.

The schema is shown here:


License: Creative Commons Zero license (CC0)