http://www.rnadisease.org/

Version: RNAdisease v4.0

First, the TSV file of RNAdisease is downloaded if it is not already downloaded. Then it is opened with a pandas dataframe and all not human data are removed. Next, the information is separated into RNA (Symbol and type), disease (name, doid, mesh id, Kegg id), and edge information (RNA symbol, disease name, "RDID","PMID","score"). Then the TSV files are generated for RNA, disease, and edge, and additionally the cypher file with the fitting cypher queries is generated.

Then the script executes the Neo4j cypher-shell to execute the cypher file to integrate the RNAdisease information.


License:  Provide data for non-commercial use, distribution, or reproduction in any medium, only if you properly cite the original work.