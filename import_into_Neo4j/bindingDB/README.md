## BindingDB

https://www.bindingdb.org/rwd/bind/index.jsp

Version: 2025-08-21


Important steps for importing BindingDB into MySQL:
mysql -u ckoenigs -p bindingDB < BDB-mySQL_All_202508.dmp

The import into Neo4j is separated into multiple steps.
First, load all tables that are considered into TSV files in batches. Only polymer, monomer, and complex are a bit complex because the Tsv is a combination of multiple tables. Polymer, monomer, and complex are combined with their name tables.

The second program prepares the edge files and the cypher queries.
    First, the TSV is prepared for the tables which are connected through direct property names and now information in the edge.

prepare_queries.py: creates cypher queries


License: CC BY 3.0 US Deed

This need manual updating. First the, dump need to be downloaded and integrated int mysql, then in the script the url need to be changed to the latest version and in merge_and_save the zip name need to be changed too.