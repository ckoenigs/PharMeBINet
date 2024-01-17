## BindingDB

https://www.bindingdb.org/rwd/bind/index.jsp

Version: 2023-12-31


Important steps for importing BindingDB into MySQL:
mysql -u ckoenigs -p bindingDB < BDB-mySQL_All_202301.dmp
Create Index mono_in_struct ON bindingDB.monomer_struct (monomerid);

The import into Neo4j is separated into multiple steps.
First, load all tables that are considered into TSV files in batches. Only polymer, monomer, and complex are a bit complex because the Tsv is a combination of multiple tables. Polymer and complex are combined with their name tables. The monomer is combined with the monomer-name and monomer-structure.

The second program prepares the edge files and the cypher queries.
    First, the TSV is prepared for the tables which are connected through direct property names and now information in the edge.

prepare_queries.py: creates cypher queries


License: CC BY 3.0 US Deed