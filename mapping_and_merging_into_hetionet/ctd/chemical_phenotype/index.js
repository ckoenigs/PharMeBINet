const fs = require("fs");
const path = require("path");
const neo4j = require('neo4j-driver');
const ProgressBar = require('progress');
const configFolder = "./configs/";
const missingFolder = "./missing/";


/**
 * Read a csv file line by line and returns an JSON object list of it
 * Use the config file, to modify the format.
 * Async function! - Use await to get the list
 * @param config Configuration file object
 * @returns {Promise<list>} Promise or list with json of each line
 */
async function readCSV(config) {
    // Open file stream
    const lineReader = require('readline').createInterface({
        input: fs.createReadStream(config.file)
    });

    // Parse lines
    let lines = [];
    lineReader.on('line', function (line) {
        lineConverter(line, lines, config)
    });

    return await new Promise(resolve => {
        lineReader.on('close', () => {
            resolve(lines)
        });
    });
}

/**
 * Gets a line string, convert it to json
 * @param line LineString which should be converted
 * @param lines Object in which the converted line should store to
 * @param config config file object
 */
function lineConverter (line, lines, config) {
    // Ignore all comments
    if(line.startsWith("#")) {
        return;
    }

    var splitted = line.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);

    var obj = {};
    config.fields.forEach((field, index) => {
        var tmp = splitted[index].replace("\"", "");

        // Separate strings to list, if they have a separator in it
        if(tmp.includes("|")) {
            tmp = tmp.split("|")
        }
        // Split if value is a list
        obj[field] = tmp;
    });

    // Remove keys, which should not exist
    if(!filterObject(obj, config)) {
        lines.push(obj);
    }
}

/**
 * Remove all fields, that should not be in the object
 *
 * @param object the given object
 * @param config object which contains the removeFields element
 * @returns boolean true = don't push element to list, false = add element to list
 */
function filterObject(object, config) {
    // Remove unessesary fields
    config.removeFields.forEach((x) => {
        delete object[x];
    });

    let removeObject = false;

    // Remove object, if value does not match
    Object.keys(config.removeFieldsByValue.noMatch).forEach((x) => {
        if (object[x] !== config.removeFieldsByValue.noMatch[x]) {
            removeObject = true;
        }
    });

    // Skip the next filter, because the line should allready removed
    if(removeObject === true) {
        return removeObject;
    }

    // Remove object if value match
    Object.keys(config.removeFieldsByValue.match).forEach((x) => {
        if (object[x] === config.removeFieldsByValue.match[x]) {
            removeObject = true;
        }
    });

    return removeObject;
}
async function complexRelation(relation, line, driver) {
    // Skip insertion if config values not pass
    if(!relation.$insert(line)) {
        return;
    }

    // Load sql statement and replace all {{values}} with the relation entry
    let stmt = relation.$sql;
    let vars = stmt.match(/{{\w+}}/gi);
    for(var i in vars) {
        let tmp = vars[i].replace("{{", "").replace("}}", "");
        stmt = stmt.replace(vars[i], relation[tmp](line));
    }

    // Run SQL statement
    const session = driver.session();
    const result = await session.run(
        stmt,
        relation.$chipher(line)
    );
    session.close();
}

async function createSQL (line, config, driver, fileStream) {
    // Create complex relations
    for(let id in config.complexRelations) {
        let relation = config.complexRelations[id];
        await complexRelation(relation, line, driver);
    }

    // Create simple relations
    for(let relationName in config.relations) {
        // Define all relation values
        let relation = config.relations[relationName];
        let override = relation.create;
        // Delete this entry to get always the correct A and B keys
        delete relation.create;
        let aName = Object.keys(relation)[0];
        let bName = Object.keys(relation)[1];
        relation.create = override;
        let a = Object.keys(relation[aName])[0];
        let aFieldKey = relation[aName][a];
        let aFieldVal = line[aFieldKey];
        let b = Object.keys(relation[bName])[0];
        let bFieldKey = relation[bName][b];
        let bFieldVal = line[bFieldKey];

        // Remove relation keys from object
        delete line[aFieldKey];
        delete line[bFieldKey];

        // If aFieldVal is a list with values -> create for each entry of the list a relation (bFieldVal check is in insert4Neo)
        if(typeof aFieldVal === "object") {
            for(let x in aFieldVal) {
                await insert4Neo(relationName, aName, bName, a, b, aFieldVal[x], bFieldVal, line, override, driver, fileStream);
            }
        } else {
            await insert4Neo(relationName, aName, bName, a, b, aFieldVal, bFieldVal, line, override, driver, fileStream);
        }
    }
}

async function insert4Neo(relationName, aName, bName, a, b, aFieldVal, bFieldVal, line, override, driver, fileStream) {
    // If bFieldVal is a list with values -> create for each entry of the list a relation (aFieldVal check is in createSQL)
    if(typeof bFieldVal === "object") {
        for(let x in bFieldVal) {
            await insert4Neo(relationName, aName, bName, a, b, aFieldVal, bFieldVal[x], line, override, driver, fileStream)
        }
        return;
    }

    // Create Neo4J statement
    let stmt = "";
    if(override) {
        // Create relation A-[relation]->B and create nodes A & B if they are not existing
        stmt = "MERGE (a:" + aName + " {" + a + ": {aFieldVal}}) \n" +
            "MERGE (b:" + bName + " {" + b + ": {bFieldVal}}) \n" +
            "MERGE (a)-[r:" + relationName + " " +
            /*
            JSON.stringify would create an object like {"key": "value", ...}
            For reasons I can't understand, Neo4J wants an object like {key: "value"} -> replace quotes for keys:
            */
            JSON.stringify(line)
                .replace(/\\"/g,"\uFFFF")
                .replace(/\"([^"]+)\":/g,"$1:")
                .replace(/\uFFFF/g,"\\\"") +
            "]->(b) \n";
    } else {
        // Create only the relation A-[relation]->B and show console output, if line could not created
        stmt = "MATCH (a:" + aName + "),(b:" + bName + ") WHERE a." + a + " = {aFieldVal} AND b." + b + " = {bFieldVal} CREATE (a)-[r:" + relationName + " {line}]->(b) RETURN r";
    }

    // Neo4J insertion
    const session = driver.session();
    const result = await session.run(
        stmt,
        {aFieldVal: aFieldVal, bFieldVal: bFieldVal, line: line}
    );

    // Log missing lines -> only possible, if lines should not created
    if(!override && typeof result.records[0] === "undefined") {
        console.log("  Error: Relation (" + aName + "." + a+ "=" + aFieldVal+ " -> " + bName + "." + b + "=" + bFieldVal+ ") could not created");
        fileStream.write(relationName +"," + aFieldVal + "," + bFieldVal + "\n");
    }

    // Close session
    session.close();
}

/**
 * Insert all lines in sql.
 * @param lines all lines list
 * @param config current config file
 * @param driver Neo4J driver
 * @returns {Promise<void>}
 */
async function insertLines(lines, config, driver) {
    // Init progress bar
    let bar = new ProgressBar('  Inserting Lines: [:bar] :rate/lps :percent', {
        complete: '=',
        incomplete: ' ',
        total: lines.length
    });

    // Open filestream for new csv file with all missing nodes
    if (!fs.existsSync(missingFolder)){
        fs.mkdirSync(missingFolder);
    }
    let fileStream = fs.createWriteStream("./missing/missingData_" + path.basename(config.file, '.csv')+ ".csv", {flags:'a'});
    fileStream.write("RelationName,AFieldValue,BFieldValue\n");

    // Insert all lines
    for(var key in lines) {
        var line = lines[key];
        await createSQL(line, config, driver, fileStream );
        bar.tick();
    }

    fileStream.end();
}

function openSQL(config) {
    return neo4j.driver(config.database.uri, neo4j.auth.basic(config.database.user, config.database.pw));
}

/**
 * Convert all files in the configFolder.
 */
function convertAll() {
    fs.readdir(configFolder, (err, files) => {
        files.forEach(async file => {
            console.log(new Date().toLocaleString(), " [", file, "]: Begin process for this config file");
            var config = require('./' + path.join(configFolder, file));
            let lines = await readCSV(config);
            console.log(new Date().toLocaleString(), " [", file, "]: Read lines finished. Found ", lines.length, " lines. Start SQL insertion");
            let driver = openSQL(config);
            await insertLines(lines, config, driver);
            driver.close();
            console.log(new Date().toLocaleString(), " [", file, "]: Finished SQL insertion and finished this config file");
        });
    })
}

convertAll();