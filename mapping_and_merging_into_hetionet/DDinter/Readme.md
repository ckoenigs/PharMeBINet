The script of DDinter first prepares a drug mapping

The Python program tries to map the DDinter drug to a Chemical with name mapping. Second, with synonyms to name/synonym of chemicals. All mapping pairs are written into a TSV file and additionally, a cypher file with cypher queries to integrate the mapping into Neo4j.

The mappings are integrated with cypher shell.



Description of level of interaction (http://ddinter.scbdd.com/explanation/)[http://ddinter.scbdd.com/explanation/]:
    Major: The interactions are life-threatening and/or require medical treatment or intervention to minimize or prevent severe adverse effects.
    Moderate: The interactions may result in exacerbation of the disease of the patient and/or change in therapy.
    Minor: The interactions would limit the clinical effects. The manifestations may include an increase in the frequency or severity of adverse effects, but usually, they do not require changes in therapy.
    Unknown: The DDIs collected from the article published in Sci Transl Med were lack of mechanism descriptions, and thus the severity classifications of these DDIs were annotated with 'Unknown'.


The program merges the drug-drug interaction of DDinter into PharMeBINet:
    First, load all existing pairs.
    Then, generate TSV files for mapped edges and new edges. Additionally, a cypher file is generated with the additional cypher queries.
    Next,  all DDinter pairs are loaded and checked if they exist already or not and write the information into the different TSV files.

The last step is the execution of the cypher file with the use of the Neo4j cypher-shell.