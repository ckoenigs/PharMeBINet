# DDinter Parser

http://ddinter.scbdd.com/

Version: DDinter 1.0 

The script first prepares the DDinter:
    First, the edge TSV file and cypher file are generated.
    Then, for the different DDinter CSV files are loaded from DDinter. The edge information is written into the TSV file. The drug information is gathered in a dictionary.
    Next, the TSV file for the drugs is generated. Additionally, the cypher nor durg and edge integration are generated and added to the cypher file.

Next, with the use of Neo4j cypher and the cypher shell the drug and edge information is integrated.


License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license