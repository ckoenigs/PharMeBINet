http://ddinter.scbdd.com/

Version: 2020-05-13

The script of DDinter first prepare a drug mapping

The python program try to map the DDinter drug to Chemical with name mapping. All mapping pairs are written into a TSV file and additonally a cypher file with cypher queries to integrate the mapping into Neo4j.

The mappings are integrated with cypher shell.



Description of level of interaction (http://ddinter.scbdd.com/explanation/)[http://ddinter.scbdd.com/explanation/]:
    Major: The interactions are life-threatening and/or require medical treatment or intervention to minimize or prevent severe adverse effects.
    Moderate: The interactions may result in exacerbation of the disease of the patient and/or change in therapy.
    Minor: The interactions would limit the clinical effects. The manifestations may include an increase in frequency or severity of adverse effects, but usually they do not require changes in therapy.
    Unknown: The DDIs collected from the article published in Sci Transl Med were lack of mechanism descriptions, and thus the severity classifications of these DDIs were annotated with 'Unknown'.


License: Creative Commons Attribution-NonCommercial-ShareAlike 4.0