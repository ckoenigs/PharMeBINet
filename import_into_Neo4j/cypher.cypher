Match (n) Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[n]->() Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[n]->() Where exists(n.pubMedIDs) Set n.pubMed_ids=n.pubMedIDs Remove n.pubMedIDs;
Match ()-[n]->() Where exists(n.pubmed_ids) Set n.pubMed_ids=n.pubmed_ids Remove n.pubmed_ids;
MATCH (n:Anatomy) where exists(n.bto_id) or exists(n.mesh_id) Set n.xrefs=[];
MATCH (n:Anatomy) where exists(n.bto_id) Set n.xrefs=n.xrefs + ["BTO:"+n.bto_id];
MATCH (n:Anatomy) where exists(n.mesh_id) Set n.xrefs=n.xrefs + ["MeSH:"+n.mesh_id];
Match (g:Gene) Set g.identifier=toString(g.identifier);
MATCH (n:Symptom) Set n.xrefs=["MESH:"+n.identifier];
Match (:Compound)-[r]->(:Compound) Where exists(r.similarity) Set r.similarity_dice_and_ecfp=r.similarity Remove r.similarity;
Match (a:Compound)-[r:CAUSES_CcSE]->(b) Create (a)-[h:CAUSES_CHcSE]->(b) Set h=r Delete r;
Match (a:Compound)-[r:BINDS_CbG]->(b) Create (a)-[h:BINDS_CHbG]->(b) Set h=r Delete r;
Match (a:Compound)-[r:DOWNREGULATES_CdG]->(b) Create (a)-[h:DOWNREGULATES_CHdG]->(b) Set h=r Delete r;
Match (a:Compound)-[r:UPREGULATES_CuG]->(b) Create (a)-[h:UPREGULATES_CHuG]->(b) Set h=r Delete r;
Match (a:Compound)-[r:TREATS_CtD]->(b) Create (a)-[h:TREATS_CHtD]->(b) Set h=r Delete r;
Match (a:Compound)-[r:PALLIATES_CpD]->(b) Create (a)-[h:PALLIATES_CHpD]->(b) Set h=r Delete r;
