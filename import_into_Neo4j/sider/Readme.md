http://sideeffects.embl.de/

Version: SIDER 4.1

meddra_all_se.tsv: [STITCH compund IDs (flat/stereo); UMLS concept ID (on lable); MedDRA concept type; UMLS concept id (MedDRA term); Side effect name]
With stitch stereo and flat the drug is generated. The rest is for side effects. All node information is added to dictionaries.
With stitch stereo and UMLS MedDRA id is the relationship generated.

meddra_freq.tsv: [STITCH compund IDs (flat/stereo); UMLS concept ID (on lable); placebo; frequency description; lower/upper bound on frequency ; MedDRA concept type; UMLS concept id (MedDRA term); Side effect name ]
Add drug nodes like before but only if not already in the dictionary. If no MedDRA UMLS id is there it takes the UMLS id label. Like before the side effect nodes are only added if they are not already in the dictionary.
The information placebo frequency, lower frequency, and upper frequency is added to the relationships or generates new edges.

meddra_all_lable_indications.tsv: [source labelindication; STITCH compund IDs (flat); STITCH compund IDs (stereo) ; UMLS concept ID (on lable); method of detection: NLP_indication / NLP_precondition / text_mention; concept name; MedDRA concept type; UMLS concept id (MedDRA term); MedDRA concept name ]
It is like before drug nodes that are not already added are add and the same goes for side effect nodes.
The relationships get additional information method Detection or generate a new edge with this information.

meddra_all_indications.tsv: [STITCH compund IDs (flat); UMLS concept ID (on lable); method of detection: NLP_indication / NLP_precondition / text_mention; concept name; MedDRA concept type; UMLS concept id (MedDRA term); MedDRA concept name]
Here we have only the flat id and I use normally the stereo id because this is specific and the flat id the merged ids. That is why from the other file a dictionary from flat id to the stereo ids was generated.
As for the other files, the side effect nodes are only added if they are not already in the dictionary.
Add relationships between the flat -> stereo ids and the UMLS id if they are not already existing.

Next, the cypher queries are generated to integrate the nodes and the relationships with their information into Neo4j. They are written into a cypher file.
In following the tsv file for the nodes and relationships are generated.
However, for the frequency information are so kind of preparation done. Frequencies with from ... to ... take the average. If for one pair exist multiple frequencies exists it tries to take the average.
The same is done for the placebo frequencies.

In the last step, the data are integrated into Neo4j with cypher-shell and the cypher file.
 
License:  Creative Commons Attribution-Noncommercial-Share Alike 4.0 License

Theoretically it automatically updaed when data is removed.