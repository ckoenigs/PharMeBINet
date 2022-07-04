import csv
import os
import datetime

# Erstellt das Verzeichnis in dem der Output liegen wird.
# Der Output sind alle mapping, nonmapping und cypher files.
def make_dir():
    print(datetime.datetime.utcnow())
    print("Creating directory \"FDA_mappings\" ...")
    # Das Verzeichnis wird nur erstellt, wenn es nicht schon existiert.
    if not os.path.exists("FDA_mappings"):
        os.makedirs("FDA_mappings")

# Erstellt das Mapping file mit Header.
def make_mapping_file(map_file_name, FDA_attr, CAT_attr):
    # Datei die die erfolgreichen Mappings enthält.
    file_name = "FDA_mappings/" + map_file_name
    f1 = open(file_name, 'w', encoding="utf-8", newline='')
    csv_writer_mapped = csv.writer(f1, delimiter="\t")
    csv_writer_mapped.writerow([FDA_attr, CAT_attr, "how_mapped", "resource"])
    f1.close()

# Erstellt die cypher Datei.
# FDA_name: Name des openFDA Knotens.
# CAT_name: Name des Kategorie Knotens.
# FDA_attr: Identifier des openFDA Knotens.
# CAT_attr: Identifier des Kategorie Knotens.
# _map: Name der Kante.
# cypher_file_name: Name des cypher files.
# map_file_name: Name des mapping files.
def make_cypher_file(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, cypher_file_name, map_file_name, path_of_directory):
    # Cypher-Datei erstellen.
    file_name = "FDA_mappings/" + cypher_file_name
    f = open(file_name, 'a', encoding="utf-8")
    match = "USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM 'file:"
    match += path_of_directory + "mapping_and_merging_into_hetionet/openFDA/FDA_mappings/" + map_file_name
    match += "' AS row FIELDTERMINATOR '\\t' MATCH "
    match += "(n:" + FDA_name + "), (m:" + CAT_name + ") WHERE "
    match += "n." + FDA_attr + " = row." + FDA_attr + " AND m." + CAT_attr + " = row." + CAT_attr
    match += " SET m.resource = split(row.resource,'|')"
    match += " CREATE (m)-[:" + _map + "_merge{how_mapped:row.how_mapped}]->(n);\n"
    f.write(match)
    f.close()

# Übernimmt das Mapping. Schreibt mapping und nonmapping files.
# FDA_name: Name des openFDA Knotens.
# CAT_name: Name des Kategorie Knotens.
# FDA_attr: Identifier des openFDA Knotens.
# CAT_attr: Identifier des Kategorie Knotens.
# _map: Array der mapping-attribute.
# map_file_name: Name des mapping files.
# nonmap_file_name: Array der Namen aller nonmap files.
# _FDA: Array mit den openFDA Knoten Attributen als Array von Dicts. [[{"id": 1, "reaction": A}, ...], ...].
# _CAT: Array mit den Kategorie Knoten Attributen als Dict. [{"reaction": ["id", "source"]}, ...].
def fill_files(FDA_name, CAT_name, FDA_attr, CAT_attr, _map, map_file_name, nonmap_file_name, _FDA, _CAT):
    print(datetime.datetime.utcnow())
    # Alle mapping-attribute als string.
    m = ""
    for s in _map:
        m += s + ","
    m = m[:len(m)-1]
    print("Mapping \"" + FDA_name + "\" and \"" + CAT_name + "\" by \"" + m + "\" ...")
    mapping_arr = {}
    nonmapped_arr = {}
    mapped = {}
    for entry in nonmap_file_name:
        nonmapped_arr[entry] = []
    # Mapping.
    for j in range(len(_FDA)):
        for entry in _FDA[j]:
            # Ist das Attribut aus openFDA in Kategorie.
            if entry[_map[j]] in _CAT[j]:
                # Wenn die Kombination aus id und attribut noch nicht in mapping_arr ist werden id, attribut und resource gespeichert.
                if (entry[FDA_attr[j][0]], _CAT[j][entry[_map[j]]][0]) not in mapping_arr:
                    resource = _CAT[j][entry[_map[j]]][1]
                    resource.append("openFDA")
                    resource = "|".join(sorted(set(resource), key=lambda s: s.lower()))
                    mapping_arr[(entry[FDA_attr[j][0]], _CAT[j][entry[_map[j]]][0])] = [entry[FDA_attr[j][0]], _CAT[j][entry[_map[j]]][0], _map[j], resource]
                    # Speichert ids die schon gemappt wurden.
                    mapped[entry[FDA_attr[j][0]]] = ""
                # Sonst wird dem Punkt how_mapped das attribut hinzugefügt.
                else:
                    if _map[j] not in mapping_arr[(entry[FDA_attr[j][0]], _CAT[j][entry[_map[j]]][0])][2]:
                        mapping_arr[(entry[FDA_attr[j][0]], _CAT[j][entry[_map[j]]][0])][2] = mapping_arr[(entry[FDA_attr[j][0]], _CAT[j][entry[_map[j]]][0])][2] + "," + _map[j]
            # Sonst kann der Knoten nicht gemappt werden.
            else:
                nonmapped_arr[nonmap_file_name[j]].append([entry[FDA_attr[j][0]], entry[_map[j]]])
    
    # Datei die die erfolgreichen Mappings enthält.
    file_name = "FDA_mappings/" + map_file_name
    f1 = open(file_name, 'a', encoding="utf-8", newline='')
    csv_writer_mapped = csv.writer(f1, delimiter="\t")
    for entry in mapping_arr:
        csv_writer_mapped.writerow(mapping_arr[entry])
    f1.close()
    
    for j in range(len(nonmap_file_name)):
        # Datei die die erfolgslosen Mappings enthält.
        file_name = "FDA_mappings/" + nonmap_file_name[j]
        f2 = open(file_name, 'w', encoding="utf-8", newline='')
        csv_writer_notmapped = csv.writer(f2, delimiter="\t")
        csv_writer_notmapped.writerow([FDA_attr[j][0], _map[j]])
        for entry in nonmapped_arr[nonmap_file_name[j]]:
            # Prüft, welcher Knoten aus openFDA über keine Kategorie gemappt werden konnte.
            if entry[0] not in mapped:
                csv_writer_notmapped.writerow(entry)
        f2.close()

# Mapping über umls Datenbank.
# _CAT: Dict der Kategorie Knoten. {"attribut": ["id", "resource"], ...}
# nonmap_name: Name des nonmap files.
# new_node_name: Name des files das die neuen SideEffect Knoten enthält.
# map_name: Name des map files.
def map_others(cur, _CAT, nonmap_name, map_name):
    print(datetime.datetime.utcnow())
    print("Mapping \"" + nonmap_name + "\" and \"" + "umls" + "\" by \"" + "reaction" + "\" ...")
    print("Making new \"SideEffect\" nodes ...")
    # Informationen aus dem nonmapped file auslesen.
    f = open("FDA_mappings/" + nonmap_name + ".tsv", 'r', encoding="utf-8")
    header = f.readline()
    reader = csv.reader(f, delimiter="\t")
    nonmapped = {}
    # Speichert jeden Eintrag der noch nicht gemappt werden konnte als Dictionary.
    # nonmapped: {"reaction": id, ...}
    for line in reader:
        if line[1] in nonmapped:
            line[1] = line[1].capitalize()
            nonmapped[line[1]] = line[0]
        else:
            nonmapped[line[1]] = line[0]
    f.close()
    db = {}
    # Iteriert über jeden Eintrag der umls Datenbank und speichert ihn als Dictionary.
    # db: {"reaction": CUI, ...}
    for (cui_, str_) in cur:
        db[str_.lower()] = cui_
    ids = {}
    # Iteriert über jeden Eintrag der zu mappenden Kategorie und speichert ihn als Dictionary.
    # ids: {"identifier of SideEffect (CUI)": "resource", ...}
    for entry in _CAT:
        ids[_CAT[entry][0]] = _CAT[entry][1]
    unique_cuis = []
    # Iteriert über jeden Eintrag in to_SideEffect und speichert die CUIs ab, die schon neue
    # SideEffect Knoten erstellen sollen.
    # unique_cuis: ["CUI", ...] set
    if os.path.exists("FDA_mappings/to_SideEffect.tsv"):
        f = open("FDA_mappings/to_SideEffect.tsv", 'r', encoding="utf-8", newline='')
        f.readline()
        reader = csv.reader(f, delimiter="\t")
        # Speichert die CUIs die schon erstellt werden.
        for entry in reader:
            unique_cuis.append(entry[0])
        f.close()
        head = False
    else:
        head = True
    unique_cuis = set(unique_cuis)
    # Datei die die neuen SideEffect Knoten enthält.
    f = open("FDA_mappings/to_SideEffect.tsv", 'a', encoding="utf-8", newline='')
    writer = csv.writer(f, delimiter="\t")
    if head:
        writer.writerow(["identifier", "name", "resource"])
    # Mapping Datei.
    f2 = open("FDA_mappings/" + map_name + ".tsv", 'a', encoding="utf-8", newline='')
    writer2 = csv.writer(f2, delimiter="\t")
    # Nonmapping Datei.
    f3 = open("FDA_mappings/" + nonmap_name + ".tsv", 'w', encoding="utf-8", newline='')
    writer3 = csv.writer(f3, delimiter="\t")
    writer3.writerow(["id", "name"])
    # Jeder Eintrag der noch nicht gemappt werden konnte.
    for entry in nonmapped:
        # Existiert das Attribut in der Datenbank und die CUI ist noch nicht in SideEffects,
        # dann wird ein neuer SideEffect Knoten erstellt.
        # Außerdem wird der openFDA Knoten mit diesem gemappt.
        lower_entry=entry.lower()
        if lower_entry in db and db[lower_entry] not in ids:
            # Checkt, ob ein Knoten mit der CUI schon erstellt wurde.
            if db[lower_entry] not in unique_cuis:
                writer.writerow([db[lower_entry], lower_entry, "openFDA"])
                writer2.writerow([nonmapped[entry], db[lower_entry], "new", "openFDA"])
                unique_cuis.add(db[lower_entry])
            else:
                writer2.writerow([nonmapped[entry], db[lower_entry], "new", "openFDA"])
        # Existiert das Attribut in der Datenbank und die CUI ist schon in SideEffects,
        # dann wird der openFDA Knoten über die CUI mit dem SideEffect Knoten gemappt.
        elif lower_entry in db and db[lower_entry] in ids:
            resource = ids[db[lower_entry]]
            resource.append("openFDA")
            resource = "|".join(sorted(set(resource), key=lambda s: s.lower()))
            writer2.writerow([nonmapped[entry], db[lower_entry], "name,umls", resource])
        else:
            writer3.writerow([nonmapped[lower_entry], lower_entry])
    f.close()
    f2.close()
    f3.close()
