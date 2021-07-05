Match (n) Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[n]->() Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[n]->() Where exists(n.pubMedIDs) Set n.pubMed_ids=n.pubMedIDs Remove n.pubMedIDs;
Match ()-[n]->() Where exists(n.pubmed_ids) Set n.pubMed_ids=n.pubmed_ids Remove n.pubmed_ids;
MATCH (n:Anatomy) where exists(n.bto_id) or exists(n.mesh_id) Set n.xrefs=[];
MATCH (n:Anatomy) where exists(n.bto_id) Set n.xrefs=n.xrefs + ["BTO:"+n.bto_id];
MATCH (n:Anatomy) where exists(n.mesh_id) Set n.xrefs=n.xrefs + ["MeSH:"+n.mesh_id];
Match (g:Gene) Set g.identifier=toString(g.identifier);
MATCH (n:Symptom) Set n.xrefs=["MESH:"+n.identifier];

