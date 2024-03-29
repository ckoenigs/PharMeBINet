# DrugBank to Neo4j
This integrates all open-source data of DrugBank into Neo4j.

Version: 5.1.11 (2024-01-03)

The first step of the DrugBank integration script is to get all DrugBank categories from the API.
The next step is to prepare the SDF files into CSV files.
Then the DrugBank XML file is formed into a tsv file orientated by https://github.com/dhimmel/drugbank/blob/gh-pages/parse.ipynb
with a lot of changes. It takes all information from the file and generates CSV files for targets, carriers, transporter, enzymes, SNPs, pathways, salts, products, metabolites, and pharmacological classes.
Also, the relationships between the different node types are added to CSV files.
After extracting the information from the XML file the information must be combined with the information from the other DrugBank files. Also, the targets are validated with the UniProt identifier (https://github.com/ckoenigs/UniProt_to_Neo4j). The program needs information on where the other DrugBank files are. Also, the generated CSV files from the other program are in a dictionary DrugBank.
In this step are also the cypher queries generated to integrate the different nodes and relationships into Noe4j.
In the last step, the information is integrated into Neo4j with Neo4j cypher-shell.

This should have the form:

![er_diagram](picture/drugbank_er_new.png)

The Compound has so many properties:

![er_diagram](picture/drugbank_compound.png)

The Relationships have also some properties:

![er_diagram](picture/drugbank_er_rela.png)

License: Creative Common's Attribution-NonCommercial 4.0 International License.
