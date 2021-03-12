existing_file = open("C:/Users/Dietrich/Downloads/neo4j-community-3.5.4/pathwaydata.graphml", "r", encoding="utf8")
new_file = open("pathwaydata_replaced.graphml", "w", encoding="utf8")
for line in existing_file:
    if line[0:5]=="<node":
        labels = line.split("labels=\"")[1].split("\">")[0]
        newlabels= ""
        for label in labels.split(":")[1:]:
            newlabels+= ":" + label+"_reactome"
        line = line.replace(labels, newlabels)
        new_file.write(line)
    else:
        new_file.write(line)