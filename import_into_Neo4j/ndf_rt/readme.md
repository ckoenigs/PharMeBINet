The program induce_and_contraindication_final.py: This integrated only the disease and drugs which are in a contraindicates or induces relationship. 

The database can be downloaded by https://evs.nci.nih.gov/ftp1/NDF-RT/. I used the version from 2017.06.05

The program prepare_ndf_rt_to_neo4j_integration.py extract all information out of ndf-rt and the integrated data of ndf-rt will look like this:

![er_diagram](https://github.com/ckoenigs/master_database_change/blob/master/import_into_Neo4j/ndf_rt/ndf-rt.png)

This program is for ndf-rt 05.02.2018.

