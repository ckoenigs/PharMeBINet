//Create new Node "ReactionLikeEvent"
CREATE INDEX indexReactionLikeEvent FOR (node:ReactionLikeEvent) ON (node.identifier);

//Create new Node "Reaction"
CREATE INDEX indexReaction FOR (node:Reaction) ON (node.identifier);

MATCH (n:Reaction_reactome) WHERE n.speciesName = "Homo sapiens" and n.pubMed_ids is not NULL
CREATE (m:Reaction :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_reaction]-(n);

//Create new Node "Polymerisation"
CREATE INDEX indexPolymerisation FOR (node:Polymerisation) ON (node.identifier);

MATCH (n:Polymerisation_reactome) WHERE n.speciesName = "Homo sapiens" and n.pubMed_ids is not NULL
CREATE (m:Polymerisation :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_polymerisation]-(n);

//Create new Node "Depolymerisation"
CREATE INDEX indexDepolymerisation FOR (node:Depolymerisation) ON (node.identifier);

MATCH (n:Depolymerisation_reactome) WHERE n.speciesName = "Homo sapiens" and n.pubMed_ids is not NULL
CREATE (m:Depolymerisation :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome"})<-[:equal_to_reactome_depolymerisation]-(n);

//Create new Node "BlackBoxEvent"
CREATE INDEX indexBlackBoxEvent FOR (node:BlackBoxEvent) ON (node.identifier);

MATCH (n:BlackBoxEvent_reactome) WHERE n.speciesName = "Homo sapiens" and n.pubMed_ids  is not NULL
CREATE (m:BlackBoxEvent :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_blackBoxEvent]-(n);

//Create new Node "FailedReaction"  
CREATE INDEX indexFailedReaction FOR (node:FailedReaction) ON (node.identifier);

MATCH (n:FailedReaction_reactome) WHERE n.speciesName = "Homo sapiens" and n.pubMed_ids is not NULL
CREATE (m:FailedReaction :ReactionLikeEvent{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), node_edge:true, name:n.displayName, alternative_id:n.oldStId, isInDisease:n.isInDisease, isChimeric:n.isChimeric,
category:n.category, isInferred:n.isInferred, definition:n.definition, resource:['Reactome'], license:'CC BY 4.0',  reactome:'yes', url:"https://reactome.org/content/detail/"+ n.stId, pubMed_ids:n.pubMed_ids, source:"Reactome", systematicName:n.systematicName})<-[:equal_to_reactome_failedreaction]-(n);

//-------------------- Create Regulation --------------------------------------------------
CREATE INDEX indexRegulation FOR (node:Regulation) ON (node.identifier);
 
MATCH (n:Regulation_reactome)--(m:PhysicalEntity_reactome)
WHERE m.speciesName = "Homo sapiens" and n.pubMed_ids is not NULL WITH distinct n
CREATE (m:Regulation{identifier:toString(n.dbId), name:n.displayName, alternative_id:n.oldStId, pubMed_ids:n.pubMed_ids, node_edge:true,
url:"https://reactome.org/content/detail/" + n.stId, source:'Reactome', resource:['Reactome'], reactome:'yes', license:'CC BY 4.0'})<-[:equal_to_reactome_regulation]-(n);

//Create new Node "MolecularComplex"
CREATE INDEX indexMolecularComplex FOR (node:MolecularComplex) ON (node.identifier);

MATCH (n:Complex_reactome) WHERE n.speciesName = "Homo sapiens"
CREATE (m:MolecularComplex{identifier:n.stId, synonyms:apoc.convert.fromJsonList(n.name), name:n.displayName, alternative_id:n.oldStId, pubMed:n.pubMed,
isInDisease:n.isInDisease, isChimeric:n.isChimeric, systematicName:n.systematicName, stoichiometryKnown: n.stoichiometryKnown,
url:"https://reactome.org/content/detail/" + n.stId, source:'Reactome', resource:['Reactome'], reactome:'yes', license:'CC BY 4.0'})<-[:equal_to_reactome_complex]-(n);

