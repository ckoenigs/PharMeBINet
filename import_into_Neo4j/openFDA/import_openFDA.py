import os
import requests
import zipfile
import json
from pathlib import Path
import sys
import shutil
import csv, datetime


class directory_maker():
    def __init__(self):
        pass

    """ Erstellt die Verzeichnisse.
        directories: Name des Verzeichnisses. """

    def make_directory(self, directories):
        for directory in directories:
            print("Creating directory " + directory + " ...")
            try:
                os.mkdir(directory)
            except BaseException:
                pass


class downloader():
    def __init__(self, parser):
        self.parser = parser

    """ Ändert den Namen der Dateien.
        s: Name der Dateien als String. """

    def trim(self, s):
        return s.replace(
            " (all)",
            "").replace(
            " data",
            "").replace(
            "/",
            "_").replace(
            " ",
            "_").replace(
            "All",
            "all")

    """ Downloaded und speichert die Datei, wenn diese noch nicht vorhanden ist.
        files: Alle Dateien im Verzeichnis.
        directories: Das Oberverzeichnis.
        entry: Die Datei die gedownloaded werden soll.
        directory_name: Das Unterverzeichnis. """

    def make_file(self, files, directories, entry, directory_name):
        name = self.trim(entry["display_name"])
        # Prüft, ob die Datei bereits gedownloadet ist. Sonst wird sie gedownloaded.
        n = (str(Path(directories[directory_name]).name) + "_" + name + ".json.zip").replace("__", "_")
        z = True
        for f in files:
            if f.endswith(".zip") or f.endswith(".json"):
                z = False
        if n not in files and z:
            r = requests.get(entry["file"], allow_redirects=True)
            open((directories[directory_name] +
                  "/" +
                  str(Path(directories[directory_name]).name) +
                  "_" +
                  name +
                  ".json.zip").replace("__", "_"), 'wb').write(r.content)

    """ Filtert die Download-Links aus der download.json.
        f: Die download.json.
        directories: Das Oberverzeichnis. """

    def download(self, f, directories):
        dictionary = self.parser.parse(f)
        dictionary = dictionary["results"]
        drug = dictionary["drug"]
        food = dictionary["food"]
        other = dictionary["other"]

        if "CAERSReports" in directories:
            files = os.listdir(directories["CAERSReports"])
            for entry in food["event"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "CAERSReports")

        if "DrugAdverseEvents" in directories:
            files = os.listdir(directories["DrugAdverseEvents"])
            for entry in drug["event"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DrugAdverseEvents")

        if "DrugRecallEnforcementReports" in directories:
            files = os.listdir(directories["DrugRecallEnforcementReports"])
            for entry in drug["enforcement"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DrugRecallEnforcementReports")

        if "FoodRecallEnforcementReports" in directories:
            files = os.listdir(directories["FoodRecallEnforcementReports"])
            for entry in food["enforcement"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "FoodRecallEnforcementReports")

        if "NationalDrugCodeDirectory" in directories:
            files = os.listdir(directories["NationalDrugCodeDirectory"])
            for entry in drug["ndc"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "NationalDrugCodeDirectory")

        if "SubstanceData" in directories:
            files = os.listdir(directories["SubstanceData"])
            for entry in other["substance"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "SubstanceData")


class unzipper:
    def __init__(self):
        pass

    """ Entzippt die Dateien und speichert sie unter neuem Namen.
        Anschließend werden sie in das richtige Verzeichnis kopiert.
        Das temporär erstellte Verzeichnis wird gelöscht.
        directory: Das Verzeichnis in der die Datei 'f' liegt.
        f: Eine zip-Datei. """

    def unzip(self, directory, f):
        print("Unzipping " + "\"" + f + "\" ...")
        with zipfile.ZipFile(f, 'r') as zipped:
            # Infos über die Zip-Datei.
            zipinfos = zipped.infolist()
            if (len(zipinfos) == 1):
                # Festlegen des richtigen Dateinamens und Verzeichnisses.
                zipinfo = zipinfos[0]
                name = os.path.basename(f).split(".")
                name = name[0] + '.' + name[1]
                zipinfo.filename = os.path.basename(os.path.abspath(directory)) + '/' + name
                # Prüft, ob die Datei nicht schon entzippt wurde. Sonst wird sie entzippt.
                if name not in os.listdir(directory):
                    # Entzippen der Datei in einen Ordner des momentanen Verzeichnisses des Programms.
                    zipped.extract(zipinfo)
                    # Verschieben der Datei in das Verzeichnis am richtigen Ort.
                    shutil.move(zipinfo.filename, directory + '/' + os.path.basename(zipinfo.filename))
                    # Löschen des Verzeichnisses im Ordner des Programms.
                    os.rmdir(os.path.dirname(zipinfo.filename))
        zipped.close()

    """ Unzipped alle Dateien im Verzeichnis.
        directory: Das Verziechnis in dem alle zip-Dateien entpackt werden sollen. """

    def unzipall(self, directory):
        # Entzippt alle Zip-Dateien im Verzeichnis.
        files = os.listdir(directory)
        for f in files:
            if (f.endswith('.zip')):
                self.unzip(directory, directory + '/' + f)


class parser:
    def __init__(self):
        pass

    """ Lädt die Datei in ein Dictionary.
        path: Der Dateipfad der json-Datei die geparsed werden soll. """

    def parse(self, path):
        print("Parsing " + "\"" + path + "\" ...")
        with open(path, 'r') as f:
            data = json.load(f)
        f.close()
        return data


class reader:
    def __init__(self, parser, former):
        self.parser = parser
        self.former = former

    """ Geht alle Dateien des Verzeichnis durch.
        directory: Das Verzeichnis in dem die json-Dateien liegen. """

    def readall(self, directory):
        files = os.listdir(directory)
        jsons = []
        for f in files:
            if (f.endswith('.json')):
                jsons.append(f)
        jsons.sort()
        jsons_old = []
        jsons_new = []
        # Prüft, ob das Programm schon einmal mit json-Dateien ausgeführt wurde
        if ("jsons.txt" in files):
            fl = open(directory + "/" + "jsons.txt", 'r', encoding="utf-8")
            for f in fl:
                jsons_old.append(f.replace("\n", ""))
            fl.close()
            # 2 Fälle
            # 1. Eine json-Datei aus einem vorheringen Aufruf fehlt
            # In diesem Fall werden die tsv-Dateien gelöscht, da sie keine
            # nicht vorhandenen json-Einträge enthalten sollen
            continue_ = True
            for f in jsons_old:
                if f not in jsons:
                    continue_ = False
                    os.remove(directory + "/" + "jsons.txt")
                    for tsv in files:
                        if tsv.endswith('.tsv'):
                            os.remove(directory + "/" + tsv)
                    break
            # Anschließend werden die jetzt verwendeten json-Dateien in jsons.txt geschrieben
            if not continue_:
                jsons.sort()
                fl = open(directory + "/" + "jsons.txt", 'w', encoding="utf-8")
                for f in jsons:
                    jsons_new.append(f)
                    fl.write(f + '\n')
                fl.close()
            # Es wurde keine bereits vorhandene Datei gelöscht
            if continue_:
                # 2. Eine oder mehrere json-Dateien sind hinzugekommen
                # Die bereits verwendeten json-Dateien werden als erstes hinzugefügt
                for f in jsons_old:
                    jsons_new.append(f)
                # Die neuen json-Dateien werden hinzugefügt
                for f in jsons:
                    if f not in jsons_new:
                        jsons_new.append(f)
                # Die jetzt verwendeten json-Dateien werden in jsons.txt geschrieben
                fl = open(directory + "/" + "jsons.txt", 'w', encoding="utf-8")
                for json in jsons_new:
                    fl.write(json + '\n')
                fl.close()
        # Wird das Programm das erste Mal ausgeführt, werden die vorhandenen json-Dateien
        # in jsons.txt geschrieben
        else:
            fl = open(directory + "/" + "jsons.txt", 'w', encoding="utf-8")
            for json in jsons:
                fl.write(json + '\n')
                jsons_new.append(json)
            fl.close()
        # Es wird in über die json-Dateien geloopt, in der Reihenfolge, wie sie in jsons.txt stehen
        # Dabei werden jsons aus vorherigen Programmaufrufen zuerst verwendet, da diese dann nicht erneut
        # in die tsv-Dateien geschrieben werden
        for f in jsons_new:
            self.read(directory, f)
        # Die tsv-Dateien mit den einzigartigen Einträgen und die id1_id2-tsv-Datei werden erstellt
        # nachdem alle anderen tsv-Dateien erzeugt wurden
        self.former.make_key_files(directory)

    """ Wenn die Datei eine json-Datei ist, wird sie geparsed.
        Anschließend werden ihre Daten in eine tsv-Datei geschrieben.
        directory: Das Verzeichnis in dem die Datei 'f' liegt.
        f: Die Datei die geparsed und in tsv-Form geschrieben werden soll. """

    def read(self, directory, f):
        if (f.endswith('.json')):
            data = self.parser.parse(directory + '/' + f)
            self.former.to_tsv(data, directory)


class former:
    def __init__(self, parser):
        self.tsv_path = {}
        self.tsv_header = {}
        self.lists = {}
        self.parser = parser
        self.caers_reaction_keys = []
        self.caers_product_keys = []
        self.caers_keys = []
        self.caers_reaction_list = []
        self.caers_product_list = []
        self.caers_list = []
        self.caers_id = [1]
        self.caers_is_id = [0]
        self.drugadverseevent_reaction_keys = []
        self.drugadverseevent_drug_keys = []
        self.drugadverseevent_drug_indication_keys = []
        self.drugadverseevent_drug_openfda_keys = []
        self.drugadverseevent_keys = []
        self.drugadverseevent_reaction_list = []
        self.drugadverseevent_drug_list = []
        self.drugadverseevent_drug_indication_list = []
        self.drugadverseevent_drug_openfda_list = []
        self.drugadverseevent_list = []
        self.drugadverseevent_id = [1]
        self.drugadverseevent_is_id = [0]
        self.drugrecallenforcementreports_openfda_keys = []
        self.drugrecallenforcementreports_keys = []
        self.drugrecallenforcementreports_openfda_list = []
        self.drugrecallenforcementreports_list = []
        self.drugrecallenforcementreports_id = [1]
        self.drugrecallenforcementreports_is_id = [0]
        self.foodrecallenforcementreports_keys = []
        self.foodrecallenforcementreports_list = []
        self.foodrecallenforcementreports_id = [1]
        self.foodrecallenforcementreports_is_id = [0]
        self.nationaldrugcodedirectory_activeingredients_keys = []
        self.nationaldrugcodedirectory_keys = []
        self.nationaldrugcodedirectory_activeingredients_list = []
        self.nationaldrugcodedirectory_list = []
        self.nationaldrugcodedirectory_id = [1]
        self.nationaldrugcodedirectory_is_id = [0]
        self.substancedata_relationships_keys = []
        self.substancedata_relationships_substance_keys = []
        self.substancedata_moieties_keys = []
        self.substancedata_mixture_keys = []
        self.substancedata_component_keys = []
        self.substancedata_names_keys = []
        self.substancedata_substance_keys = []
        self.substancedata_keys = []
        self.substancedata_relationships_list = []
        self.substancedata_relationships_substance_list = []
        self.substancedata_moieties_list = []
        self.substancedata_mixture_list = []
        self.substancedata_component_list = []
        self.substancedata_names_list = []
        self.substancedata_substance_list = []
        self.substancedata_list = []
        self.substancedata_id = [1]
        self.substancedata_is_id = [0]
        # Überprüft, ob neue Einträge für die jeweilige Kategorie hinzugekommen sind
        # Andernfalls wird make_files nicht ausgeführt
        self.changed = False

    """ Trimmet einen String.
        s: Der zu trimmende String. """

    def trim(self, s):
        return s.replace("\"", "\'").replace("\n", "").replace("\\", "")

    """ Erstellt die Key-Arrays aus den Hadern bereits vorhandener tsv-Dateien.
        keys: Liste mit den Headern einer tsv-Datei.
        tsv: Die tsv-Datei deren Header ausgelesen werden sollen."""

    def make_keys(self, keys, tsv):
        f = open(directory + tsv, 'r', encoding="utf-8")
        csv_reader = csv.reader(f, delimiter='\t')
        header = next(csv_reader)
        header.remove("id")
        for entry in header:
            keys.append(entry.replace("\"", "").replace("\n", ""))
        f.close()

    """ Prüft, welche Einträge Listen enthalten. Benötigt für das spätere Erstellen der cypher-Datei.
        lists: Die Liste welche alle Attribute enthält, die als Listen gespeichert sind.
        tsv_: Die tsv-Datei die nach Listen-Attributen durchsucht wird. """

    def make_lists(self, lists, tsv_):
        f = open(directory + tsv_, 'r', encoding="utf-8")
        csv_reader = csv.reader(f, delimiter='\t')
        header = next(csv_reader)
        for entry in csv_reader:
            for i in range(len(entry)):
                if '|' in entry[i]:
                    if header[i] not in lists:
                        lists.append(header[i])
        f.close()

    """ Erstellt die ids-Dateien und die der Oberthemen.
        directory: Das Verzeichnis in dem die tsv-Dateien gespeichert werden.
        dicts: Die Einträge der json-Datei als Dictionary.
        entries: Die Attribute der einzelnen Kategorien die erstellt werden. """

    def make_files(self, directory, dicts, entries):
        for entry in entries:
            if not os.path.isfile(directory + entry["tsv"]):
                if "single_header" in entry:
                    entry["keys"].append(entry["single_header"])
                elif "special_remove" in entry:
                    entry["keys"].append(entry["special_remove"])
                else:
                    for dictionary in dicts["results"]:
                        try:
                            if "is_special" in entry:
                                my_dict = []
                                for i in dictionary[entry["one_key"]][entry["two_key"]]:
                                    my_dict.append(i[entry["three_key"]])
                                dictionary = my_dict
                            elif "is_special2" in entry:
                                head_dict = []
                                for i in dictionary[entry["one_key"]]:
                                    head_dict.append(i[entry["two_key"]])
                                dictionary = head_dict
                            elif "is_special3" in entry:
                                head_dict = []
                                x = 0
                                for i in dictionary[entry["one_key"]]:
                                    head_dict.append({})
                                    for j in entry["two_key"]:
                                        head_dict[x][j] = i[j]
                                    x += 1
                                dictionary = head_dict
                            elif "three_key" in entry:
                                dictionary = dictionary[entry["one_key"]][entry["two_key"]][entry["three_key"]]
                            elif "two_key" in entry:
                                dictionary = dictionary[entry["one_key"]][entry["two_key"]]
                            elif "one_key" in entry:
                                dictionary = dictionary[entry["one_key"]]
                            else:
                                dictionary = dictionary
                            if "is_list" in entry:
                                for d in dictionary:
                                    for key in d.keys():
                                        if key not in entry["keys"]:
                                            entry["keys"].append(key)
                            else:
                                for key in dictionary.keys():
                                    if key not in entry["keys"]:
                                        entry["keys"].append(key)
                        except:
                            pass
                header = "\"id\"\t"
                if "remove_keys" in entry:
                    for i in entry["remove_keys"]:
                        try:
                            entry["keys"].remove(i)
                        except BaseException:
                            pass
                try:
                    entry["keys"].remove("id")
                except BaseException:
                    pass
                for key in entry["keys"]:
                    header = header + "\"" + key + "\"" + '\t'
                header = header[:len(header) - 1] + '\n'
                f = open(directory + entry["tsv"], 'w', encoding="utf-8")
                f.write(header)
                f.close()
            elif not entry["keys"]:
                self.make_keys(entry["keys"], entry["tsv"])
                f = open(directory + entry["tsv"], 'r', encoding="utf-8")
                entries[len(entries) - 1]["id"][0] = sum(1 for line in f)
                f.close()
                self.make_lists(entry["lists"], entry["tsv"])
        fields = []
        for dictionary in dicts["results"]:
            entries[len(entries) - 1]["is_id"][0] = entries[len(entries) - 1]["is_id"][0] + 1
            if "DrugAdverseEvents" in directory:
                a = False
                try:
                    for d in dictionary["patient"]["reaction"]:
                        if d["reactionmeddrapt"] == "No adverse event":
                            a = True
                    if len(dictionary["patient"]["drug"]) > 1 and not a:
                        a = True
                except BaseException:
                    a = True
                if a:
                    entries[len(entries) - 1]["id"][0] = entries[len(entries) - 1]["id"][0] + 1
            if entries[len(entries) - 1]["is_id"][0] < entries[len(entries) - 1]["id"][0]:
                continue
            self.changed = True
            identifier = entries[len(entries) - 1]["id"][0]
            head_dict = dictionary
            for entry in entries:
                write = True
                if "DrugAdverseEvents" in directory:
                    try:
                        for d in dictionary["patient"]["reaction"]:
                            if d["reactionmeddrapt"] == "No adverse event":
                                write = False
                        if len(dictionary["patient"]["drug"]) > 1:
                            write = False
                    except BaseException:
                        write = False
                f = open(directory + entry["tsv"], 'a', encoding="utf-8")
                csv_writer = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                        quotechar='')
                try:
                    if "is_special" in entry:
                        head_dict = []
                        for i in dictionary[entry["one_key"]][entry["two_key"]]:
                            head_dict.append(i[entry["three_key"]])
                    elif "is_special2" in entry:
                        head_dict = []
                        for i in dictionary[entry["one_key"]]:
                            head_dict.append(i[entry["two_key"]])
                    elif "is_special3" in entry:
                        head_dict = []
                        x = 0
                        for i in dictionary[entry["one_key"]]:
                            head_dict.append({})
                            for j in entry["two_key"]:
                                head_dict[x][j] = i[j]
                            x += 1
                    elif "three_key" in entry:
                        head_dict = dictionary[entry["one_key"]][entry["two_key"]][entry["three_key"]]
                    elif "two_key" in entry:
                        head_dict = dictionary[entry["one_key"]][entry["two_key"]]
                    elif "one_key" in entry:
                        head_dict = dictionary[entry["one_key"]]
                    elif "is_single" in entry:
                        head_dict = dictionary[entry["single_header"]]
                    else:
                        head_dict = dictionary
                    if "is_single" in entry:
                        for d in head_dict:
                            fields.append("\"" + str(identifier) + "\"")
                            if len(d) < 2000000:
                                fields.append("\"" + self.trim(str(d)) + "\"")
                            else:
                                fields.append("")
                            for i in range(len(fields)):
                                fields[i] = fields[i].replace("\"\"", "").replace("\"[]\"", "").replace("\"{}\"",
                                                                                                        "").replace(
                                    "\t", " ")
                            if write:
                                csv_writer.writerow(fields)
                            fields = []
                    elif "is_list" in entry:
                        for d in head_dict:
                            fields.append("\"" + str(identifier) + "\"")
                            for key in entry["keys"]:
                                if key in d and len(str(d[key])) < 2000000:
                                    if isinstance(d[key], list):
                                        length = len(d[key])
                                        d[key] = [str(entry).replace("|", "") for entry in d[key]]
                                        d[key] = "|".join(str(elem) for elem in d[key])
                                        if key not in entry["lists"] and length > 1:
                                            entry["lists"].append(key)
                                    elif isinstance(d[key], dict):
                                        d[key] = json.dumps(d[key])
                                        d[key] = d[key].replace("|", "")
                                    else:
                                        d[key] = str(d[key]).replace("|", "")
                                    fields.append("\"" + self.trim(str(d[key])) + "\"")
                                else:
                                    fields.append("")
                            for i in range(len(fields)):
                                fields[i] = fields[i].replace("\"\"", "").replace("\"[]\"", "").replace("\"{}\"",
                                                                                                        "").replace(
                                    "\t", " ")
                            if write:
                                csv_writer.writerow(fields)
                            fields = []
                    elif "is_head" in entry:
                        fields.append("\"" + str(identifier) + "\"")
                        for key in entry["keys"]:
                            if key in head_dict.keys() and len(str(head_dict[key])) < 2000000:
                                if isinstance(head_dict[key], list):
                                    length = len(head_dict[key])
                                    head_dict[key] = [str(entry).replace("|", "") for entry in head_dict[key]]
                                    head_dict[key] = "|".join(str(elem) for elem in head_dict[key])
                                    if key not in entry["lists"] and length > 1:
                                        entry["lists"].append(key)
                                elif isinstance(head_dict[key], dict):

                                    if entry["name"] == "DrugAdverseEvent":
                                        if key == "patient":
                                            try:
                                                del head_dict[key]["reaction"]
                                                del head_dict[key]["drug"]
                                            except BaseException:
                                                pass
                                    head_dict[key] = json.dumps(head_dict[key])
                                    head_dict[key] = head_dict[key].replace("|", "")
                                else:
                                    head_dict[key] = str(head_dict[key]).replace("|", "")
                                fields.append("\"" + self.trim(str(head_dict[key])) + "\"")
                            else:
                                fields.append("")
                        for i in range(len(fields)):
                            fields[i] = fields[i].replace("\"\"", "").replace("\"[]\"", "").replace("\"{}\"",
                                                                                                    "").replace("\t",
                                                                                                                " ")
                        if write:
                            csv_writer.writerow(fields)
                except BaseException:
                    pass
                f.close()
                fields = []
            entries[len(entries) - 1]["id"][0] += 1

        for entry in entries:
            if isinstance(entry["keys"], str):
                entry["keys"] = [entry["keys"]]
            if not entry["name"] in tsv_paths:
                self.tsv_path[entry["name"]] = directory + entry["tsv"]
            if not entry["name"] in tsv_headers:
                self.tsv_header[entry["name"]] = ["id"] + entry["keys"]
            self.lists[entry["list_name"]] = entry["lists"]

    """ Erstellt die unique-Dateien und die id1-id2-Dateien.
        directory: Das Verzeichnis in dem die tsv-Dateien liegen und gespeichert werden.
        ids_tsv: Die tsv-Datei die die originalen Einträge aus der json-Datei enthält.
        unique_tsv: Die tsv-Datei die nur die einzigartigen Einträge enthalten wird.
        id1_id2_tsv: Die Datei die die ids zum matchen der Kategorien enthält.
        keys: Die Liste die alle Attribute des Headers der 'ids_tsv'-Datei enthält. """

    def make_unique_files(self, directory, ids_tsv, unique_tsv, id1_id2_tsv, keys):
        if self.changed:
            # Erstellt die Datei mit den einzigartigen Einträgen, indem
            # diese aus der ids-Datei gelesen werden
            f = open(directory + '/' + ids_tsv + '.tsv', 'r', encoding="utf-8")
            reactions = []
            header = f.readline()
            csv_reader = csv.reader(f, delimiter="\t")
            for line in csv_reader:
                line = line[1:]
                for i in range(len(line)):
                    if line[i] != "":
                        line[i] = "\"" + line[i] + "\""
                line = "\t".join(line)
                reactions.append(line)
            f.close()
            reactions = set(reactions)
            if "" in reactions:
                reactions.remove("")
            f = open(directory + '/' + unique_tsv + '.tsv', 'w', encoding="utf-8")
            f.write(header)
            csv_writer = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                    quotechar='')
            identifier = 1
            for entry in reactions:
                csv_writer.writerow(["\"" + str(identifier) + "\""] + str(entry).split("\t"))
                identifier += 1
            f.close()
            # Erstellt die Datei, welche den Haupteintrag mit den einzigartigen Einträgen
            # über ids matched
            f_id = open(directory + '/' + ids_tsv + '.tsv', 'r', encoding="utf-8")
            header = f_id.readline()
            header = ["\"id\"", "\"id2\""]
            csv_reader = csv.reader(f_id, delimiter="\t")
            lines = []
            for line in csv_reader:
                l = line[1:]
                for i in range(len(l)):
                    if l[i] != "":
                        l[i] = "\"" + l[i] + "\""
                l = "\t".join(l)
                if l != "":
                    lines.append([line[0], l])
            f_id.close()
            reactions = list(reactions)
            reactions_dict = {}
            for i in range(len(reactions)):
                reactions_dict[reactions[i]] = i + 1
            f = open(directory + '/' + id1_id2_tsv + '.tsv', 'w', encoding="utf-8")
            csv_writer = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                    quotechar='')
            csv_writer.writerow(header)
            # id1 ist die id des Haupteintrags
            # id2 ist die id des einzigartigen Eintrags
            for line in lines:
                id1 = line[0]
                id2 = reactions_dict[line[1]]
                csv_writer.writerow([str(id1), "\"" + str(id2) + "\""])
            f.close()
        if unique_tsv not in self.tsv_path:
            self.tsv_path[unique_tsv] = directory + '/' + unique_tsv + '.tsv'
        if unique_tsv not in self.tsv_header:
            self.tsv_header[unique_tsv] = ["id"] + keys
        if id1_id2_tsv not in self.tsv_path:
            self.tsv_path[id1_id2_tsv] = directory + '/' + id1_id2_tsv + '.tsv'
        if id1_id2_tsv not in self.tsv_header:
            self.tsv_header[id1_id2_tsv] = ["id1", "id2"]

    """ Erstellt speziell die Dateien die zwei ids brauchen.
        Das sind jene, die als Kanten genutzt werden.
        directory: Das Verzeichnis in dem die tsv-Dateien liegen und gespeichert werden.
        category: Die ids-Datei mit den originalen Einträgen.
        name: Der Name der Datei in der die _id1_id2 ids zum matchen der Kategorien gespeichert sind."""

    def make_id_files(self, directory, category, name):
        f1 = open(directory + '/' + category + ".tsv", 'r', encoding="utf-8")
        f2 = open(directory + '/' + name + ".tsv", 'w', encoding="utf-8")
        header = f1.readline()
        csv_reader = csv.reader(f1, delimiter="\t")
        csv_writer = csv.writer(f2, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                quotechar='')
        header = ["\"id\"", "\"id2\""]
        csv_writer.writerow(header)
        identifier = 1
        for line in csv_reader:
            line = "\"" + line[0] + "\""
            csv_writer.writerow([line, "\"" + str(identifier) + "\""])
            identifier += 1
        f1.close()
        f2.close()
        if name not in self.tsv_path:
            self.tsv_path[name] = directory + '/' + name + '.tsv'

    """ Erstellt speziell die Dateien die eine id brauchen.
        directory: Das Verzeichnis in dem die tsv-Dateien liegen und gespeichert werden.
        category: Die ids-Datei mit den originalen Einträgen.
        name: Die tsv-Dateien die die Einträge aus den ids-Dateien enthalten, aber neue, einzigartige ids bekommen.
        keys: Die Liste die alle Attribute des Headers der 'ids_tsv'-Datei enthält. """

    def make_special_files(self, directory, category, name, keys):
        f1 = open(directory + '/' + category + ".tsv", 'r', encoding="utf-8")
        f2 = open(directory + '/' + name + ".tsv", 'w', encoding="utf-8")
        header = f1.readline()
        f2.write(header)
        csv_reader = csv.reader(f1, delimiter="\t")
        csv_writer = csv.writer(f2, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                quotechar='')
        identifier = 1
        for line in csv_reader:
            csv_writer.writerow(["\"" + str(identifier) + "\""] + line[1:])
            identifier += 1
        f1.close()
        f2.close()
        if name not in self.tsv_path:
            self.tsv_path[name] = directory + '/' + name + '.tsv'
        if name not in self.tsv_header:
            self.tsv_header[name] = ["id"] + keys

    """ Erstellt eine Datei über die zwei Knoten in neo4j gematcht werden. """

    def make_match_file(self, directory, category, name):
        f1 = open(directory + '/' + category + ".tsv", 'r', encoding="utf-8")
        f2 = open(directory + '/' + name + ".tsv", 'w', encoding="utf-8")
        header = f1.readline()
        csv_reader = csv.reader(f1, delimiter="\t")
        csv_writer = csv.writer(f2, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                quotechar='')
        header = ["\"id\"", "\"id2\""]
        csv_writer.writerow(header)
        for line in csv_reader:
            csv_writer.writerow(["\"" + line[0] + "\""] + ["\"" + line[0] + "\""])
        f1.close()
        f2.close()
        if name not in self.tsv_path:
            self.tsv_path[name] = directory + '/' + name + '.tsv'
        if name not in self.tsv_header:
            self.tsv_header[name] = ["id1", "id2"]

    """ Spezielle Funktion zu Erstellen der DrugAdverseEvent_drug_openfda.tsv.
        directory: Das Verzeichnis für DrugAdverseEvents.
        openfda: Die openfda_ids-Datei.
        drug_ids: Die drug_ids-Datei.
        id1_id2: Die Datei zum matchen der openfdas mit den drugs. """

    def make_openfda_file(self, directory, openfda, drug_ids, id1_id2, name, keys):
        f = open(directory + '/' + openfda + ".tsv", 'r', encoding="utf-8")
        header = f.readline()
        csv_reader = csv.reader(f, delimiter="\t")
        fda = []
        fda_dict = {}
        count_unique = 1
        for line in csv_reader:
            l = line[1:]
            for i in range(len(l)):
                if l[i] != "":
                    l[i] = "\"" + l[i] + "\""
            l = "\t".join(l)
            if l not in fda_dict:
                fda_dict[l] = count_unique
                count_unique += 1
            fda.append(["\"" + line[0] + "\"", fda_dict[l]])
        f.close()
        fda_dict_new = {}
        for entry in fda_dict:
            fda_dict_new[fda_dict[entry]] = entry
        f = open(directory + '/' + name + ".tsv", 'w', encoding="utf-8")
        f.write(header)
        for i in range(len(fda_dict_new)):
            f.write("\"" + str(i + 1) + "\"" + '\t' + str(fda_dict_new[i + 1]) + '\n')
        f.close()
        f = open(directory + '/' + drug_ids + ".tsv", 'r', encoding="utf-8")
        header = f.readline()
        csv_reader = csv.reader(f, delimiter="\t")
        drugs = []
        for line in csv_reader:
            drugs.append("\"" + line[0] + "\"")
        f = open(directory + '/' + id1_id2 + ".tsv", 'w', encoding="utf-8")
        csv_writer = csv.writer(f, delimiter='\t', lineterminator='\n', quoting=csv.QUOTE_NONE, escapechar='',
                                quotechar='')
        csv_writer.writerow(["\"id\"", "\"id2\""])
        j = 0
        count = 0
        for entry in drugs:
            count += 1
            try:
                if fda[j][0] == entry:
                    csv_writer.writerow(["\"" + str(count) + "\"", "\"" + str(fda[j][1]) + "\""])
                    j += 1
            except BaseException:
                pass
        f.close()
        if id1_id2 not in self.tsv_path:
            self.tsv_path[id1_id2] = directory + '/' + id1_id2 + '.tsv'
        if name not in self.tsv_path:
            self.tsv_path[name] = directory + '/' + name + '.tsv'
        if name not in self.tsv_header:
            self.tsv_header[name] = ["id"] + keys

    """ Erstellt die Dateien, die nur einzigartige Einträge enthalten.
        directory: Das jeweilige Verzeichnis. """

    def make_key_files(self, directory):
        if ("CAERSReports" in directory):
            self.make_unique_files(directory, "CAERSReport_reaction_ids", "CAERSReport_reaction",
                                   "CAERSReport_reaction_id1_id2", self.caers_reaction_keys)
            self.make_unique_files(directory, "CAERSReport_product_ids", "CAERSReport_product",
                                   "CAERSReport_product_id1_id2", self.caers_product_keys)

        if ("DrugAdverseEvents" in directory):
            self.make_unique_files(directory, "DrugAdverseEvent_reaction_ids", "DrugAdverseEvent_reaction",
                                   "DrugAdverseEvent_reaction_id1_id2", self.drugadverseevent_reaction_keys)
            self.make_id_files(directory, "DrugAdverseEvent_drug_ids", "DrugAdverseEvent_drug_id1_id2")
            self.make_special_files(directory, "DrugAdverseEvent_drug_ids", "DrugAdverseEvent_drug",
                                    self.drugadverseevent_drug_keys)
            self.make_openfda_file(directory, "DrugAdverseEvent_drug_indication_ids", "DrugAdverseEvent_drug_ids",
                                   "DrugAdverseEvent_drug_indication_id1_id2", "DrugAdverseEvent_drug_indication",
                                   self.drugadverseevent_drug_indication_keys)
            self.make_openfda_file(directory, "DrugAdverseEvent_drug_openfda_ids", "DrugAdverseEvent_drug_ids",
                                   "DrugAdverseEvent_drug_openfda_id1_id2", "DrugAdverseEvent_drug_openfda",
                                   self.drugadverseevent_drug_openfda_keys)

        if ("DrugRecallEnforcementReports" in directory):
            self.make_unique_files(directory, "DrugRecallEnforcementReport_openfda_ids",
                                   "DrugRecallEnforcementReport_openfda", "DrugRecallEnforcementReport_openfda_id1_id2",
                                   self.drugrecallenforcementreports_openfda_keys)

        if ("NationalDrugCodeDirectory" in directory):
            self.make_unique_files(directory, "NationalDrugCodeDirectory_activeingredients_ids",
                                   "NationalDrugCodeDirectory_activeingredients",
                                   "NationalDrugCodeDirectory_activeingredients_id1_id2",
                                   self.nationaldrugcodedirectory_activeingredients_keys)

        if ("SubstanceData" in directory):
            self.make_unique_files(directory, "SubstanceData_moieties_ids", "SubstanceData_moieties",
                                   "SubstanceData_moieties_id1_id2", self.substancedata_moieties_keys)
            self.make_id_files(directory, "SubstanceData_substance_ids", "SubstanceData_substance_id1_id2")
            self.make_special_files(directory, "SubstanceData_substance_ids", "SubstanceData_substance",
                                    self.substancedata_substance_keys)
            self.make_special_files(directory, "SubstanceData_component_ids", "SubstanceData_component",
                                    self.substancedata_component_keys)
            self.make_special_files(directory, "SubstanceData_names_ids", "SubstanceData_names",
                                    self.substancedata_names_keys)
            self.make_special_files(directory, "SubstanceData_relationships_ids", "SubstanceData_relationships",
                                    self.substancedata_relationships_keys)
            self.make_special_files(directory, "SubstanceData_relationships_substance_ids",
                                    "SubstanceData_relationships_substance",
                                    self.substancedata_relationships_substance_keys)

        self.changed = False

    """ Überprüft erst, welche Kategorie über Dictionary gegeben ist.
        Filtert die Keys aus den Daten und schreibt sie als Header in eine tsv-Datei.
        Anschließend wird jeder Eintrag der Datei in die tsv-Datei geschrieben.
        Vor jeden Eintrag wird eine ID gesetzt.
        Die Keys, sowie die Dateipfade werden zum Erstellen der cypher-Datei gespeichert.
        dicts: Der Inhalt einer json-Datei als Dictionary.
        directory: Das jeweilige Verzeichnis. """

    def to_tsv(self, dicts, directory):
        # Zuerst wird geprüft, um welche Kategorie es sich handelt.
        print("Creating tsv ...")
        if ("CAERSReports" in directory):
            caersreport_reaction = {
                "name": "CAERSReport_reaction_ids",
                "list_name": "CAERSReport_reaction",
                "tsv": "/CAERSReport_reaction_ids.tsv",
                "keys": self.caers_reaction_keys,
                "single_header": "reactions",
                "is_single": True,
                "id": self.caers_id,
                "is_id": self.caers_is_id,
                "is_list": True,
                "lists": self.caers_reaction_list
            }
            caersreport_product = {
                "name": "CAERSReport_product_ids",
                "list_name": "CAERSReport_product",
                "tsv": "/CAERSReport_product_ids.tsv",
                "keys": self.caers_product_keys,
                "one_key": "products",
                "is_list": True,
                "id": self.caers_id,
                "is_id": self.caers_is_id,
                "lists": self.caers_product_list
            }
            caersreport = {
                "name": "CAERSReport",
                "list_name": "CAERSReport",
                "tsv": "/CAERSReport.tsv",
                "keys": self.caers_keys,
                "remove_keys": ["reactions", "products"],
                "id": self.caers_id,
                "is_id": self.caers_is_id,
                "is_head": True,
                "lists": self.caers_list
            }
            entries = [caersreport_reaction, caersreport_product, caersreport]
            self.make_files(directory, dicts, entries)

        if ("DrugAdverseEvents" in directory):
            drugadverseevent_reaction = {
                "name": "DrugAdverseEvent_reaction_ids",
                "list_name": "DrugAdverseEvent_reaction",
                "tsv": "/DrugAdverseEvent_reaction_ids.tsv",
                "keys": self.drugadverseevent_reaction_keys,
                "one_key": "patient",
                "two_key": "reaction",
                "is_list": True,
                "id": self.drugadverseevent_id,
                "is_id": self.drugadverseevent_is_id,
                "lists": self.drugadverseevent_reaction_list
            }
            drugadverseevent_drug = {
                "name": "DrugAdverseEvent_drug_ids",
                "list_name": "DrugAdverseEvent_drug",
                "tsv": "/DrugAdverseEvent_drug_ids.tsv",
                "keys": self.drugadverseevent_drug_keys,
                "remove_keys": ["openfda", "drugindication"],
                "one_key": "patient",
                "two_key": "drug",
                "is_list": True,
                "id": self.drugadverseevent_id,
                "is_id": self.drugadverseevent_is_id,
                "lists": self.drugadverseevent_drug_list
            }
            drugadverseevent_drug_indication = {
                "name": "DrugAdverseEvent_drug_indication_ids",
                "list_name": "DrugAdverseEvent_drug_indication",
                "tsv": "/DrugAdverseEvent_drug_indication_ids.tsv",
                "keys": self.drugadverseevent_drug_indication_keys,
                "one_key": "patient",
                "two_key": "drug",
                "is_list": True,
                "special_remove": "drugindication",
                "id": self.drugadverseevent_id,
                "is_id": self.drugadverseevent_is_id,
                "lists": self.drugadverseevent_drug_indication_list
            }
            drugadverseevent_drug_openfda = {
                "name": "DrugAdverseEvent_drug_openfda_ids",
                "list_name": "DrugAdverseEvent_drug_openfda",
                "tsv": "/DrugAdverseEvent_drug_openfda_ids.tsv",
                "keys": self.drugadverseevent_drug_openfda_keys,
                "one_key": "patient",
                "two_key": "drug",
                "three_key": "openfda",
                "is_special": True,
                "is_list": True,
                "id": self.drugadverseevent_id,
                "is_id": self.drugadverseevent_is_id,
                "lists": self.drugadverseevent_drug_openfda_list
            }
            drugadverseevent = {
                "name": "DrugAdverseEvent",
                "list_name": "DrugAdverseEvent",
                "tsv": "/DrugAdverseEvent.tsv",
                "keys": self.drugadverseevent_keys,
                "remove_keys": ["reaction", "drug"],
                "id": self.drugadverseevent_id,
                "is_id": self.drugadverseevent_is_id,
                "is_head": True,
                "lists": self.drugadverseevent_list
            }
            entries = [drugadverseevent_reaction, drugadverseevent_drug, drugadverseevent_drug_indication,
                       drugadverseevent_drug_openfda, drugadverseevent]
            self.make_files(directory, dicts, entries)

        if ("DrugRecallEnforcementReports" in directory):
            drugrecallenforcementreport_openfda = {
                "name": "DrugRecallEnforcementReport_openfda_ids",
                "list_name": "DrugRecallEnforcementReport_openfda",
                "tsv": "/DrugRecallEnforcementReport_openfda_ids.tsv",
                "keys": self.drugrecallenforcementreports_openfda_keys,
                "one_key": "openfda",
                "id": self.drugrecallenforcementreports_id,
                "is_id": self.drugrecallenforcementreports_is_id,
                "is_head": True,
                "lists": self.drugrecallenforcementreports_openfda_list
            }
            drugrecallenforcementreport = {
                "name": "DrugRecallEnforcementReport",
                "list_name": "DrugRecallEnforcementReport",
                "tsv": "/DrugRecallEnforcementReport.tsv",
                "keys": self.drugrecallenforcementreports_keys,
                "remove_keys": ["openfda"],
                "id": self.drugrecallenforcementreports_id,
                "is_id": self.drugrecallenforcementreports_is_id,
                "is_head": True,
                "lists": self.drugrecallenforcementreports_list
            }
            entries = [drugrecallenforcementreport_openfda, drugrecallenforcementreport]
            self.make_files(directory, dicts, entries)

        if ("FoodRecallEnforcementReports" in directory):
            foodrecallenforcementreport = {
                "name": "FoodRecallEnforcementReport",
                "list_name": "FoodRecallEnforcementReport",
                "tsv": "/FoodRecallEnforcementReport.tsv",
                "keys": self.foodrecallenforcementreports_keys,
                "id": self.foodrecallenforcementreports_id,
                "is_id": self.foodrecallenforcementreports_is_id,
                "is_head": True,
                "lists": self.foodrecallenforcementreports_list
            }
            entries = [foodrecallenforcementreport]
            self.make_files(directory, dicts, entries)

        if ("NationalDrugCodeDirectory" in directory):
            nationaldrugcodedirectory_activeingredients = {
                "name": "NationalDrugCodeDirectory_activeingredients_ids",
                "list_name": "NationalDrugCodeDirectory_activeingredients",
                "tsv": "/NationalDrugCodeDirectory_activeingredients_ids.tsv",
                "keys": self.nationaldrugcodedirectory_activeingredients_keys,
                "one_key": "active_ingredients",
                "is_list": True,
                "id": self.nationaldrugcodedirectory_id,
                "is_id": self.nationaldrugcodedirectory_is_id,
                "lists": self.nationaldrugcodedirectory_activeingredients_list
            }
            nationaldrugcodedirectory = {
                "name": "NationalDrugCodeDirectory",
                "list_name": "NationalDrugCodeDirectory",
                "tsv": "/NationalDrugCodeDirectory.tsv",
                "keys": self.nationaldrugcodedirectory_keys,
                "remove_keys": ["active_ingredients"],
                "id": self.nationaldrugcodedirectory_id,
                "is_id": self.nationaldrugcodedirectory_is_id,
                "is_head": True,
                "lists": self.nationaldrugcodedirectory_list
            }
            entries = [nationaldrugcodedirectory_activeingredients, nationaldrugcodedirectory]
            self.make_files(directory, dicts, entries)

        if ("SubstanceData" in directory):
            substancedata_relationships = {
                "name": "SubstanceData_relationships_ids",
                "list_name": "SubstanceData_relationships",
                "tsv": "/SubstanceData_relationships_ids.tsv",
                "keys": self.substancedata_relationships_keys,
                "remove_keys": ["related_substance"],
                "one_key": "relationships",
                "is_list": True,
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "lists": self.substancedata_relationships_list
            }
            substancedata_relationships_substance = {
                "name": "SubstanceData_relationships_substance_ids",
                "list_name": "SubstanceData_relationships_substance",
                "tsv": "/SubstanceData_relationships_substance_ids.tsv",
                "keys": self.substancedata_relationships_substance_keys,
                "one_key": "relationships",
                "two_key": "related_substance",
                "is_list": True,
                "is_special2": True,
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "lists": self.substancedata_relationships_substance_list
            }
            substancedata_moieties = {
                "name": "SubstanceData_moieties_ids",
                "list_name": "SubstanceData_moieties",
                "tsv": "/SubstanceData_moieties_ids.tsv",
                "keys": self.substancedata_moieties_keys,
                "one_key": "moieties",
                "is_list": True,
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "lists": self.substancedata_moieties_list
            }
            substancedata_mixture = {
                "name": "SubstanceData_mixture",
                "list_name": "SubstanceData_mixture",
                "tsv": "/SubstanceData_mixture.tsv",
                "keys": self.substancedata_mixture_keys,
                "remove_keys": ["components"],
                "one_key": "mixture",
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "is_head": True,
                "lists": self.substancedata_mixture_list
            }
            substancedata_component = {
                "name": "SubstanceData_components_ids",
                "list_name": "SubstanceData_component",
                "tsv": "/SubstanceData_component_ids.tsv",
                "keys": self.substancedata_component_keys,
                "remove_keys": ["substance"],
                "one_key": "mixture",
                "two_key": "components",
                "is_list": True,
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "is_head": True,
                "lists": self.substancedata_component_list
            }
            substancedata_names = {
                "name": "SubstanceData_names_ids",
                "list_name": "SubstanceData_names",
                "tsv": "/SubstanceData_names_ids.tsv",
                "keys": self.substancedata_names_keys,
                "one_key": "names",
                "is_list": True,
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "lists": self.substancedata_names_list
            }
            substancedata_substance = {
                "name": "SubstanceData_substance_ids",
                "list_name": "SubstanceData_substance",
                "tsv": "/SubstanceData_substance_ids.tsv",
                "keys": self.substancedata_substance_keys,
                "one_key": "mixture",
                "two_key": "components",
                "three_key": "substance",
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "is_list": True,
                "lists": self.substancedata_substance_list,
                "is_special": True
            }
            substancedata = {
                "name": "SubstanceData",
                "list_name": "SubstanceData",
                "tsv": "/SubstanceData.tsv",
                "keys": self.substancedata_keys,
                "remove_keys": ["relationships", "moieties", "mixture", "names"],
                "id": self.substancedata_id,
                "is_id": self.substancedata_is_id,
                "is_head": True,
                "lists": self.substancedata_list
            }
            entries = [substancedata_relationships, substancedata_relationships_substance, substancedata_moieties,
                       substancedata_mixture, substancedata_component, substancedata_names, substancedata_substance,
                       substancedata]
            self.make_files(directory, dicts, entries)

    def remove_lists(self):
        self.__init__(self.parser)


class cypher_creator:

    def __init__(self):
        self.script = ""
        self.cypher_path = ""

    """ Erstellt einen neuen Knoten.
        file_path: Das Dict mit den Dateipfaden.
        header: Das Dict mit den Knoten-Attributen.
        name: Der Name der Datei aus der die Knoten erstellt werden sollen.
        lists: Dict von Attributen die als Liste gespeichert werden sollen. """

    def create(self, file_path, header, name, node_name, lists):
        statement = "USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM 'file:///" + \
                    str(file_path[name]).replace('\\', '/') + "' AS row FIELDTERMINATOR '\\t' CREATE "
        obj = "(" + node_name + \
              ":" + node_name + " "
        attributes = "{"
        for head in header[name]:
            if head not in lists[name]:
                attributes = attributes + \
                             str(head).replace("\"", "") + ": row." + str(head).replace("\"", "") + ", "
            else:
                attributes = attributes + \
                             str(head).replace("\"", "") + ": split(row." + str(head).replace("\"", "") + ",'|')" + ", "
        attributes = attributes[:len(attributes) - 2] + "}"
        statement = statement + obj + attributes + ");" + '\n'
        f = open(self.cypher_path, 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Erstellt einen neuen Constraint.
        name1: Name des Constraints.
        name2: Name des Knotens.
        id1: Attribut auf das der Constraint erzeugt werden soll. """

    def constraint(self, name1, name2, id1):
        statement = "CREATE CONSTRAINT " + name1 + " IF NOT EXISTS ON (n: " + name2 + ") ASSERT n." + str(
            id1) + " IS UNIQUE;"
        statement = statement + '\n'
        f = open(self.cypher_path, 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Matched zwei Knoten 'n' -> 'm'.
        name1: Name des Knotens 'n'.
        name2: Name des Knotens 'm'.
        id1: 'n' id.
        id2: 'm' id. """

    def match(self, name1, name2, id1, id2):
        statement = "MATCH (n: " + name1 + "), (m: " + name2 + ") WHERE n." + id1 + " = m." + id2 + " CREATE (n)-[:Event]->(m);"
        statement = statement + '\n'
        f = open(self.cypher_path, 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Setzt Kantenattribute für Kante 'n' -> 'm'.
        file_path: Das Dict mit den Dateipfaden.
        header: Das Dict mit den Knoten-Attributen.
        lists: Dict von Attributen die als Liste gespeichert werden sollen.
        name: Name der Datei aus der die Kanten-Attribute ausgelesen werden sollen.
        name1: Name des Knotens 'n'.
        name2: Name des Knotens 'm'.
        id1: 'n' id.
        id2: Id in der Kanten-Datei. """

    def set_properties(self, file_path, header, lists, name, name1, name2, id1, id2):
        statement = "USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM 'file:///" + \
                    str(file_path[name]).replace('\\', '/') + "'AS row FIELDTERMINATOR '\\t'"
        obj = " MATCH (n:" + name1 + ")-[e:Event]->(m:" + name2 + ")"
        obj2 = " WHERE n." + str(id1) + " = row." + str(id2)
        obj3 = " SET e = "
        attributes = "{"
        for head in header[name]:
            if head not in lists[name]:
                attributes = attributes + \
                             str(head).replace("\"", "") + ": row." + str(head).replace("\"", "") + ", "
            else:
                attributes = attributes + \
                             str(head).replace("\"", "") + ": split(row." + str(head).replace("\"", "") + ",'|')" + ", "
        attributes = attributes[:len(attributes) - 2] + "};"
        statement = statement + obj + obj2 + obj3 + attributes + '\n'
        f = open(self.cypher_path, 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Matched zwei Knoten über ids in einer Datei.
        file_path: Das Dict mit den Dateipfaden.
        name: Name der Datei in der die ids stehen.
        name1: Name des Knotens 'n'.
        name2: Name des Knotens 'm'. """

    def match_from_file(self, file_path, name, name1, name2):
        statement = "USING PERIODIC COMMIT 1000 LOAD CSV WITH HEADERS FROM 'file:///" + \
                    str(file_path[name]).replace('\\', '/') + "' AS row FIELDTERMINATOR '\\t'"
        obj = " MATCH (n:" + name1 + "), (m:" + name2 + ") WHERE n." + "id" + " = row." + "id2 AND m." + "id" + " = row." + "id"
        statement = statement + obj + " CREATE (n)-[:Event]->(m);" + '\n'
        f = open(self.cypher_path, 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Überprüft über Directory, welche Kategorie gegeben ist.
        Anschließend werden die jeweiligen Knoten, Constraints und Merges erstellt.
        file_path: Das Dict mit den Dateipfaden.
        header: Das Dict mit den Knoten-Attributen.
        directory: Das Verzeichnis.
        lists: Dict von Attributen die als Liste gespeichert werden sollen. """

    def create_cypher(self, file_path, header, directory, lists):
        print("Creating Cypher-File ...")
        self.cypher_path = os.path.split(directory)[0] + '/' + "load-cypher.cypher"
        # Hier werden die vorher gespeicherten Dictionaries mit den Dateipfaden und
        # Headern verwendet.
        # Die Dateien mit _id1_id2 enthalten nur die IDs zum matchen der Haupteinträge
        # mit den Untereinträgen
        if "CAERSReports" in directory:
            self.create(file_path, header, "CAERSReport_reaction", "CAERSReport_reaction_openFDA", lists)
            self.create(file_path, header, "CAERSReport_product", "CAERSReport_product_openFDA", lists)
            self.create(file_path, header, "CAERSReport", "CAERSReport_openFDA", lists)
            self.constraint("CAERSReport_openFDA_constraint", "CAERSReport_openFDA", "id")
            self.constraint("CAERSReport_reaction_openFDA_constraint", "CAERSReport_reaction_openFDA", "id")
            self.constraint("CAERSReport_product_openFDA_constraint", "CAERSReport_product_openFDA", "id")
            self.match_from_file(file_path, "CAERSReport_reaction_id1_id2", "CAERSReport_reaction_openFDA",
                                 "CAERSReport_openFDA")
            self.match_from_file(file_path, "CAERSReport_product_id1_id2", "CAERSReport_product_openFDA",
                                 "CAERSReport_openFDA")

        if "DrugAdverseEvents" in directory:
            self.create(file_path, header, "DrugAdverseEvent_reaction", "DrugAdverseEvent_reaction_openFDA", lists)
            self.create(file_path, header, "DrugAdverseEvent_drug", "DrugAdverseEvent_drug_openFDA", lists)
            self.create(file_path, header, "DrugAdverseEvent_drug_indication",
                        "DrugAdverseEvent_drug_indication_openFDA", lists)
            self.create(file_path, header, "DrugAdverseEvent_drug_openfda", "DrugAdverseEvent_drug_openfda_openFDA",
                        lists)
            self.create(file_path, header, "DrugAdverseEvent", "DrugAdverseEvent_openFDA", lists)
            self.constraint("DrugAdverseEvent_openFDA_constraint", "DrugAdverseEvent_openFDA", "id")
            self.constraint("DrugAdverseEvent_reaction_openFDA_constraint", "DrugAdverseEvent_reaction_openFDA", "id")
            self.constraint("DrugAdverseEvent_drug_openFDA_constraint", "DrugAdverseEvent_drug_openFDA", "id")
            self.constraint("DrugAdverseEvent_drug_indication_openFDA_constraint",
                            "DrugAdverseEvent_drug_indication_openFDA", "id")
            self.constraint("DrugAdverseEvent_drug_openfda_openFDA_constraint", "DrugAdverseEvent_drug_openfda_openFDA",
                            "id")
            self.match_from_file(file_path, "DrugAdverseEvent_drug_id1_id2", "DrugAdverseEvent_drug_openFDA",
                                 "DrugAdverseEvent_openFDA")
            self.match_from_file(file_path, "DrugAdverseEvent_reaction_id1_id2", "DrugAdverseEvent_reaction_openFDA",
                                 "DrugAdverseEvent_openFDA")
            self.match_from_file(file_path, "DrugAdverseEvent_drug_indication_id1_id2",
                                 "DrugAdverseEvent_drug_indication_openFDA", "DrugAdverseEvent_drug_openFDA")
            self.match_from_file(file_path, "DrugAdverseEvent_drug_openfda_id1_id2",
                                 "DrugAdverseEvent_drug_openfda_openFDA", "DrugAdverseEvent_drug_openFDA")

        if "DrugRecallEnforcementReports" in directory:
            self.create(file_path, header, "DrugRecallEnforcementReport_openfda",
                        "DrugRecallEnforcementReport_openfda_openFDA", lists)
            self.create(file_path, header, "DrugRecallEnforcementReport", "DrugRecallEnforcementReport_openFDA", lists)
            self.constraint("DrugRecallEnforcementReport_openfda_openFDA_constraint",
                            "DrugRecallEnforcementReport_openfda_openFDA", "id")
            self.constraint("DrugRecallEnforcementReport_openFDA_constraint", "DrugRecallEnforcementReport_openFDA",
                            "id")
            self.match_from_file(file_path, "DrugRecallEnforcementReport_openfda_id1_id2",
                                 "DrugRecallEnforcementReport_openfda_openFDA", "DrugRecallEnforcementReport_openFDA")

        if "FoodRecallEnforcementReports" in directory:
            self.create(file_path, header, "FoodRecallEnforcementReport", "FoodRecallEnforcementReport_openFDA", lists)
            self.constraint("FoodRecallEnforcementReport_openFDA_constraint", "FoodRecallEnforcementReport_openFDA",
                            "id")

        if "NationalDrugCodeDirectory" in directory:
            self.create(file_path, header, "NationalDrugCodeDirectory_activeingredients",
                        "NationalDrugCodeDirectory_activeingredients_openFDA", lists)
            self.create(file_path, header, "NationalDrugCodeDirectory", "NationalDrugCodeDirectory_openFDA", lists)
            self.constraint("NationalDrugCodeDirectory_activeingredients_openFDA_constraint",
                            "NationalDrugCodeDirectory_activeingredients_openFDA", "id")
            self.constraint("NationalDrugCodeDirectory_openFDA_constraint", "NationalDrugCodeDirectory_openFDA", "id")
            self.match_from_file(file_path, "NationalDrugCodeDirectory_activeingredients_id1_id2",
                                 "NationalDrugCodeDirectory_activeingredients_openFDA",
                                 "NationalDrugCodeDirectory_openFDA")

        if "SubstanceData" in directory:
            self.create(file_path, header, "SubstanceData_relationships_substance",
                        "SubstanceData_relationships_substance_openFDA", lists)
            self.create(file_path, header, "SubstanceData_moieties", "SubstanceData_moieties_openFDA", lists)
            self.create(file_path, header, "SubstanceData_mixture", "SubstanceData_mixture_openFDA", lists)
            self.create(file_path, header, "SubstanceData_substance", "SubstanceData_substance_openFDA", lists)
            self.create(file_path, header, "SubstanceData_names", "SubstanceData_names_openFDA", lists)
            self.create(file_path, header, "SubstanceData", "SubstanceData_openFDA", lists)
            self.constraint("SubstanceData_relationships_substance_openFDA_constraint",
                            "SubstanceData_relationships_substance_openFDA", "id")
            self.constraint("SubstanceData_moieties_openFDA_constraint", "SubstanceData_moieties_openFDA", "id")
            self.constraint("SubstanceData_mixture_openFDA_constraint", "SubstanceData_mixture_openFDA", "id")
            self.constraint("SubstanceData_substance_openFDA_constraint", "SubstanceData_substance_openFDA", "id")
            self.constraint("SubstanceData_names_openFDA_constraint", "SubstanceData_names_openFDA", "id")
            self.constraint("SubstanceData_openFDA_constraint", "SubstanceData_openFDA", "id")
            self.match("SubstanceData_relationships_substance_openFDA", "SubstanceData_openFDA", "id", "id")
            self.match("SubstanceData_mixture_openFDA", "SubstanceData_openFDA", "id", "id")
            self.match_from_file(file_path, "SubstanceData_moieties_id1_id2", "SubstanceData_moieties_openFDA",
                                 "SubstanceData_openFDA")
            self.match_from_file(file_path, "SubstanceData_substance_id1_id2", "SubstanceData_substance_openFDA",
                                 "SubstanceData_mixture_openFDA")
            self.set_properties(file_path, header, lists, "SubstanceData_relationships",
                                "SubstanceData_relationships_substance_openFDA", "SubstanceData_openFDA", "id", "id")
            self.set_properties(file_path, header, lists, "SubstanceData_component", "SubstanceData_substance_openFDA",
                                "SubstanceData_mixture_openFDA", "id", "id")


directory_maker = directory_maker()
parser = parser()
downloader = downloader(parser)
unzipper = unzipper()
former = former(parser)
reader = reader(parser, former)
cypher_creator = cypher_creator()

# Prüfe, ob ein Pfad über die Konsole übergeben wurde, sonst wird das Verzeichnis des Programms benutzt.
if len(sys.argv) > 1:
    try:
        path = str(sys.argv[1])
    except BaseException:
        path = os.path.dirname(os.path.abspath(__file__)) + '/'
else:
    path = os.path.dirname(os.path.abspath(__file__)) + '/'

print("Path is: " + path)

# Alle möglichen Verzeichnisse der FDA-Datenbank.
# directories = ["AnimalAndVeterinaryAdverseEvents","CAERSReports","COVID19SerologicalTestingEvaluations","Device510","DeviceAdverseEvents","DeviceClassification","DevicePremarketApproval","DeviceRecallEnforcementReports","DeviceRecalls","DeviceRegistrationsAndListings","DrugAdverseEvents","DrugLabeling","DrugRecallEnforcementReports","FoodRecallEnforcementReports","NationalDrugCodeDirectory","NSDE","SubstanceData","TabaccoProblemReports","UniqueDeviceIdentifier"];
# Alle relevanten Verzeichnisse der FDA-Datenbank.

directories = [
    "CAERSReports",
    "DrugAdverseEvents",
    "DrugRecallEnforcementReports",
    "FoodRecallEnforcementReports",
    "NationalDrugCodeDirectory",
    "SubstanceData"]

# Vor jedes Verzeichnis wird der angegebene Pfad gesetzt.
dicts = {}
i = 0
for directory in directories:
    dicts[directory] = path + directories[i]
    i += 1
for j in range(len(directories)):
    directories[j] = path + directories[j]

# Die Datei mit den Links zu den Dateien der Datenbank wird heruntergeladen.
r = requests.get('https://api.fda.gov/download.json', allow_redirects=True)
f = open(path + 'download.json', 'w')
f.write(r.content.decode("utf-8"))
f.close()

# Die load-cypher.cypher löschen
try:
    os.remove(path + 'load-cypher.cypher')
except BaseException:
    pass

# Arrays für das Erstellen der Cypher-Datei.
tsv_paths = []
tsv_headers = []
# Erstellen der Verzeichnisse.
directory_maker.make_directory(directories)
print('download', datetime.datetime.now())
# Die Dateien aus der Datenbank werden gedownloaded.
downloader.download(path + "download.json", dicts)

csv.field_size_limit(2000000)

for directory in directories:
    print('unzip', datetime.datetime.now())
    # Die Dateien des jeweiligen Verzeichnisses werden entpackt.
    unzipper.unzipall(directory)
    print('read all', datetime.datetime.now())
    # Die Dateien werden einzeln eingelesen und anschließend zu einer tsv-Datei verarbeitet.
    reader.readall(directory)
    print('generate files', datetime.datetime.now())
    # Dateipfade und Datei-Header werden gespeichert, um sie in der cypher-Datei zu verwenden.
    tsv_paths = former.tsv_path
    tsv_headers = former.tsv_header
    lists = former.lists
    print('remove lists', datetime.datetime.now())
    # Löschen der Listen in Former.
    former.remove_lists()
    print('create cypher', datetime.datetime.now())
    # Die Cypher-Datei wird erstellt.
    cypher_creator.create_cypher(tsv_paths, tsv_headers, directory, lists)
    tsv_paths = []
    tsv_headers = []
    lists = []
