http://stitch.embl.de/cgi/download.pl?UserId=G6pkqvOYhcVR&sessionId=PKTbgaQf0RMR
License: Attribution 4.0 International (CC BY 4.0)
https://www.biostars.org/p/155342/

The SIDER script prepares the mapping and the integration of SE-drug relationships.
First, the SIDER SEs are mapped, and add new nodes to the database.
               First, the TSV files for the new nodes are generated.
               Next, the SIDER SE information is prepared and written into the new node TSV file.
               In the last step, the cypher file and cypher query are generated.

Second, the SIDER drugs are mapped to chemicals.
               First, load all chemical information and write them into dictionaries.
               Next, load all SIDER drug information into dictionaries.
               Then, a part STITCH chemical is generated if not existing for only the PubChem stereo/flat IDs from SIDER drugs. From STITCH chemical dictionaries from PubChem ID to name are generated.
               The first mapping is based on the PubChem stereo ID to chemical external references. Then with the PubChem flat id to the external reference from chemical.
               Then a part STITCH chemicals.inchikey is generated if not existing for only the PubChem stereo from SIDER drugs which did not map before. From STITCH chemicals.inchikey the fitting InChIKey for the PubChem stereo id is used for mapping to chemicals InChIKey.
               Next, a part of STITCH chemicals.sources is generated if not existing for only the PubChem stereo/flat IDs from SIDER drugs that have source DrugBank or ChEMBL. From STITCH chemicals.source the fitting DrugBank ID for the PubChem stereo/flat ID is used for mapping to chemicals DrugBank ID. However, for the flat, only the ones are excepted where the flat and the stereo are equal or the flat name is equal to the chemical name. The same is being done with the ChEMBL to the chemical external references.
               The next mapping method is based on the stereo name of STITCH for the drug to the chemical name or chemical synonyms, mixture name, and brand names.
               Last, generate the cypher query to integrate the mapping information into the database. Also, the mapping TSV is generated and all mapped pairs are written into this file.

               [
                1. Map stereo ID to Drugbank with the use of STITCH
                2. Map flat id (has same stereo ID) to Drugbank with the use of STITCH
                3. Map flat id to Drugbank with the use of STITCH 
                4. Map sider InChIKey to Drugbank InChIKey. Sider InChIKey is from STITCH 
                5. map sider InChIKey to Drugbank alternative InChIKey. Sider InChIKey is from STITCH 
                6. Map SIDER name to DrugBank name, synonym, brands, and Product Ingredients name
                ]

               
               
Then, the mapping information and the new nodes are integrated into the database with the cypher-shell.

In the last program, the drug-SE edges are prepared for integration.
            First, all pairs are loaded from the sider and the information is written into a dictionary.
            Then, the cypher file and the cypher query for integrating new edges are generated.
            Next, the TSV files are generated for the new edges.
            In the following, for all pairs, the lowest frequency is computed. Then go through all frequencies try to get a value and compute the average else take a word. Next, the upper frequency is computed. The same is done for the placebo frequencies. The pairs are written into the TSV file.

Finally, the cypher-shell integrates the edge information into the database.

