https://evs.nci.nih.gov/ftp1/MED-RT/

Version: 2025-07-07

The XML is parsed in multiple TSV files for nodes and relationships. Additionally, the cypher files are generated to integrated the information into Neo4j.
MED-RT has not only information from their database but also contains data from MESH and RXNORM that at are not in the XML file. Therefore, the files from Core MEDRT Accessory files are used. However, only the files without DTS in the file name.
Because these files have the same information as the other files but after the name also the identifier.

Like in here:

License: UMLS license, available at https://uts.nlm.nih.gov/license.html