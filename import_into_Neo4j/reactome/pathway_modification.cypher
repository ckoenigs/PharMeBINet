//Insertion of figures in Pathway as a list of properties (only url)
// set new list
MATCH (a:DatabaseObject_reactome)-[:figure]-(b:Figure_reactome)
SET a.figure_urls=[];

// fill list
MATCH p=(a:DatabaseObject_reactome)-[:figure]-(b:Figure_reactome) 
SET a.figure_urls = a.figure_urls +  ["https://reactome.org" + b.url];

// Insertion of URLs in Pathway as a list of properties (only uniformRsourceLocator)
//  set new list
MATCH (a:DatabaseObject_reactome)-[:literatureReference]-(b:URL_reactome)
SET a.publication_urls=[];

// fill list
MATCH p=(a:DatabaseObject_reactome)-[:literatureReference]-(b:URL_reactome) 
SET a. publication_urls = a.publication_urls + b.uniformResourceLocator;

// Insertion of LiteratureReference in Pathway as a list of properties (only pubMedIdentifier)
// NOTE!!! 3 publications had no pudMedIdentifier (3 of ~600)
// set new list
MATCH (a:DatabaseObject_reactome)-[:literatureReference]-(b:LiteratureReference_reactome) set a.pubMed_ids=[];

// fill list
MATCH p=(a:DatabaseObject_reactome)-[:literatureReference]-(b:LiteratureReference_reactome) 
SET a.pubMed_ids = a.pubMed_ids + toString(b.pubMedIdentifier);

// Insertion of Book in Pathway as a list of properties (only ISBN and title)
// set new list
MATCH (a:DatabaseObject_reactome)-[:literatureReference]-(b:Book_reactome) set a.books=[];

//fill list
MATCH p=(a:DatabaseObject_reactome)-[:literatureReference]-(b:Book_reactome) 
SET a.books = a.books + ("ISBN:" + b.ISBN + "; Title:" + b.title);


//set new list of pubMedIds
MATCH (a:Regulation_reactome)-[]-(b:RegulationReference_reactome) Where a.pubMed_ids is NULL set a.pubMed_ids=[];
 
//fill list
MATCH p=(a:Regulation_reactome)-[]-(b:RegulationReference_reactome)
SET a.pubMed_ids = a.pubMed_ids +b.pubMed_ids;
 
//Add RegulationReferences to ReactionLikeEvent_reactome
MATCH p=(a:RegulationReference_reactome)-[:regulationReference]-(b:ReactionLikeEvent_reactome)
WITH a.pubMed_ids as listA, b.pubMed_ids as listB, b
WITH [n IN listA WHERE NOT n IN listB] as listC, b
SET b.pubMed_ids = b.pubMed_ids + listC
