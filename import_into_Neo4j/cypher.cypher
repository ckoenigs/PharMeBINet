Match (n) Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[n]->() Set n.hetionet='yes', n.resource=['Hetionet'];
MATCH (n:Anatomy) where exists(n.bto_id) or exists(n.mesh_id) Set n.xrefs=[];
MATCH (n:Anatomy) where exists(n.bto_id) Set n.xrefs=n.xrefs + ["BTO:"+n.bto_id];
MATCH (n:Anatomy) where exists(n.mesh_id) Set n.xrefs=n.xrefs + ["MeSH:"+n.mesh_id];
# Match (n) Where not exists(n.xrefs) Set n.xrefs=[];
#Match ()-[r]->() Where not exists(r.urls) Set r.urls=[];
