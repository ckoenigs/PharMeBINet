The idea is from https://think-lab.github.io/d/40/ but it is only the basic idea.

Version: UNII:  2023-09-22 
        RxNorm: 2023-11 

The preparation of mapping table with RxNorm and UNII from mapping between RxNorm Cui to DrugBank.
First, download the latest version of UNII from FDA-SRS database (https://precision.fda.gov/uniisearch/archive/latest/UNII_Data.zip) and unzip it.
Then generate the UNII-DrugBank-InChIKey table.
               Load all DrugBank identifier with UNII and InChIKey entries and wrote into a TSV file.
Next, load all RxNorm-UNII connections.
               With the use of RxNorm, the TSV with information between RxCui and UNII is generated.
Then, another RxNorm-UNII table is generated.
               The next pairs are extracted from the UNII data and written into another TSV file.
In the following, the information from the generated tables is combined.
First, all RxCui-UNII tables are loaded into a dictionary. 
Next, it extracts the UNII-InChIKey information from UNII data into a dictionary.
Finally, generate a combined TSV with RxCui-UNII-InChIKey
The following program generates a mapping table between DrugBank id and RxCui.
               First, the information from the last tables is loaded into dictionaries.
               Then, the table with the DrugBank-UNII-InChIKey is loaded and mapped with UNII and InChIKey to the RxCui. The mapping pair is written into a dictionary.
               In the last step, all RxCuis with the DrugBank ids are written into a new TSV file.







