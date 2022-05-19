//Create new Node "ReactionLikeEvent"
CREATE CONSTRAINT ON (a:ReactionLikeEvent) ASSERT a.identifier IS UNIQUE;

//Create new Node "Reaction"
CREATE CONSTRAINT ON (a:Reaction) ASSERT a.identifier IS UNIQUE;

MATCH (n:Reaction_reactome) WHERE n.speciesName = "Homo sapiens" and exists(n.pubMed_ids)
CREATE (m:Reaction :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_reaction]-(n);

//Create new Node "Polymerisation"
CREATE CONSTRAINT ON (a:Polymerisation) ASSERT a.identifier IS UNIQUE;

MATCH (n:Polymerisation_reactome) WHERE n.speciesName = "Homo sapiens" and exists(n.pubMed_ids)
CREATE (m:Polymerisation :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_polymerisation]-(n);

//Create new Node "Depolymerisation"
CREATE CONSTRAINT ON (a:Depolymerisation) ASSERT a.identifier IS UNIQUE;

MATCH (n:Depolymerisation_reactome) WHERE n.speciesName = "Homo sapiens" and exists(n.pubMed_ids)
CREATE (m:Depolymerisation :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome"})<-[:equal_to_reactome_depolymerisation]-(n);

//Create new Node "BlackBoxEvent"
CREATE CONSTRAINT ON (a:BlackBoxEvent) ASSERT a.identifier IS UNIQUE;

MATCH (n:BlackBoxEvent_reactome) WHERE n.speciesName = "Homo sapiens" and exists(n.pubMed_ids)
CREATE (m:BlackBoxEvent :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_blackBoxEvent]-(n);

//Create new Node "FailedReaction"  
CREATE CONSTRAINT ON (a:FailedReaction) ASSERT a.identifier IS UNIQUE;

MATCH (n:FailedReaction_reactome) WHERE n.speciesName = "Homo sapiens" and exists(n.pubMed_ids)
CREATE (m:FailedReaction :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_failedreaction]-(n);

//-------------------- Create Regulation --------------------------------------------------
// CREATE CONSTRAINT ON (a:Regulation) ASSERT a.identifier IS UNIQUE;
 
// MATCH (n:Regulation_reactome)--(m:PhysicalEntity_reactome)
// WHERE m.speciesName = "Homo sapiens" and exists(n.pubMed_ids) WITH distinct n
// CREATE (m:Regulation{identifier:toString(n.dbId), name:n.displayName, alternative_id:n.oldStId, pubMed_ids:n.pubMed_ids,
// url:"https://reactome.org/content/detail/" + n.stId})<-[:equal_to_reactome_regulation]-(n);

//Create new Node "MolecularComplex"
// CREATE CONSTRAINT ON (a:MolecularComplex) ASSERT a.identifier IS UNIQUE;

// MATCH (n:Complex_reactome) WHERE n.speciesName = "Homo sapiens"
// CREATE (m:MolecularComplex{identifier:n.stId, synonyme:n.name, name:n.displayName, alternativeId:n.oldStId, pubMed:n.pubMed,
// isInDisease:n.isInDisease, isChimeric:n.isChimeric, systematicName:n.systematicName, stoichiometryKnown: n.stoichiometryKnown,
// url:"https://reactome.org/content/detail/" + n.stId})<-[:equal_to_reactome_complex]-(n);
