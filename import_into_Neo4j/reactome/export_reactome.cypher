CALL apoc.export.graphml.all("/mnt/e/databases//reactome/pathwaydata.graphml", {batchSize:10000, readLabels: true, storeNodeIds: false, useTypes: true});
