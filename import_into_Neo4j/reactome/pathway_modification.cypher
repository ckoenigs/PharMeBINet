MATCH (:Pathway_reactome)-[r]-(s:Species_reactome)
WHERE s.taxId <> "9606" delete r;

//Delete all nodes that now miss relationship to Species
MATCH (n:Pathway_reactome) 
WHERE NOT (n)-[]->(:Species_reactome) 
detach delete n;

//Insertion of figures in Pathway as a list of properties (only url)
// set new list
MATCH (a:Pathway_reactome) 
SET a.figure_urls=[];

// fill list
MATCH p=(a:Pathway_reactome)-[:figure]-(b:Figure_reactome) 
SET a.figure_urls = a.figure_urls + b.url;

// delete Figure
MATCH (n:Figure_reactome) Detach delete n;

// Insertion of URLs in Pathway as a list of properties (only uniformRsourceLocator)
//  set new list
MATCH (a:Pathway_reactome)
SET a.publication_url=[];

// fill list
MATCH p=(a:Pathway_reactome)-[]-(b:URL_reactome) 
SET a. publication_url = a.publication_url + b.uniformResourceLocator;

// delete URL
MATCH (n:URL_reactome) Detach delete n;

// Insertion of LiteratureReference in Pathway as a list of properties (only pubMedIdentifier)
// NOTE!!! 3 publications had no pudMedIdentifier (3 of ~600)
// set new list
MATCH (a:Pathway_reactome) set a.pubMed=[];

// fill list
MATCH p=(a:Pathway_reactome)-[]-(b:LiteratureReference_reactome) 
SET a.pubMed = a.pubMed + b.pubMedIdentifier;

// Insertion of Book in Pathway as a list of properties (only ISBN and title)
// set new list
MATCH (a:Pathway_reactome) set a.books=[];

//fill list
MATCH p=(a:Pathway_reactome)-[]-(b:Book_reactome) 
SET a.books = a.books + ("ISBN:" + b.ISBN + "; Title:" + b.title);

// delete Book
MATCH (n:Book_reactome) Detach delete n;

//Publication was empty and deleted

// Delete all nodes that are not "Homo sapiens" in ReactionLikeEvent
MATCH (s:ReactionLikeEvent_reactome)--(:Pathway_reactome)
WHERE s.speciesName <> "Homo sapiens" 
detach delete s;