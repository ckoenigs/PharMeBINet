import os
import requests
import zipfile
import json
from pathlib import Path
import sys
import shutil


class directory_maker():
    def __init__(self):
        pass

    """ Erstellt die Verzeichnisse. """
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

    """ Ändert den Namen der Dateien. """
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

    """ Downloaded und speichert die Datei, wenn diese noch nicht vorhanden ist. """
    def make_file(self, files, directories, entry, directory_name):
        name = self.trim(entry["display_name"])
        if not (str(Path(directories[directory_name]).name) + "_" + name + ".json.zip").replace("__", "_") in files:
            r = requests.get(entry["file"], allow_redirects=True)
            open((directories[directory_name] +
                  "/" +
                  str(Path(directories[directory_name]).name) +
                  "_" +
                  name +
                  ".json.zip").replace("__", "_"), 'wb').write(r.content)

    """ Filtert die Download-Links aus der download.json. """
    def download(self, f, directories):
        dictionary = self.parser.parse(f)
        dictionary = dictionary["results"]
        animal = dictionary["animalandveterinary"]
        drug = dictionary["drug"]
        device = dictionary["device"]
        food = dictionary["food"]
        other = dictionary["other"]
        tobacco = dictionary["tobacco"]
        if "AnimalAndVeterinaryAdverseEvents" in directories.keys():
            files = os.listdir(directories["AnimalAndVeterinaryAdverseEvents"])
            for entry in animal["event"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "AnimalAndVeterinaryAdverseEvents")

        if "CAERSReports" in directories:
            files = os.listdir(directories["CAERSReports"])
            for entry in food["event"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "CAERSReports")

        if "COVID19SerologicalTestingEvaluations" in directories:
            files = os.listdir(
                directories["COVID19SerologicalTestingEvaluations"])
            for entry in device["covid19serology"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "COVID19SerologicalTestingEvaluations")

        if "Device510" in directories:
            files = os.listdir(directories["Device510"])
            for entry in device["510k"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "Device510")
        if "DeviceAdverseEvents" in directories:
            files = os.listdir(directories["DeviceAdverseEvents"])
            for entry in device["event"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DeviceAdverseEvents")

        if "DeviceClassification" in directories:
            files = os.listdir(directories["DeviceClassification"])
            for entry in device["classification"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DeviceClassification")

        if "DevicePremarketApproval" in directories:
            files = os.listdir(directories["DevicePremarketApproval"])
            for entry in device["pma"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DevicePremarketApproval")

        if "DeviceRecallEnforcementReports" in directories:
            files = os.listdir(directories["DeviceRecallEnforcementReports"])
            for entry in device["enforcement"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DeviceRecallEnforcementReports")

        if "DeviceRecalls" in directories:
            files = os.listdir(directories["DeviceRecalls"])
            for entry in device["recall"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DeviceRecalls")

        if "DeviceRegistrationsAndListings" in directories:
            files = os.listdir(directories["DeviceRegistrationsAndListings"])
            for entry in device["registrationlisting"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DeviceRegistrationsAndListings")

        if "DrugAdverseEvents" in directories:
            files = os.listdir(directories["DrugAdverseEvents"])
            for entry in drug["event"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DrugAdverseEvents")

        if "DrugLabeling" in directories:
            files = os.listdir(directories["DrugLabeling"])
            for entry in drug["label"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "DrugLabeling")

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

        if "NSDE" in directories:
            files = os.listdir(directories["NSDE"])
            for entry in other["nsde"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "NSDE")

        if "SubstanceData" in directories:
            files = os.listdir(directories["SubstanceData"])
            for entry in other["substance"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "SubstanceData")

        if "TabaccoProblemReports" in directories:
            files = os.listdir(directories["TabaccoProblemReports"])
            for entry in tobacco["problem"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "TabaccoProblemReports")

        if "UniqueDeviceIdentifier" in directories:
            files = os.listdir(directories["UniqueDeviceIdentifier"])
            for entry in device["udi"]["partitions"]:
                print("Downloading " + "\"" + entry["file"] + "\"" + " ...")
                self.make_file(files, directories, entry, "UniqueDeviceIdentifier")


class unzipper:
    def __init__(self):
        pass

    """ Entzippt die Dateien und speichert sie unter neuem Namen.
        Anschließend werden sie in das richtige Verzeichnis kopiert.
        Das temporär erstellte Verzeichnis wird gelöscht. """
    def unzip(self, directory, f, count):
        print("Unzipping " + "\"" + f + "\" ...")
        subcount = 1
        with zipfile.ZipFile(f, 'r') as zipped:
            zipinfos = zipped.infolist()
            if(len(zipinfos) == 1):
                zipinfo = zipinfos[0]
                zipinfo.filename = os.path.basename(os.path.abspath(directory)) + '/' + os.path.splitext(
                    zipinfo.filename)[0] + '_' + str(count) + os.path.splitext(zipinfo.filename)[1]
                zipped.extract(zipinfo)
                shutil.move(zipinfo.filename, directory+'\\'+os.path.basename(zipinfo.filename))
                os.rmdir(os.path.dirname(zipinfo.filename))
            else:
                for zipinfo in zipinfos:
                    zipinfo.filename = os.path.basename(os.path.abspath(directory)) + '/' + os.path.splitext(
                        zipinfo.filename)[0] + '_' + str(count) + '_' + str(subcount) + os.path.splitext(zipinfo.filename)[1]
                    subcount += 1
                    zipped.extract(zipinfo)
        zipped.close()

    """ Unzipped alle Dateien im Verzeichnis,
        wenn die Anzahl der gezippten Dateien nicht der
        der ungezippten Dateien entspricht. """
    def unzipall(self, directory):
        files = os.listdir(directory)
        zipped = 0
        unzipped = 0
        for f in files:
            if(f.endswith('.zip')):
                zipped += 1
            elif(f.endswith('.json')):
                unzipped += 1
        if(zipped != unzipped):
            count = 1
            for f in files:
                if(f.endswith('.zip')):
                    self.unzip(directory, directory + '/' + f, count)
                    count += 1


class parser:
    def __init__(self):
        pass
    """This is a function found on the internet.
       It flattens a dictionary. """

    def flatten_json(self, y):
        out = {}

        def flatten(x, name=''):
            if isinstance(x, dict):
                for a in x:
                    flatten(x[a], name + a + '_')
            elif isinstance(x, list):
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x
        flatten(y)
        return out

    """ Lädt die Datei in ein Dictionary. """
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

    """ Geht alle Dateien des Verzeichnis durch. """
    def readall(self, directory):
        files = os.listdir(directory)
        for f in files:
            self.read(directory, f)

    """ Wenn die Datei eine json-Datei ist, wird sie geparsed.
        Anschließend werden ihre Daten in eine csv-Datei geschrieben. """
    def read(self, directory, f):
        if(f.endswith('.json')):
            data = self.parser.parse(directory + '/' + f)
            self.former.to_csv(data, directory)


class former:
    def __init__(self, parser):
        self.csv_path = {}
        self.csv_header = {}
        self.parser = parser
        self.animal_drug_keys = []
        self.animal_reaction_keys = []
        self.animal_event_keys = []
        self.animal_id = 1
        self.caers_keys = []
        self.caers_id = 1
        self.drugadverseevent_reaction_keys = []
        self.drugadverseevent_drug_keys = []
        self.drugadverseevent_keys = []
        self.drugadverseevent_id = 1
        self.drugrecallenforcementreports_openfda_keys = []
        self.drugrecallenforcementreports_keys = []
        self.drugrecallenforcementreports_id = 1
        self.foodrecallenforcementreports_keys = []
        self.foodrecallenforcementreports_id = 1
        self.nationaldrugcodedirectory_activeingredients_keys = []
        self.nationaldrugcodedirectory_keys = []
        self.nationaldrugcodedirectory_id = 1
        self.substancedata_names_keys = []
        self.substancedata_keys = []
        self.substancedata_id = 1

    """ Trimmet einen String. """
    def trim(self, s):
        return s.replace("\"", "\'").replace(",", "").replace("\\", "").replace("\n", "")

    """ Überprüft erst, welche Kategorie über Dictionary gegeben ist.
        Filtert die Keys aus den Daten und schreibt sie als Header in eine csv-Datei.
        Anschließend wird jeder Eintrag der Datei in die csv-Datei geschrieben.
        Vor jeden Eintrag wird eine ID gesetzt.
        Die Keys, sowie die Dateipfade werden zum Erstellen der cypher-Datei gespeichert. """
    def to_csv(self, dicts, directory):
        print("Creating csv ...")
        if("AnimalAndVeterinaryAdverseEvents" in directory):
            if not os.path.isfile(directory + "/AnimalAndVeterinaryAdverseEvent_drug.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary["drug"][0].keys():
                        if key not in self.animal_drug_keys:
                            self.animal_drug_keys.append(key)
                header = "\"id\","
                for key in self.animal_drug_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(directory + "/AnimalAndVeterinaryAdverseEvent_drug.csv", 'w', encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(directory + "/AnimalAndVeterinaryAdverseEvent_reaction.csv"):
                for dictionary in dicts["results"]:
                    for d in dictionary["reaction"]:
                        for key in d:
                            if key not in self.animal_reaction_keys:
                                self.animal_reaction_keys.append(key)
                header = "\"id\","
                for key in self.animal_reaction_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(directory + "/AnimalAndVeterinaryAdverseEvent_reaction.csv", 'w', encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(directory +
                                  "/AnimalAndVeterinaryAdverseEvent.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.animal_event_keys:
                            self.animal_event_keys.append(key)
                header = "\"id\","
                for key in self.animal_event_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/AnimalAndVeterinaryAdverseEvent.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            line = ""
            reaction = ""
            event = ""
            for dictionary in dicts["results"]:
                line = line + "\"" + str(self.animal_id) + "\"" + ','
                event = event + "\"" + str(self.animal_id) + "\"" + ','
                for key in self.animal_drug_keys:
                    if key in dictionary["drug"][0].keys() and len(str(dictionary["drug"][0][key])) < 2000000:
                        line = line + "\"" + \
                            self.trim(str(dictionary["drug"][0][key])) + "\"" + ','
                    else:
                        line = line + "\"" + "\"" + ','
                line = line[:len(line) - 1] + '\n'
                try:
                    for d in dictionary["reaction"]:
                        reaction = reaction + "\"" + \
                            str(self.animal_id) + "\"" + ','
                        for key in self.animal_reaction_keys:
                            if key in d and len(str(d[key])) < 2000000:
                                reaction = reaction + "\"" + \
                                    self.trim(str(d[key])) + "\"" + ','
                            else:
                                reaction = reaction + "\"" + "\"" + ','
                        reaction = reaction[:len(reaction) - 1] + '\n'
                    reaction = reaction[:len(reaction) - 1] + '\n'
                except BaseException:
                    pass
                for key in self.animal_event_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        event = event + "\"" + \
                            self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        event = event + "\"" + "\"" + ','
                event = event[:len(event) - 1] + '\n'
                f = open(directory + "/AnimalAndVeterinaryAdverseEvent_drug.csv", 'a', encoding="utf-8")
                f.write(line)
                f.close()
                f = open(directory + "/AnimalAndVeterinaryAdverseEvent_reaction.csv", 'a', encoding="utf-8")
                f.write(reaction)
                f.close()
                f = open(
                    directory +
                    "/AnimalAndVeterinaryAdverseEvent.csv",
                    'a',
                    encoding="utf-8")
                f.write(event)
                f.close()
                line = ""
                reaction = ""
                event = ""
                self.animal_id += 1
            if "AnimalAndVeterinaryAdverseEvent_drug" not in self.csv_path:
                self.csv_path["AnimalAndVeterinaryAdverseEvent_drug"] = directory + "/AnimalAndVeterinaryAdverseEvent_drug.csv"
            if "AnimalAndVeterinaryAdverseEvent_reaction" not in self.csv_path:
                self.csv_path["AnimalAndVeterinaryAdverseEvent_reaction"] = directory + "/AnimalAndVeterinaryAdverseEvent_reaction.csv"
            if "AnimalAndVeterinaryAdverseEvent" not in self.csv_path:
                self.csv_path["AnimalAndVeterinaryAdverseEvent"] = directory + \
                    "/AnimalAndVeterinaryAdverseEvent.csv"
            if "AnimalAndVeterinaryAdverseEvent_drug" not in self.csv_header:
                self.csv_header["AnimalAndVeterinaryAdverseEvent_drug"] = ["id"] + self.animal_drug_keys
            if "AnimalAndVeterinaryAdverseEvent_reaction" not in self.csv_header:
                self.csv_header["AnimalAndVeterinaryAdverseEvent_reaction"] = [
                    "id"] + self.animal_reaction_keys
            if "AnimalAndVeterinaryAdverseEvent" not in self.csv_header:
                self.csv_header["AnimalAndVeterinaryAdverseEvent"] = [
                    "id"] + self.animal_event_keys

        if("CAERSReports" in directory):
            if not os.path.isfile(directory + "/CAERSReport.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.caers_keys:
                            self.caers_keys.append(key)
                header = "\"id\","
                for key in self.caers_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/CAERSReport.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            report = ""
            for dictionary in dicts["results"]:
                report = report + "\"" + str(self.caers_id) + "\"" + ','
                for key in self.caers_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        report = report + "\"" + self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        report = report + "\"" + "\"" + ','
                report = report[:len(report) - 1] + '\n'
                f = open(
                    directory +
                    "/CAERSReport.csv",
                    'a',
                    encoding="utf-8")
                f.write(report)
                f.close()
                report = ""
                self.caers_id += 1
            if "CAERSReport" not in self.csv_path:
                self.csv_path["CAERSReport"] = directory + "/CAERSReport.csv"
            if "CAERSReport" not in self.csv_header:
                self.csv_header["CAERSReport"] = ["id"] + self.caers_keys

        if("DrugAdverseEvents" in directory):
            if not os.path.isfile(
                    directory + "/DrugAdverseEvent_reaction.csv"):
                for dictionary in dicts["results"]:
                    for d in dictionary["patient"]["reaction"]:
                        for key in d:
                            if key not in self.drugadverseevent_reaction_keys:
                                self.drugadverseevent_reaction_keys.append(key)
                header = "\"id\","
                for key in self.drugadverseevent_reaction_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugAdverseEvent_reaction.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(directory + "/DrugAdverseEvent_drug.csv"):
                for dictionary in dicts["results"]:
                    for d in dictionary["patient"]["drug"]:
                        for key in d:
                            if key not in self.drugadverseevent_drug_keys:
                                self.drugadverseevent_drug_keys.append(key)
                header = "\"id\","
                for key in self.drugadverseevent_drug_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugAdverseEvent_drug.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(directory + "/DrugAdverseEvent.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.drugadverseevent_keys:
                            self.drugadverseevent_keys.append(key)
                header = "\"id\","
                for key in self.drugadverseevent_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugAdverseEvent.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            reaction = ""
            drug = ""
            drugadverseevent = ""
            for dictionary in dicts["results"]:
                for d in dictionary["patient"]["reaction"]:
                    reaction = reaction + "\"" + \
                        str(self.drugadverseevent_id) + "\"" + ','
                    for key in self.drugadverseevent_reaction_keys:
                        if key in d and len(str(d[key])) < 2000000:
                            reaction = reaction + "\"" + \
                                self.trim(str(d[key])) + "\"" + ','
                        else:
                            reaction = reaction + "\"" + "\"" + ','
                    reaction = reaction[:len(reaction) - 1] + '\n'
                reaction = reaction[:len(reaction) - 1] + '\n'
                for d in dictionary["patient"]["drug"]:
                    drug = drug + "\"" + \
                        str(self.drugadverseevent_id) + "\"" + ','
                    for key in self.drugadverseevent_drug_keys:
                        if key in d and len(str(d[key])) < 2000000:
                            drug = drug + "\"" + \
                                self.trim(str(d[key])) + "\"" + ','
                        else:
                            drug = drug + "\"" + "\"" + ','
                    drug = drug[:len(drug) - 1] + '\n'
                drug = drug[:len(drug) - 1] + '\n'
                drugadverseevent = drugadverseevent + "\"" + \
                    str(self.drugadverseevent_id) + "\"" + ','
                for key in self.drugadverseevent_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        drugadverseevent = drugadverseevent + "\"" + \
                            self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        drugadverseevent = drugadverseevent + "\"" + "\"" + ','
                drugadverseevent = drugadverseevent[:len(
                    drugadverseevent) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugAdverseEvent_reaction.csv",
                    'a',
                    encoding="utf-8")
                f.write(reaction)
                f.close()
                f = open(
                    directory +
                    "/DrugAdverseEvent_drug.csv",
                    'a',
                    encoding="utf-8")
                f.write(drug)
                f.close()
                f = open(
                    directory +
                    "/DrugAdverseEvent.csv",
                    'a',
                    encoding="utf-8")
                f.write(drugadverseevent)
                f.close()
                reaction = ""
                drug = ""
                drugadverseevent = ""
                self.drugadverseevent_id += 1
            if "DrugAdverseEvent_reaction" not in self.csv_path:
                self.csv_path["DrugAdverseEvent_reaction"] = directory + \
                    "/DrugAdverseEvent_reaction.csv"
            if "DrugAdverseEvent_drug" not in self.csv_path:
                self.csv_path["DrugAdverseEvent_drug"] = directory + \
                    "/DrugAdverseEvent_drug.csv"
            if "DrugAdverseEvent" not in self.csv_path:
                self.csv_path["DrugAdverseEvent"] = directory + \
                    "/DrugAdverseEvent.csv"
            if "DrugAdverseEvent_reaction" not in self.csv_header:
                self.csv_header["DrugAdverseEvent_reaction"] = ["id"] + \
                    self.drugadverseevent_reaction_keys
            if "DrugAdverseEvent_drug" not in self.csv_header:
                self.csv_header["DrugAdverseEvent_drug"] = ["id"] + \
                    self.drugadverseevent_drug_keys
            if "DrugAdverseEvent" not in self.csv_header:
                self.csv_header["DrugAdverseEvent"] = [
                    "id"] + self.drugadverseevent_keys

        if("DrugRecallEnforcementReports" in directory):
            if not os.path.isfile(directory +
                                  "/DrugRecallEnforcementReport_openfda.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary["openfda"]:
                        if key not in self.drugrecallenforcementreports_openfda_keys:
                            self.drugrecallenforcementreports_openfda_keys.append(
                                key)
                header = "\"id\","
                for key in self.drugrecallenforcementreports_openfda_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugRecallEnforcementReport_openfda.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(
                    directory + "/DrugRecallEnforcementReport.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.drugrecallenforcementreports_keys:
                            self.drugrecallenforcementreports_keys.append(key)
                header = "\"id\","
                for key in self.drugrecallenforcementreports_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugRecallEnforcementReport.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            drugrecallenforcementreport_openfda = ""
            drugrecallenforcementreport = ""
            for dictionary in dicts["results"]:
                drugrecallenforcementreport_openfda = drugrecallenforcementreport_openfda + \
                    "\"" + str(self.drugrecallenforcementreports_id) + "\"" + ','
                for key in self.drugrecallenforcementreports_openfda_keys:
                    if key in dictionary["openfda"].keys() and len(str(dictionary["openfda"][key])) < 2000000:
                        drugrecallenforcementreport_openfda = drugrecallenforcementreport_openfda + "\"" + \
                            self.trim(str(dictionary["openfda"][key])) + "\"" + ','
                    else:
                        drugrecallenforcementreport_openfda = drugrecallenforcementreport_openfda + "\"" + "\"" + ','
                drugrecallenforcementreport_openfda = drugrecallenforcementreport_openfda[:len(
                    drugrecallenforcementreport_openfda) - 1] + '\n'
                drugrecallenforcementreport = drugrecallenforcementreport + \
                    "\"" + str(self.drugrecallenforcementreports_id) + "\"" + ','
                for key in self.drugrecallenforcementreports_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        drugrecallenforcementreport = drugrecallenforcementreport + "\"" + \
                            self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        drugrecallenforcementreport = drugrecallenforcementreport + "\"" + "\"" + ','
                drugrecallenforcementreport = drugrecallenforcementreport[:len(
                    drugrecallenforcementreport) - 1] + '\n'
                f = open(
                    directory +
                    "/DrugRecallEnforcementReport_openfda.csv",
                    'a',
                    encoding="utf-8")
                f.write(drugrecallenforcementreport_openfda)
                f.close()
                f = open(
                    directory +
                    "/DrugRecallEnforcementReport.csv",
                    'a',
                    encoding="utf-8")
                f.write(drugrecallenforcementreport)
                f.close()
                drugrecallenforcementreport_openfda = ""
                drugrecallenforcementreport = ""
                self.drugrecallenforcementreports_id += 1
            if "DrugRecallEnforcementReport_openfda" not in self.csv_path:
                self.csv_path["DrugRecallEnforcementReport_openfda"] = directory + \
                    "/DrugRecallEnforcementReport_openfda.csv"
            if "DrugRecallEnforcementReports" not in self.csv_path:
                self.csv_path["DrugRecallEnforcementReport"] = directory + \
                    "/DrugRecallEnforcementReport.csv"
            if "DrugRecallEnforcementReport_openfda" not in self.csv_header:
                self.csv_header["DrugRecallEnforcementReport_openfda"] = ["id"] + \
                    self.drugrecallenforcementreports_openfda_keys
            if "DrugRecallEnforcementReport" not in self.csv_header:
                self.csv_header["DrugRecallEnforcementReport"] = [
                    "id"] + self.drugrecallenforcementreports_keys

        if ("FoodRecallEnforcementReports" in directory):
            if not os.path.isfile(
                    directory + "/FoodRecallEnforcementReport.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.foodrecallenforcementreports_keys:
                            self.foodrecallenforcementreports_keys.append(key)
                header = "\"id\","
                for key in self.foodrecallenforcementreports_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/FoodRecallEnforcementReport.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            report = ""
            for dictionary in dicts["results"]:
                report = report + "\"" + \
                    str(self.foodrecallenforcementreports_id) + "\"" + ','
                for key in self.foodrecallenforcementreports_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        report = report + "\"" + \
                            self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        report = report + "\"" + "\"" + ','
                report = report[:len(report) - 1] + '\n'
                f = open(
                    directory +
                    "/FoodRecallEnforcementReport.csv",
                    'a',
                    encoding="utf-8")
                f.write(report)
                f.close()
                report = ""
                self.foodrecallenforcementreports_id += 1
            if "FoodRecallEnforcementReport" not in self.csv_path:
                self.csv_path["FoodRecallEnforcementReport"] = directory + \
                    "/FoodRecallEnforcementReport.csv"
            if "FoodRecallEnforcementReport" not in self.csv_header:
                self.csv_header["FoodRecallEnforcementReport"] = [
                    "id"] + self.foodrecallenforcementreports_keys

        if ("NationalDrugCodeDirectory" in directory):
            if not os.path.isfile(
                    directory + "/NationalDrugCodeDirectory_activeingredients.csv"):
                for dictionary in dicts["results"]:
                    try:
                        for d in dictionary["active_ingredients"]:
                            for key in d.keys():
                                if key not in self.nationaldrugcodedirectory_activeingredients_keys:
                                    self.nationaldrugcodedirectory_activeingredients_keys.append(
                                        key)
                    except BaseException:
                        pass
                header = "\"id\","
                for key in self.nationaldrugcodedirectory_activeingredients_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/NationalDrugCodeDirectory_activeingredients.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(
                    directory + "/NationalDrugCodeDirectory.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.nationaldrugcodedirectory_keys:
                            self.nationaldrugcodedirectory_keys.append(key)
                header = "\"id\","
                for key in self.nationaldrugcodedirectory_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/NationalDrugCodeDirectory.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            activeingredients = ""
            nationaldrugcodedirectory = ""
            for dictionary in dicts["results"]:
                try:
                    for d in dictionary["active_ingredients"]:
                        activeingredients = activeingredients + "\"" + \
                            str(self.nationaldrugcodedirectory_id) + "\"" + ','
                        for key in self.nationaldrugcodedirectory_activeingredients_keys:
                            if key in d and len(str(d[key])) < 2000000:
                                activeingredients = activeingredients + "\"" + \
                                    self.trim(str(d[key])) + "\"" + ','
                            else:
                                activeingredients = activeingredients + "\"" + "\"" + ','
                        activeingredients = activeingredients[:len(
                            activeingredients) - 1] + '\n'
                    activeingredients = activeingredients[:len(
                        activeingredients) - 1] + '\n'
                except BaseException:
                    activeingredients = activeingredients + "\"" + \
                        str(self.nationaldrugcodedirectory_id) + "\"" + ','
                    for key in self.nationaldrugcodedirectory_activeingredients_keys:
                        activeingredients = activeingredients + "\"" + "\"" + ','
                    activeingredients = activeingredients[:len(
                        activeingredients) - 1] + '\n'
                nationaldrugcodedirectory = nationaldrugcodedirectory + \
                    "\"" + str(self.nationaldrugcodedirectory_id) + "\"" + ','
                for key in self.nationaldrugcodedirectory_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        nationaldrugcodedirectory = nationaldrugcodedirectory + "\"" + \
                            self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        nationaldrugcodedirectory = nationaldrugcodedirectory + "\"" + "\"" + ','
                nationaldrugcodedirectory = nationaldrugcodedirectory[:len(
                    nationaldrugcodedirectory) - 1] + '\n'
                f = open(
                    directory +
                    "/NationalDrugCodeDirectory_activeingredients.csv",
                    'a',
                    encoding="utf-8")
                f.write(activeingredients)
                f.close()
                f = open(
                    directory +
                    "/NationalDrugCodeDirectory.csv",
                    'a',
                    encoding="utf-8")
                f.write(nationaldrugcodedirectory)
                f.close()
                activeingredients = ""
                nationaldrugcodedirectory = ""
                self.nationaldrugcodedirectory_id += 1
            if "NationalDrugCodeDirectory_activeingredients" not in self.csv_path:
                self.csv_path["NationalDrugCodeDirectory_activeingredients"] = directory + \
                    "/NationalDrugCodeDirectory_activeingredients.csv"
            if "NationalDrugCodeDirectory" not in self.csv_path:
                self.csv_path["NationalDrugCodeDirectory"] = directory + \
                    "/NationalDrugCodeDirectory.csv"
            if "NationalDrugCodeDirectory_activeingredients" not in self.csv_header:
                self.csv_header["NationalDrugCodeDirectory_activeingredients"] = [
                    "id"] + self.nationaldrugcodedirectory_activeingredients_keys
            if "NationalDrugCodeDirectory" not in self.csv_header:
                self.csv_header["NationalDrugCodeDirectory"] = [
                    "id"] + self.nationaldrugcodedirectory_keys

        if ("SubstanceData" in directory):
            if not os.path.isfile(directory + "/SubstanceData_names.csv"):
                for dictionary in dicts["results"]:
                    try:
                        for d in dictionary["names"]:
                            for key in d.keys():
                                if key not in self.substancedata_names_keys:
                                    self.substancedata_names_keys.append(key)
                    except BaseException:
                        pass
                header = "\"id\","
                for key in self.substancedata_names_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/SubstanceData_names.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            if not os.path.isfile(directory + "/SubstanceData.csv"):
                for dictionary in dicts["results"]:
                    for key in dictionary.keys():
                        if key not in self.substancedata_keys:
                            self.substancedata_keys.append(key)
                header = "\"id\","
                for key in self.substancedata_keys:
                    header = header + "\"" + key + "\"" + ','
                header = header[:len(header) - 1] + '\n'
                f = open(
                    directory +
                    "/SubstanceData.csv",
                    'w',
                    encoding="utf-8")
                f.write(header)
                f.close()
            names = ""
            substancedata = ""
            for dictionary in dicts["results"]:
                try:
                    for d in dictionary["names"]:
                        names = names + "\"" + \
                            str(self.substancedata_id) + "\"" + ','
                        for key in self.substancedata_names_keys:
                            if key in d and len(str(d[key])) < 2000000:
                                names = names + "\"" + \
                                    self.trim(str(d[key])) + "\"" + ','
                            else:
                                names = names + "\"" + "\"" + ','
                        names = names[:len(names) - 1] + '\n'
                    names = names[:len(names) - 1] + '\n'
                except BaseException:
                    names = names + "\"" + \
                        str(self.substancedata_id) + "\"" + ','
                    for key in self.substancedata_names_keys:
                        names = names + "\"" + "\"" + ','
                    names = names[:len(names) - 1] + '\n'
                substancedata = substancedata + "\"" + \
                    str(self.substancedata_id) + "\"" + ','
                for key in self.substancedata_keys:
                    if key in dictionary.keys() and len(str(dictionary[key])) < 2000000:
                        substancedata = substancedata + "\"" + self.trim(str(dictionary[key])) + "\"" + ','
                    else:
                        substancedata = substancedata + "\"" + "\"" + ','
                substancedata = substancedata[:len(substancedata) - 1] + '\n'
                f = open(
                    directory +
                    "/SubstanceData_names.csv",
                    'a',
                    encoding="utf-8")
                f.write(names)
                f.close()
                f = open(
                    directory +
                    "/SubstanceData.csv",
                    'a',
                    encoding="utf-8")
                f.write(substancedata)
                f.close()
                names = ""
                substancedata = ""
                self.substancedata_id += 1
            if "SubstanceData_names" not in self.csv_path:
                self.csv_path["SubstanceData_names"] = directory + "/SubstanceData_names.csv"
            if "SubstanceData" not in self.csv_path:
                self.csv_path["SubstanceData"] = directory + \
                    "/SubstanceData.csv"
            if "SubstanceData_names" not in self.csv_header:
                self.csv_header["SubstanceData_names"] = ["id"] + \
                    self.substancedata_names_keys
            if "SubstanceData" not in self.csv_header:
                self.csv_header["SubstanceData"] = [
                    "id"] + self.substancedata_keys


class cypher_creator:
    def __init__(self):
        self.script = ""

    """ Erstellt einen neuen Knoten. """
    def create(self, file_path, header, name):
        statement = ":auto USING PERIODIC COMMIT 100 LOAD CSV WITH HEADERS FROM 'file:///" + \
           str(file_path[name]).replace('\\', '/') + "' AS row FIELDTERMINATOR ',' CREATE "
        obj = "(" + name + \
            ":" + name + " "
        attributes = "{"
        for head in header[name]:
            attributes = attributes + \
                str(head).replace("\"", "") + ": row." + str(head).replace("\"", "") + ", "
        attributes = attributes[:len(attributes) - 2] + "}"
        statement = statement + obj + attributes + ");" + '\n'
        f = open("load-cypher.cypher", 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Erstellt einen neuen Constraint. """
    def constraint(self, name1, name2):
        statement = '\n' + \
            "CREATE CONSTRAINT " + name1 + " IF NOT EXISTS ON (n: " + name2 + ") ASSERT n.id IS UNIQUE;"
        f = open("load-cypher.cypher", 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Matched zwei Knoten. """
    def match(self, name1, name2):
        statement = '\n' + \
            "MATCH (n: " + name1 + "), (m: " + name2 + ") WHERE n.id = m.id MERGE (n)-[:Event]->(m);"
        f = open("load-cypher.cypher", 'a', encoding="utf-8")
        f.write(statement)
        f.close()

    """ Überprüft über Directory, welche Kategorie gegeben ist.
        Anschließend werden die jeweiligen Knoten, Constraints und Merges erstellt. """
    def create_cypher(self, file_path, header, directory):
        print("Creating Cypher-File ...")
        if "AnimalAndVeterinaryAdverseEvents" in directory:
            self.create(file_path, header, "AnimalAndVeterinaryAdverseEvent_drug")
            self.create(file_path, header, "AnimalAndVeterinaryAdverseEvent_reaction")
            self.create(file_path, header, "AnimalAndVeterinaryAdverseEvent")
            self.constraint("AnimalAndVeterinaryAdverseEvent_drug_constraint", "AnimalAndVeterinaryAdverseEvent_drug")
            self.constraint("AnimalAndVeterinaryAdverseEvent_constraint", "AnimalAndVeterinaryAdverseEvent")
            self.match("AnimalAndVeterinaryAdverseEvent_drug", "AnimalAndVeterinaryAdverseEvent")
            self.match("AnimalAndVeterinaryAdverseEvent_reaction", "AnimalAndVeterinaryAdverseEvent")

        if "CAERSReports" in directory:
            self.create(file_path, header, "CAERSReport")
            self.constraint("CAERSReport_constraint", "CAERSReport")

        if "DrugAdverseEvents" in directory:
            self.create(file_path, header, "DrugAdverseEvent_reaction")
            self.create(file_path, header, "DrugAdverseEvent_drug")
            self.create(file_path, header, "DrugAdverseEvent")
            self.constraint("DrugAdverseEvent_constraint", "DrugAdverseEvent")
            self.match("DrugAdverseEvent_reaction", "DrugAdverseEvent")
            self.match("DrugAdverseEvent_drug", "DrugAdverseEvent")

        if "DrugRecallEnforcementReports" in directory:
            self.create(file_path, header, "DrugRecallEnforcementReport_openfda")
            self.create(file_path, header, "DrugRecallEnforcementReport")
            self.constraint("DrugRecallEnforcementReport_constraint", "DrugRecallEnforcementReport_openfda")
            self.constraint("DrugRecallEnforcementReport_constraint", "DrugRecallEnforcementReport")
            self.match("DrugRecallEnforcementReport_openfda", "DrugRecallEnforcementReport")

        if "FoodRecallEnforcementReports" in directory:
            self.create(file_path, header, "FoodRecallEnforcementReport")
            self.constraint("FoodRecallEnforcementReport_constraint", "FoodRecallEnforcementReport")

        if "NationalDrugCodeDirectory" in directory:
            self.create(file_path, header, "NationalDrugCodeDirectory_activeingredients")
            self.create(file_path, header, "NationalDrugCodeDirectory")
            self.constraint("NationalDrugCodeDirectory_constraint", "NationalDrugCodeDirectory")
            self.match("NationalDrugCodeDirectory_activeingredients", "NationalDrugCodeDirectory")

        if "SubstanceData" in directory:
            self.create(file_path, header, "SubstanceData_names")
            self.create(file_path, header, "SubstanceData")
            self.constraint("SubstanceData_constraint", "SubstanceData")
            self.match("SubstanceData_names", "SubstanceData")

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
        path = sys.argv[1]
    except BaseException:
        path = os.path.dirname(os.path.abspath(__file__)) + '/'
else:
    path = os.path.dirname(os.path.abspath(__file__)) + '/'

print("Path is: " + path)

# Alle möglichen Verzeichnisse der FDA-Datenbank.
# directories = ["AnimalAndVeterinaryAdverseEvents","CAERSReports","COVID19SerologicalTestingEvaluations","Device510","DeviceAdverseEvents","DeviceClassification","DevicePremarketApproval","DeviceRecallEnforcementReports","DeviceRecalls","DeviceRegistrationsAndListings","DrugAdverseEvents","DrugLabeling","DrugRecallEnforcementReports","FoodRecallEnforcementReports","NationalDrugCodeDirectory","NSDE","SubstanceData","TabaccoProblemReports","UniqueDeviceIdentifier"];
# Alle relevanten Verzeichnisse der FDA-Datenbank.
directories = [
    "AnimalAndVeterinaryAdverseEvents",
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
f = open(path+'download.json', 'w')
f.write(r.content.decode("utf-8"))
f.close()

# Arrays für das Erstellen der Cypher-Datei.
csv_paths = []
csv_headers = []
# Erstellen der Verzeichnisse.
directory_maker.make_directory(directories)
# Die Dateien aus der Datenbank werden gedownloaded.
downloader.download(path + "download.json", dicts)
for directory in directories:
    # Die Dateien des jeweiligen Verzeichnisses werden entpackt.
    unzipper.unzipall(directory)
    # Die Dateien werden einzeln eingelesen und anschließend zu einer csv-Datei verarbeitet.
    reader.readall(directory)
    csv_paths = former.csv_path
    csv_headers = former.csv_header
    # Die Cypher-Datei wird erstellt.
    cypher_creator.create_cypher(csv_paths, csv_headers, directory)
    csv_paths = []
    csv_headers = []
