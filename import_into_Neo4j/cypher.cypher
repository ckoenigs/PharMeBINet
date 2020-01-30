Match (n) Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[n]->() Set n.hetionet='yes', n.resource=['Hetionet'];
Match ()-[r]->() Where not exists(r.urls) Set r.urls=[];
Match (n) Where not exists(n.xrefs) Set n.xrefs=[]

