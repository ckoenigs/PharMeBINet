# openFDA

https://open.fda.gov/

Version: 

First for all directories of openFDA the right path is prepared.
Next, the file with all links to the openFDA files is downloaded. 
Then the directories for the different data files are generated and downloaded. (CAERSReports, DrugAdverseEvents, DrugRecallEnforcementReports, FoodRecallEnforcementReports, NationalDrugCodeDirectory, SubstanceData)
The for each directory the folowing steps were executed:
    First, unzip the file(s).
    Next, the files are read and parsed into tsv files.
    Then, tsv headers and path are saved and in the last step the cypher queries are prepared.

Then the script executes the cypher file with Neo4j cypher-shell.

License:CC0 1.0 Universal