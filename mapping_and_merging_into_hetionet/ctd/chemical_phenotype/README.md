# Neo4JCSVImporter
This Node.js module can insert comma-separated .csv files into Neo4J database relation. 
It can create not existing nodes or log them into a new csv file.

## Installation
Run `npm install` to install all dependencies

## Configuration
1. Copy the `config.example.json` into the `configs` folder. 
2. Modify config file
3. Repeat this as many csv files you want to insert

### Example configuration
```javascript
{
  "file": "path to csv file",
  "database": {
    "uri": "neo4juri",
    "user": "username for database",
    "pw": "password for database"
  },
  "fields": ["List", "with", "all", "Fields", "of", "the", "csv", "file"],
  "relations": {
    // Create Relation: MATCH (a:nameA),(b:nameB) WHERE a.fieldnameA = {properties[fieldValueA]} AND b.fieldnameB = {properties[fieldValueB]} CREATE (a)-[r:relationname {properties}]->(b) RETURN r
    "relationname": {
      "nameA": {
        "fieldnameA": "fieldValueA"
      },
      "nameB": {
        "fieldnameB": "fieldValueB"
      },
      "create": false // set to true, if you want to create not existing A or B nodes
    }
  },
  "removeFields": ["List", "with", "all", "fieldnames", "which", "should", "not", "inserted", "as", "a", "property"],
  "removeFieldsByValue": {
    "match": { // The line[fielname] is not allowed to have this value, then the line would be removed
      "fieldname": "value"
    },
    "noMath": { // The line[fieldname] should have exact this value, otherwise remove this line
      "fieldname": "value"
    }
  }
}
```

## Run
Run `npm run` to process all config-files in the `configs` folder
The output should be like this:
```
2019-2-8 21:03:34  [ ctd.json ]: Begin process for this config file
2019-2-8 21:03:38  [ ctd.json ]: Read lines finished. Found  68721  lines. Start SQL insertion
  Inserting Lines: [===================================================================] 35/lps 100%
2019-2-8 21:36:45  [ ctd.json ]: Finished SQL insertion and finished this config file
```
If you disable the `create` parameter in the relation, a folder `missing` is created with all missing relations which could not created
Hint: The script will run much faster, if you disable the `create` parameter. 
