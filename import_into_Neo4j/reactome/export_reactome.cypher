CALL apoc.export.graphml.all("/media/cassandra/T7/System_Volume_Information/databases//reactome/pathwaydata.graphml", {batchSize:10000, readLabels: true, storeNodeIds: false, useTypes: true});
