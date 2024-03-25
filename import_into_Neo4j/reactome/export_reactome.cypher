//Extraktion via APOC
//Nodes and relationships of Reactome
//CALL apoc.export.graphml.all("../../../../mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/reactome/pathwaydata.graphml", {batchSize:10000, readLabels: true, storeNodeIds: false, useTypes: true});
CALL apoc.export.graphml.all("/mnt/aba90170-e6a0-4d07-929e-1200a6bfc6e1/databases/reactome/pathwaydata.graphml", {batchSize:10000, readLabels: true, storeNodeIds: false, useTypes: true});
