module.exports = {
  "file": "./csv/CTD_pheno_term_ixns.csv",
  "database": {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "pw": "test"
  },
  "fields": [
    "chemicalname",
    "chemicalid",
    "casrn",
    "phenotypename",
    "phenotypeid",
    "comentionedterms",
    "organism",
    "organismid",
    "interaction",
    "interactionactions",
    "anatomyterms",
    "inferencegenesymbols",
    "pubmedids"
  ],
  "relations": {
    "phenotype": {
      "CTDchemical": {
        "chemical_id": "chemicalid"
      },
      "CTDGO": {
        "go_id": "phenotypeid"
      },
      "create": false
    }
  },
  "complexRelations": [
    {
      $sql: `MATCH (a:Chemical)-[]->(b:CTDchemical)-[r:phenotype]->(c:CTDGO)-[:equal_to_CTD_go ]-(d)
             WHERE b.chemical_id = {chemicalid} AND c.go_id = {phenotypeid}  AND r.organismid='9606'
             MERGE (a)-[n:{{relationtype}}]->(d)
             ON CREATE SET n={line}
             ON MATCH SET n.pubmedids = 
               CASE 
                WHEN {pubmedid} IN n.pubmedids 
                THEN n.pubmedids
                ELSE n.pubmedids + {pubmedids}
               END`,
      "relationtype": (line) => {

        let aName = line.chemicalname.trim();
        let bName = line.phenotypename.trim();
        let interaction = line.interactionactions; // Array

        // We want only the content in brackets
        //let actions = line.interaction.match(/\[.+]/);
        let actions = [line.interaction];
        if(actions === null) {
          return "ASSOCIATES_CaGO";
        }
        actions = actions[0].trim();
        // actions = actions.substring(1, actions.length -1);

        let actionChecker = (action) => {
          // Check if both names are in the action
          if(action.includes(aName) && action.includes(bName)) {
            let re = new RegExp (
                aName.replace(/\(/g, "\\(").replace(/\)/g, "\\)") +
                "(.*)" +
                bName.replace(/\(/g, "\\(").replace(/\)/g, "\\)") );
            let match = re.exec(action);
            // aName and bName has a wrong order -> no real relation
            if(match === null) {
              return false;
            }
            match = match[1];
            if(match.includes("[") || match.includes("]") || match.includes("and")) {
              return false;
            }
            return true;
          } else {
            return false;
          }
        };
        actionChecker(actions);

        if(interaction.includes("affects^phenotype")) {
          return "ASSOCIATES_CaGO";
        }
        if(interaction.includes("phenotype^increase") || interaction.includes("increases^phenotype")) {
          return actionChecker(actions) ? "UPREGULATES_CiGO" : "ASSOCIATES_CaGO"
        }

        if(interaction.includes("phenotype^decrease") || interaction.includes("decreases^phenotype")) {
          return actionChecker(actions) ? "DOWNREGULATES_CdGO" : "ASSOCIATES_CaGO"
        }
      },
      // Must return a boolean
      $insert: (line) => {
        // Line should only inserted, if interactionactions are valid
        return !(!line.interactionactions.includes("decreases^phenotype") &&
            !line.interactionactions.includes("phenotype^decrease") &&
            line.interactionactions !== "decreases^phenotype" &&
            !line.interactionactions.includes("increases^phenotype") &&
            !line.interactionactions.includes("phenotype^increase") &&
            line.interactionactions !== "increases^phenotype" &&
            !line.interactionactions.includes("affects^phenotype") &&
            line.interactionactions !== "affects^phenotype");
      },
      // Must return a sql chiper json
      $chipher: (line) => {
        let tmpLine = {};
        Object.assign(tmpLine, line);
        delete tmpLine.chemicalid;
        delete tmpLine.phenotypeid;

        // Make Pubmedids to a list, so that we can add elements later
        let pubmed = tmpLine.pubmedids;
        if(typeof tmpLine.pubmedids === "string") {
          tmpLine.pubmedids = [tmpLine.pubmedids]
        }

        return Object.assign({}, {chemicalid: line.chemicalid, phenotypeid: line.phenotypeid, line: tmpLine, pubmedid: pubmed, pubmedids: tmpLine.pubmedids}, tmpLine)
      }
    }
  ],
  "removeFields": ["casrn"],
  "removeFieldsByValue": {
    "match": {

    },
    "noMatch": {
      "organism": "Homo sapiens"
    }
  }
};
