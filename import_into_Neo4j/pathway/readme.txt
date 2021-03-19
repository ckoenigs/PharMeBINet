https://www.pathwaycommons.org/
https://www.wikipathways.org/index.php/WikiPathways

Version: Pathway Commons Version 12 and WikiPathways ...

The program was based on https://github.com/dhimmel/pathways/blob/master/merge-resources.ipynb but was changed.
First, the Entrez Gene information is used from my integrated Entrez gene Infos because these are up-to-date. This gets only human gene ids and which are coding and a dictionary from symbol to gene id.
Then it downloads the Pathway Commons and prepares only the human data. Then it takes only information that has a license that can be used like WikiPathways, Reactome, Panther, and Netpath.
Next WikiPathways is downloaded and the data are prepared.
In the following step, the information of both databases is combined and written into a CSV file. Additionally, a cypher file is generated to integrate the data into Neo4j.
In the last step, the cypher-shell integrates the data with the use of the cypher file and the CSV file into Neo4j.

License: WikiPathway: CC BY 3.0
	Pathway Commons: License of the different sources
		
