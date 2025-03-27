"""
https://github.com/dhimmel/drugbank/blob/gh-pages/parse.ipynb
"""

import os
import csv
import collections
import xml.etree.ElementTree as ET
import datetime
import sys, html

import pandas

sys.path.append("../..")
import pharmebinetutils

# path to directory of project
if len(sys.argv) < 1:
    sys.exit('need a path')
path_of_directory = sys.argv[1]

# dictionary category name to category id
dict_category_name_to_id = {}

# open file with all drugbank categories
file = open('drugbank/categories.tsv', 'r', encoding='utf-8')

# generate a file for "proteins" to show which are proteinss and which are not
decision_protein_file = open('maybe_protein_manual_checked.tsv', 'w', encoding='utf-8')
csv_decision_protein_file = csv.writer(decision_protein_file, delimiter='\t')
csv_decision_protein_file.writerow(['name', 'identifier', 'labels', 'Protein_ja=1_und_nein=0'])
maybe_not_protein_set = set()

# prepare drugbank atc information
dict_atc_nodes = {}
set_atc_edges = set()

# get the information for the drugbank categroies
csv_reader = csv.reader(file, delimiter='\t')
next(csv_reader)
for row in csv_reader:
    if row[1] in dict_category_name_to_id:
        sys.exit('ohje')
    name = html.unescape(row[1])
    dict_category_name_to_id[name] = row[0]

# open the xml file
xml_file = os.path.join('full database.xml')
# xml_file = os.path.join('part.xml')
# xml_file = os.path.join('drugbank_all_full_database_dezember.xml/test.xml')
print(datetime.datetime.now())

# parse it to usable formart
tree = ET.parse(xml_file)
root = tree.getroot()

print(datetime.datetime.now())

# templates to extract some information from drugbank xml
ns = '{http://www.drugbank.ca}'
inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"
smiles_template = "{ns}calculated-properties/{ns}property[{ns}kind='SMILES']/{ns}value"
molecular_formula_template = "{ns}calculated-properties/{ns}property[{ns}kind='Molecular Formula']/{ns}value"
molecular_formula_experimental_template = "{ns}experimental-properties/{ns}property[{ns}kind='Molecular Formula']/{ns}value"

# reference id to source
dict_reference_id_to_infos = {}

# counter_reaction_ids
counter_reaction_ids = 1


def add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions, organism, ref_article_list,
                                    ref_link_list, ref_attachment_list, ref_textbooks_list, known_action,
                                    target_id=None, induction_strength=None, inhibition_strength=None):
    """
    Prepare dictionary for relationship information between drug and carrier/enzyme/target/transporter
    :param drug_targets: dictionary
    :param db_ID: string
    :param db_targets: string
    :param position: string
    :param actions: list
    :param organism: string
    :param ref_article_list: list
    :param ref_link_list: list
    :param ref_attachment_list: list
    :param ref_textbooks_list:  list
    :param known_action: string
    :param target_id: string
    :param induction_strength: string
    :param inhibition_strength: string
    :return:
    """
    drug_targets['drugbank_id'] = db_ID
    drug_targets['targets_id_drugbank'] = db_targets
    drug_targets['position'] = position
    drug_targets['organism'] = organism
    drug_targets['actions'] = actions
    drug_targets['ref_article'] = ref_article_list
    drug_targets['ref_links'] = ref_link_list
    drug_targets['ref_attachment'] = ref_attachment_list
    drug_targets['ref_textbooks'] = ref_textbooks_list
    drug_targets['known_action'] = known_action
    if target_id:
        drug_targets['targets_id'] = target_id
    if inhibition_strength:
        drug_targets['inhibition_strength'] = inhibition_strength
    if induction_strength:
        drug_targets['induction_strength'] = induction_strength
    return drug_targets


def gather_target_infos(drug_info, target, drug_targets_info, targets_info, dict_targets_ids, db_ID, is_enzyme, is_target):
    """
    This gather the information for carrier, enzyme, target and transporter node. First the information for the
    relationship are gathered. Then if the carrier, enzyme, target and transporter has peptides then generate for them
    nodes with properties: # identifier (uniprot id), drugbank id, name , id source, general function, specific
    function, gene name, locus, cellular location, transmembrane regions, signal regions, theoretical pi, molecular
    weight, chromosome location, organism, xrefs, synonyms, amino acid sequence, gene sequence, pfams, go classifier
    If more then one polypeptide exists then an over node is generated with the drugbank id as identifier and the name
    and is connected to the polypeptides as has component. If no polypeptides exists then only the node with drugbank id
    and name is generated with connection to the drug. If only one peptide exists then the relationship is generated
    between this peptide and the drug.

    Also, for every polypeptide a edge is generated.
    :param target:string
    :param drug_targets_info: list of dictionaries
    :param targets_info: list of dictionaries
    :param dict_targets_ids:
    :param db_ID: string
    :param is_enzyme: boolean
    :param is_target:boolean
    :return:
    """
    for targets in drug_info.iterfind(target.format(ns=ns)):
        #        print('drinnen ;)')

        db_targets = targets.findtext("{ns}id".format(ns=ns))

        name_target = targets.findtext("{ns}name".format(ns=ns))

        # gather relationships information
        position = targets.get('position')
        organism = targets.findtext("{ns}organism".format(ns=ns))
        known_action = targets.findtext("{ns}known-action".format(ns=ns))

        if is_enzyme:
            inhibition_strength = targets.findtext("{ns}inhibition-strength".format(ns=ns))
            induction_strength = targets.findtext("{ns}induction-strength".format(ns=ns))

        actions = []
        for action in targets.findall('{ns}actions/{ns}action'.format(ns=ns)):
            actions.append(action.text)

        ref_article_list = []
        for ref in targets.findall('{ns}references/{ns}articles/{ns}article'.format(ns=ns)):
            pubmed_id = ref.findtext("{ns}pubmed-id".format(ns=ns))
            citation = ref.findtext("{ns}citation".format(ns=ns))
            ref_id = ref.findtext("{ns}ref-id".format(ns=ns))
            dict_reference_id_to_infos[ref_id] = [pubmed_id, citation]

            ref_article_list.append(ref_id + '::' + pubmed_id + '::' + citation)

        ref_textbooks_list = []
        for ref in targets.findall('{ns}references/{ns}textbooks/{ns}textbook'.format(ns=ns)):
            isbn = ref.findtext("{ns}isbn".format(ns=ns))
            citation = ref.findtext("{ns}citation".format(ns=ns))
            ref_id = ref.findtext("{ns}ref-id".format(ns=ns))
            dict_reference_id_to_infos[ref_id] = [isbn, citation]
            ref_textbooks_list.append(ref_id + '::' + isbn + '::' + citation)

        ref_link_list = []
        for ref in targets.findall('{ns}references/{ns}links/{ns}link'.format(ns=ns)):
            title = ref.findtext("{ns}title".format(ns=ns))
            url = ref.findtext("{ns}url".format(ns=ns))
            ref_id = ref.findtext("{ns}ref-id".format(ns=ns))
            dict_reference_id_to_infos[ref_id] = [url, title]
            ref_link_list.append(ref_id + '::' + title + '::' + url)

        ref_attachment_list = []
        for ref in targets.findall('{ns}references/{ns}attachments/{ns}attachment'.format(ns=ns)):
            title = ref.findtext("{ns}title".format(ns=ns))
            url = ref.findtext("{ns}url".format(ns=ns))
            ref_id = ref.findtext("{ns}ref-id".format(ns=ns))
            dict_reference_id_to_infos[ref_id] = [url, title]
            ref_attachment_list.append(ref_id + '::' + title + '::' + url)

        polypetide_found = False
        peptide_list = []
        dict_drug_target = {}

        # go through all polypeptide  generate target and drug-target dictionaries
        # add the drug target information into a dictionary
        for polypeptide in targets.findall("{ns}polypeptide".format(ns=ns)):
            polypetide_found = True
            drug_targets = collections.OrderedDict()
            targets_dict = collections.OrderedDict()

            targets_dict['drugbank_id'] = db_targets

            uniprot_id = polypeptide.get('id')
            # generate relationship between polypeptide and drug
            if is_enzyme:
                drug_targets = add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions,
                                                               organism, ref_article_list,
                                                               ref_link_list, ref_attachment_list, ref_textbooks_list,
                                                               known_action, uniprot_id, induction_strength,
                                                               inhibition_strength)
            else:
                drug_targets = add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions,
                                                               organism, ref_article_list,
                                                               ref_link_list, ref_attachment_list, ref_textbooks_list,
                                                               known_action, uniprot_id)

            # gather polypeptide information
            targets_dict['id'] = uniprot_id
            peptide_list.append(uniprot_id)
            targets_dict['id_source'] = polypeptide.get('source')
            targets_dict['name'] = polypeptide.findtext("{ns}name".format(ns=ns))
            targets_dict['general_function'] = polypeptide.findtext("{ns}general-function".format(ns=ns)).replace('\n',
                                                                                                                  '').replace(
                '\r', '')
            targets_dict['specific_function'] = polypeptide.findtext("{ns}specific-function".format(ns=ns)).replace(
                '\n', '').replace('\r', '')
            targets_dict['gene_name'] = polypeptide.findtext("{ns}gene-name".format(ns=ns)).replace('\n', '').replace(
                '\r', '')
            targets_dict['locus'] = polypeptide.findtext("{ns}locus".format(ns=ns)).replace('\n', '').replace('\r', '')
            targets_dict['cellular_location'] = polypeptide.findtext("{ns}cellular-location".format(ns=ns)).replace(
                '\n', '').replace('\r', '')
            targets_dict['transmembrane_regions'] = polypeptide.findtext(
                "{ns}transmembrane-regions".format(ns=ns)).replace('\n', '').replace('\r', '')
            targets_dict['signal_regions'] = polypeptide.findtext("{ns}signal-regions".format(ns=ns)).replace('\n',
                                                                                                              '').replace(
                '\r', '')
            targets_dict['theoretical_pi'] = polypeptide.findtext("{ns}theoretical-pi".format(ns=ns)).replace('\n',
                                                                                                              '').replace(
                '\r', '')
            targets_dict['molecular_weight'] = polypeptide.findtext("{ns}molecular-weight".format(ns=ns)).replace('\n',
                                                                                                                  '').replace(
                '\r', '')
            targets_dict['chromosome_location'] = polypeptide.findtext("{ns}chromosome-location".format(ns=ns)).replace(
                '\n', '').replace('\r', '')
            targets_dict['organism'] = organism

            xref_list = []
            for xref in polypeptide.findall('{ns}external-identifiers/{ns}external-identifier'.format(ns=ns)):
                resource = xref.findtext("{ns}resource".format(ns=ns))
                identifier = xref.findtext("{ns}identifier".format(ns=ns))
                xref_list.append(resource + '::' + identifier)
            targets_dict['xrefs'] = xref_list
            targets_dict['synonyms'] = [salt.text for salt in
                                        polypeptide.findall("{ns}synonyms/{ns}synonym".format(ns=ns))]
            # targets_dict['amino-acid-sequence'] = polypeptide.findtext("{ns}amino-acid-sequence".format(ns=ns)).replace(
            #     '\n', '').replace('\r', '')
            all_seq = polypeptide.findtext("{ns}amino-acid-sequence".format(ns=ns)).split('\n',
                                                                                          1) if polypeptide.findtext(
                "{ns}amino-acid-sequence".format(ns=ns)) != None else []
            if len(all_seq) == 2:
                all_seq[0] = all_seq[0].replace(' ', '_')
                all_seq[1] = all_seq[1].replace('\n', '')
            targets_dict['amino_acid_sequence'] = ' '.join(all_seq)

            all_seq = polypeptide.findtext("{ns}gene-sequence".format(ns=ns)).split('\n', 1) if polypeptide.findtext(
                "{ns}amino-acid-sequence".format(ns=ns)) != None else []
            if len(all_seq) == 2:
                all_seq[0] = all_seq[0].replace(' ', '_')
                all_seq[1] = all_seq[1].replace('\n', '')
            targets_dict['gene_sequence'] = ' '.join(all_seq)

            pfam_list = []
            for pfam in polypeptide.findall('{ns}pfams/{ns}pfam'.format(ns=ns)):
                name = pfam.findtext("{ns}name".format(ns=ns))
                identifier = pfam.findtext("{ns}identifier".format(ns=ns))
                pfam_list.append(identifier + '::' + name)
            targets_dict['pfams'] = pfam_list
            go_classifier_list = []
            for goClass in polypeptide.findall('{ns}go-classifiers/{ns}go-classifier'.format(ns=ns)):
                category = goClass.findtext("{ns}category".format(ns=ns))
                description = goClass.findtext("{ns}description".format(ns=ns))
                go_classifier_list.append(category + '::' + description)
            targets_dict['go_classifiers'] = go_classifier_list

            if not uniprot_id in dict_targets_ids:
                targets_info.append(targets_dict)
                dict_targets_ids[uniprot_id] = 1

            if not (db_ID, uniprot_id) in dict_drug_target:
                dict_drug_target[(db_ID, uniprot_id)] = drug_targets
            else:
                sys.exit()

        # if more then one peptide exists make a big node which is connected to drug and all peptites ar components of
        # this big one
        if len(peptide_list) > 1:
            drug_targets = collections.OrderedDict()
            targets_dict = collections.OrderedDict()

            targets_dict['drugbank_id'] = db_targets
            targets_dict['name'] = name_target
            targets_dict['organism'] = organism
            if not targets_dict['drugbank_id'] in maybe_not_protein_set:
                csv_decision_protein_file.writerow(
                    [targets_dict['name'], targets_dict['drugbank_id'], 'combined protein', 1])
                maybe_not_protein_set.add(targets_dict['drugbank_id'])
            if is_enzyme:
                drug_targets = add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions,
                                                               organism, ref_article_list,
                                                               ref_link_list, ref_attachment_list, ref_textbooks_list,
                                                               known_action, None, induction_strength,
                                                               inhibition_strength)
            else:
                drug_targets = add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions,
                                                               organism, ref_article_list,
                                                               ref_link_list, ref_attachment_list, ref_textbooks_list,
                                                               known_action)

            drug_targets_info.append(drug_targets)
            if not db_targets in dict_targets_ids:
                targets_info.append(targets_dict)
                dict_targets_ids[db_targets] = 1

            # prepare relationships between combined protein and its components peptides
            for peptide in peptide_list:

                if not (db_targets, peptide) in dict_has_component:
                    target_peptite = collections.OrderedDict()
                    target_peptite['target_id'] = db_targets
                    target_peptite['petide_id'] = peptide
                    dict_has_component[(db_targets, peptide)] = 1
                    has_components.append(target_peptite)

        # in case no polypeptide exists then it has only the drugbank id
        elif not polypetide_found:
            drug_targets = collections.OrderedDict()
            targets_dict = collections.OrderedDict()
            targets_dict['drugbank_id'] = db_targets
            targets_dict['name'] = targets.findtext("{ns}name".format(ns=ns))

            # the one without a uniprot id are  to classified into protein or not
            # enzyme, carrier and transporter are every time proteins
            if not targets_dict['drugbank_id'] in maybe_not_protein_set:
                if not is_target:
                    if not is_enzyme:
                        csv_decision_protein_file.writerow(
                            [targets_dict['name'], targets_dict['drugbank_id'], 'not target', 1])
                    else:
                        csv_decision_protein_file.writerow(
                            [targets_dict['name'], targets_dict['drugbank_id'], 'Enzyme', 1])
                # targets can be but this has to be checked manual
                else:
                    csv_decision_protein_file.writerow(
                        [targets_dict['name'], targets_dict['drugbank_id'], 'Target maybe no protein', 0])
                maybe_not_protein_set.add(targets_dict['drugbank_id'])
            if is_enzyme:
                drug_targets = add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions,
                                                               organism, ref_article_list,
                                                               ref_link_list, ref_attachment_list, ref_textbooks_list,
                                                               known_action, None, induction_strength,
                                                               inhibition_strength)
            else:
                drug_targets = add_information_into_dictionary(drug_targets, db_ID, db_targets, position, actions,
                                                               organism, ref_article_list,
                                                               ref_link_list, ref_attachment_list, ref_textbooks_list,
                                                               known_action)
            drug_targets_info.append(drug_targets)
            if not db_targets in dict_targets_ids:
                targets_info.append(targets_dict)
                dict_targets_ids[db_targets] = 1
        # this is when only one peptide exists
        else:
            for key, list_property in dict_drug_target.items():
                drug_targets_info.append(list_property)


counter = 0
# list of the different nodes and relationship pairs dictionaries
rows = list()
drug_interactions = list()
drug_pathways = list()
pathway_enzymes = list()
pathways = list()
snp_effects = list()
mutated_gene_proteins = list()
snp_adverse_drug_reactions = list()
drug_targets = list()
targets = list()
drug_enzymes = list()
enzymes = list()
drug_carriers = list()
carriers = list()
drug_transporters = list()
transporters = list()
drug_salts = list()
salts = list()
drug_products = list()
products = list()
metabolites = list()
has_components = list()
pharmacologic_classes = list()
pharmacologic_class_drug = list()
reactions_left_db = list()
reactions_left_dbmet = list()
reactions_right_db = list()
reactions_right_dbmet = list()
reactions_to_protein = list()

# dictionaries for the different node entities
reactions = list()
dict_pharmacologic_class = {}
dict_carrier_ids = {}
dict_enzyme_ids = {}
dict_target_ids = {}
dict_transporter_ids = {}
dict_products_ids = {}
dict_metabolites_ids = {}
dict_pathway_ids = {}
dict_mutated_gene_protein = {}
dict_has_component = {}
dict_pathway_enzyme = {}

"""
Run through each drug in the xml and parse the information into the different dictionaries. Most are the drug 
information but some are also the salt, product, target, enzyme, carrier, transporter, reaction, gene_variant, 
metabolite, atc structure and pathway.
Drug contains information about identifier, type, cas_number, alternative drugbank ids, name, description, group, atc
codes, inchi, inchikey, synonyms, unii,different references, synthesis_reference, indication, pharmacodynamics,
mechanism_of_action, toxicity, metabolism, absorption, half_life, protein_binding, route_of_elimination, 
volume_of_distribution, clearance , the different classification classes, international brands name company, mixtures 
name ingredients, packagers name url, prices description cost unit, affected organisms, dosages form route strength, 
atc code levels, ahfs codes, pdb entries,fda label, msds, patents number country approved expires pediatric extension, 
food interaction, sequences, calculated properties kind value source, experimental properties kind value source, 
external identifiers and external links resource url.  
"""
for i, drug in enumerate(root):

    counter += 1
    row = collections.OrderedDict()

    assert drug.tag == ns + 'drug'

    row['type'] = drug.get('type')
    row['drugbank_id'] = drug.findtext(ns + "drugbank-id[@primary='true']")
    db_ID = drug.findtext(ns + "drugbank-id[@primary='true']")

    row['cas_number'] = drug.findtext(ns + "cas-number")
    #    print(row['drugbank_id'])

    alternative_ids = [group.text for group in
                       drug.findall("{ns}drugbank-id".format(ns=ns))]
    alternative_ids.remove(db_ID)
    row['alternative_ids'] = alternative_ids

    row['name'] = drug.findtext(ns + "name")

    row['description'] = drug.findtext(ns + "description").replace('\n', '').replace('\r', '')
    #    print(row['description'])
    row['groups'] = [group.text for group in
                     drug.findall("{ns}groups/{ns}group".format(ns=ns))]
    row['atc_codes'] = [code.get('code') for code in
                        drug.findall("{ns}atc-codes/{ns}atc-code".format(ns=ns))]
    # prepare atc code for extracting atc structure
    for atc_code in drug.findall("{ns}atc-codes/{ns}atc-code".format(ns=ns)):
        atc_id = atc_code.get('code')
        if atc_id not in dict_atc_nodes:
            dict_atc_nodes[atc_id] = ''

        atc_before = atc_id

        for general_atc in atc_code.findall("{ns}level".format(ns=ns)):
            atc_id = general_atc.get('code')
            dict_atc_nodes[atc_id] = general_atc.text
            set_atc_edges.add((atc_id, atc_before))
            atc_before = atc_id

    #    row['categories'] = [x.findtext(ns + 'category') for x in
    #        drug.findall("{ns}categories/{ns}category".format(ns = ns))]
    row['inchi'] = drug.findtext(inchi_template.format(ns=ns))
    row['inchikey'] = drug.findtext(inchikey_template.format(ns=ns))
    row['smiles'] = drug.findtext(smiles_template.format(ns=ns))
    formular_exp = drug.findtext(molecular_formula_experimental_template.format(ns=ns))
    formular_calc = drug.findtext(molecular_formula_template.format(ns=ns))
    row['formula'] = formular_exp if formular_exp else formular_calc
    row['synonyms'] = [salt.text for salt in
                       drug.findall("{ns}synonyms/{ns}synonym".format(ns=ns))]
    row['unii'] = drug.findtext(ns + "unii")
    row['state'] = drug.findtext(ns + "state")
    row['general_references_articles_reference_id_pubmed_citation'] = []
    # combine each information to one big string
    for article in drug.iterfind('{ns}general-references/{ns}articles/{ns}article'.format(ns=ns)):
        pubmed_id = article.findtext("{ns}pubmed-id".format(ns=ns))
        citation = article.findtext("{ns}citation".format(ns=ns))
        ref_id = article.findtext("{ns}ref-id".format(ns=ns))
        dict_reference_id_to_infos[ref_id] = [pubmed_id, citation]
        combined = ref_id + '::' + pubmed_id + '::' + citation
        row['general_references_articles_reference_id_pubmed_citation'].append(combined)

    row['general_references_textbooks_reference_id_isbn_citation'] = []
    # combine each information to one big string
    for article in drug.iterfind('{ns}general-references/{ns}textbooks/{ns}textbook'.format(ns=ns)):
        isbn = article.findtext("{ns}isbn".format(ns=ns))
        citation = article.findtext("{ns}citation".format(ns=ns))
        ref_id = article.findtext("{ns}ref-id".format(ns=ns))
        dict_reference_id_to_infos[ref_id] = [isbn, citation]
        combined = ref_id + '::' + isbn + '::' + citation
        row['general_references_textbooks_reference_id_isbn_citation'].append(combined)

    row['general_references_links_reference_id_title_url'] = []
    # combine each information to one big string
    for article in drug.iterfind('{ns}general-references/{ns}links/{ns}link'.format(ns=ns)):
        title = article.findtext("{ns}title".format(ns=ns))
        url = article.findtext("{ns}url".format(ns=ns))
        ref_id = article.findtext("{ns}ref-id".format(ns=ns))
        dict_reference_id_to_infos[ref_id] = [url, title]
        combined = ref_id + '::' + title + '::' + url
        row['general_references_links_reference_id_title_url'].append(combined)

    row['general_references_attachment_reference_id_title_url'] = []
    # combine each information to one big string
    for article in drug.iterfind('{ns}general-references/{ns}attachments/{ns}attachment'.format(ns=ns)):
        title = article.findtext("{ns}title".format(ns=ns))
        url = article.findtext("{ns}url".format(ns=ns))
        ref_id = article.findtext("{ns}ref-id".format(ns=ns))
        dict_reference_id_to_infos[ref_id] = [url, title]
        combined = ref_id + '::' + title + '::' + url
        row['general_references_attachment_reference_id_title_url'].append(combined)

    row['synthesis_reference'] = drug.findtext(ns + "synthesis-reference").replace('\n', '').replace('\r', '')
    row['indication'] = drug.findtext(ns + "indication").replace('\n', '').replace('\r', '')
    row['pharmacodynamics'] = drug.findtext(ns + "pharmacodynamics").replace('\n', '').replace('\r', '')
    row['mechanism_of_action'] = drug.findtext(ns + "mechanism-of-action").replace('\n', '').replace('\r', '')
    row['toxicity'] = drug.findtext(ns + "toxicity").replace('\r\n', ' ')
    row['metabolism'] = drug.findtext(ns + "metabolism").replace('\n', '').replace('\r', '')
    row['absorption'] = drug.findtext(ns + "absorption").replace('\n', '').replace('\r', '')
    row['half_life'] = drug.findtext(ns + "half-life").replace('\n', '').replace('\r', '')
    row['protein_binding'] = drug.findtext(ns + "protein-binding").replace('\n', '').replace('\r', '')
    row['route_of_elimination'] = drug.findtext(ns + "route-of-elimination").replace('\n', '').replace('\r', '')
    row['volume_of_distribution'] = drug.findtext(ns + "volume-of-distribution").replace('\n', '').replace('\r', '')
    row['clearance'] = drug.findtext(ns + "clearance").replace('\n', '').replace('\r', '')

    row['classification_description'] = drug.findtext(ns + "classification/{ns}description".format(ns=ns))
    row['classification_direct_parent'] = drug.findtext(ns + "classification/{ns}direct-parent".format(ns=ns))
    row['classification_kingdom'] = drug.findtext(ns + "classification/{ns}kingdom".format(ns=ns))
    row['classification_superclass'] = drug.findtext(ns + "classification/{ns}superclass".format(ns=ns))
    row['classification_class'] = drug.findtext(ns + "classification/{ns}class".format(ns=ns))
    row['classification_subclass'] = drug.findtext(ns + "classification/{ns}subclass".format(ns=ns))
    row['classification_substituent'] = [group.text for group in
                                         drug.findall("{ns}classification/{ns}substituent".format(ns=ns))]
    #    drug.findtext(ns + "classification/{ns}substituent".format(ns = ns))
    row['classification_alternative_parent'] = [group.text for group in
                                                drug.findall("{ns}classification/{ns}alternative-parent".format(ns=ns))]
    #    drug.findtext(ns + "classification/{ns}alternative-parent".format(ns = ns))

    """
    The salt node has the information id, name, unii. inchikey, cas nmber, average mass and monoisotopic mass.
    Also the relationship information are extract between drug and salt.
    """
    for salt in drug.iterfind('{ns}salts/{ns}salt'.format(ns=ns)):
        salt_dict = collections.OrderedDict()
        drug_salt = collections.OrderedDict()
        drug_id = salt.findtext("{ns}drugbank-id".format(ns=ns))
        salt_dict['id'] = drug_id
        drug_salt['salt_id'] = drug_id
        drug_salt['drug_id'] = db_ID
        salt_dict['name'] = salt.findtext("{ns}name".format(ns=ns))
        salt_dict['unii'] = salt.findtext("{ns}unii".format(ns=ns))
        salt_dict['inchikey'] = salt.findtext("{ns}inchikey".format(ns=ns))
        salt_dict['cas_number'] = salt.findtext("{ns}cas-number".format(ns=ns))
        salt_dict['average_mass'] = salt.findtext("{ns}average-mass".format(ns=ns))
        salt_dict['monoisotopic_mass'] = salt.findtext("{ns}monoisotopic-mass".format(ns=ns))

        drug_salts.append(drug_salt)
        salts.append(salt_dict)

    """
        The Product node has the information id (ndc code/dpd id/ema number), name, labeller. started_marketing_on, 
        ended_marketing_on, dosage_form, strength, route, fda_application_number, generic, over_the_counter, approved, 
        country and source.
        Also the relationship information are extract between drug and product.
        """
    for product in drug.iterfind('{ns}products/{ns}product'.format(ns=ns)):
        products_dict = collections.OrderedDict()
        drug_products_dict = collections.OrderedDict()
        ndc_product_code = product.findtext("{ns}ndc-product-code".format(ns=ns))
        dpd_id = product.findtext("{ns}dpd-id".format(ns=ns))
        ema_ma_number = product.findtext("{ns}ema-ma-number".format(ns=ns))
        #        drug_products_dict['ndc_product_code']=ndc_product_code
        drug_products_dict['drugbank_id'] = db_ID
        #        drug_products_dict['dpd_id']=dpd_id
        #        drug_products_dict['ema_ma_number'] = ema_ma_number
        if ndc_product_code == '' and dpd_id == '' and ema_ma_number == '':
            print('ohje')
            print(db_ID)
        # one of ema, dpd or ndc is the unique identifier
        if dpd_id != '':
            unique_id = dpd_id
        elif ndc_product_code != '':
            unique_id = ndc_product_code
        else:
            unique_id = ema_ma_number
        drug_products_dict['partner_id'] = unique_id
        drug_products.append(drug_products_dict)
        if unique_id in dict_products_ids:
            continue

        dict_products_ids[unique_id] = ''

        products_dict['id'] = unique_id
        products_dict['name'] = product.findtext("{ns}name".format(ns=ns))
        products_dict['labeller'] = product.findtext("{ns}labeller".format(ns=ns))
        products_dict['ndc_id'] = product.findtext("{ns}ndc-id".format(ns=ns))
        products_dict['ndc_product_code'] = ndc_product_code
        products_dict['dpd_id'] = dpd_id
        products_dict['ema_product_code'] = product.findtext("{ns}ema-product-code".format(ns=ns))
        products_dict['ema_ma_number'] = ema_ma_number
        products_dict['started_marketing_on'] = product.findtext("{ns}started-marketing-on".format(ns=ns))
        products_dict['ended_marketing_on'] = product.findtext("{ns}ended-marketing-on".format(ns=ns))
        products_dict['dosage_form'] = product.findtext("{ns}dosage-form".format(ns=ns))
        products_dict['strength'] = product.findtext("{ns}strength".format(ns=ns))
        products_dict['route'] = product.findtext("{ns}route".format(ns=ns))
        products_dict['fda_application_number'] = product.findtext("{ns}fda-application-number".format(ns=ns))
        products_dict['generic'] = product.findtext("{ns}generic".format(ns=ns))
        products_dict['over_the_counter'] = product.findtext("{ns}over-the-counter".format(ns=ns))
        products_dict['approved'] = product.findtext("{ns}approved".format(ns=ns))
        products_dict['country'] = product.findtext("{ns}country".format(ns=ns))
        products_dict['source'] = product.findtext("{ns}source".format(ns=ns))
        #        print(products_dict)

        products.append(products_dict)
    row['international_brands_name_company'] = []
    for international_brand in drug.iterfind('{ns}international-brands/{ns}international-brand'.format(ns=ns)):
        # combine each information to one big string
        name = international_brand.findtext("{ns}name".format(ns=ns))
        company = international_brand.findtext("{ns}company".format(ns=ns))
        combined = name + '::' + company
        row['international_brands_name_company'].append(combined)

    row['mixtures_name_ingredients'] = []
    dict_mixtures_ingredients_combination_names = {}
    # make for all ingredients and supplemental-ingredients an dictionary with all names this combination can have
    for part in drug.iterfind('{ns}mixtures/{ns}mixture'.format(ns=ns)):
        name = part.findtext("{ns}name".format(ns=ns))
        ingredients = part.findtext("{ns}ingredients".format(ns=ns))
        supplemental_ingredients = part.findtext("{ns}supplemental-ingredients".format(ns=ns))
        if (len(ingredients) == 0):
            print(ingredients)
            print(name)

        if (ingredients, supplemental_ingredients) in dict_mixtures_ingredients_combination_names:
            dict_mixtures_ingredients_combination_names[(ingredients, supplemental_ingredients)].add(name)
        else:
            dict_mixtures_ingredients_combination_names[(ingredients, supplemental_ingredients)] = {name}
    # make for every combination a string and add to list
    for (ingredient, supplemental_ingredient), names in dict_mixtures_ingredients_combination_names.items():
        names_string = '//'.join(names)
        combined = names_string + '::' + ingredient + ' + ' + supplemental_ingredient if supplemental_ingredient is not None else names_string + '::' + ingredient

        row['mixtures_name_ingredients'].append(combined)

    row['packagers_name_url'] = []
    for part in drug.iterfind('{ns}packagers/{ns}packager'.format(ns=ns)):
        # combine each information to one big string
        name = part.findtext("{ns}name".format(ns=ns))
        url = part.findtext("{ns}url".format(ns=ns))
        combined = name + '::' + url
        row['packagers_name_url'].append(combined)

    row['manufacturers'] = [salt.text for salt in
                            drug.findall("{ns}manufacturers/{ns}manufacturer".format(ns=ns))]

    row['prices_description_cost_unit'] = []
    for part in drug.iterfind('{ns}prices/{ns}price'.format(ns=ns)):
        # combine each information to one big string
        description = part.findtext("{ns}description".format(ns=ns))
        cost = part.find("{ns}cost".format(ns=ns)).get('currency') + ':' + part.findtext("{ns}cost".format(ns=ns))
        unit = part.findtext("{ns}unit".format(ns=ns))
        combined = description + '::' + cost + '::' + unit
        row['prices_description_cost_unit'].append(combined)

    """ 
    The category ids are from the tsv file but get additional information like mesh id and name.
    Add also relationship between drug and category.
    """
    for part in drug.iterfind('{ns}categories/{ns}category'.format(ns=ns)):

        category = part.findtext("{ns}category".format(ns=ns))

        category = ' '.join(category.split())
        if category in dict_category_name_to_id:
            drugbank_category_id = dict_category_name_to_id[category]
        else:
            print('Category')
            print(category)
            print(db_ID)
        mesh_id = part.findtext("{ns}mesh-id".format(ns=ns))

        drug_pharmacological_class_dict = collections.OrderedDict()
        drug_pharmacological_class_dict['drugbank_id'] = db_ID
        drug_pharmacological_class_dict['category'] = drugbank_category_id
        pharmacologic_class_drug.append(drug_pharmacological_class_dict)
        if not drugbank_category_id in dict_pharmacologic_class:
            pharmacologic_class_dict = collections.OrderedDict()
            pharmacologic_class_dict['id'] = drugbank_category_id
            pharmacologic_class_dict['mesh_id'] = mesh_id
            pharmacologic_class_dict['name'] = category
            pharmacologic_classes.append(pharmacologic_class_dict)
            dict_pharmacologic_class[drugbank_category_id] = mesh_id

    row['affected_organisms'] = [salt.text for salt in
                                 drug.findall("{ns}affected-organisms/{ns}affected-organism".format(ns=ns))]

    row['dosages_form_route_strength'] = []
    for part in drug.iterfind('{ns}dosages/{ns}dosage'.format(ns=ns)):
        # combine each information to one big string
        form = part.findtext("{ns}form".format(ns=ns))
        route = part.findtext("{ns}route".format(ns=ns))
        strength = part.findtext("{ns}strength".format(ns=ns))
        combined = form + '::' + route + '::' + strength
        row['dosages_form_route_strength'].append(combined)

    row['atc_code_levels'] = [code.get('code') for code in
                              drug.findall("{ns}atc-codes/{ns}atc-code/{ns}level".format(ns=ns))]

    row['ahfs_codes'] = [salt.text for salt in
                         drug.findall("{ns}ahfs-codes/{ns}ahfs-code".format(ns=ns))]

    row['pdb_entries'] = [salt.text for salt in
                          drug.findall("{ns}pdb-entries/{ns}pdb-entry".format(ns=ns))]
    row['fda_label'] = drug.findtext(ns + "fda-label").replace('\n', '').replace('\r', '') if not drug.findtext(
        ns + "fda-label") is None else ''
    row['msds'] = drug.findtext(ns + "msds").replace('\n', '').replace('\r', '') if not drug.findtext(
        ns + "msds") is None else ''

    row['patents_number_country_approved_expires_pediatric_extension'] = []
    for part in drug.iterfind('{ns}patents/{ns}patent'.format(ns=ns)):
        # combine each information to one big string
        number = part.findtext("{ns}number".format(ns=ns))
        country = part.findtext("{ns}country".format(ns=ns))
        approved = part.findtext("{ns}approved".format(ns=ns))
        expires = part.findtext("{ns}expires".format(ns=ns))
        pediatric_extension = part.findtext("{ns}pediatric-extension".format(ns=ns))
        combined = number + '::' + country + '::' + approved + '::' + expires + '::' + pediatric_extension
        row['patents_number_country_approved_expires_pediatric_extension'].append(combined)

    row['food_interaction'] = [salt.text for salt in
                               drug.findall("{ns}food-interactions/{ns}food-interaction".format(ns=ns))]

    # add all drug-drug interaction
    for part in drug.iterfind('{ns}drug-interactions/{ns}drug-interaction'.format(ns=ns)):
        drug_interaction = collections.OrderedDict()
        drug_interaction['DB_ID1'] = db_ID
        drug_interaction['DB_ID2'] = part.findtext("{ns}drugbank-id".format(ns=ns))
        drug_interaction['description'] = part.findtext("{ns}description".format(ns=ns))
        drug_interactions.append(drug_interaction)

    # get all drug sequence information
    all_seq = [seq.text.split('\n', 1) for seq in
               drug.findall("{ns}sequences/{ns}sequence".format(ns=ns))] if drug.findtext(
        "{ns}sequences/{ns}sequence".format(ns=ns)) != None else []

    counter = 0
    # prepare the sequence such they would not make problems in tsv files
    for all_spliter in all_seq:
        all_spliter[0] = all_spliter[0].replace(' ', '_').replace('|', '/')
        all_spliter[1] = all_spliter[1].replace('\n', '')
        all_seq[counter] = ' '.join(all_spliter)
        counter += 1
    row['sequences'] = all_seq

    #    row['sequences']= [seq.text.replace('\n',' ',1).replace('\r',' ',1).replace('\t','').replace('\n','').replace('\r','') for seq in drug.findall("{ns}sequences/{ns}sequence".format(ns = ns))] if drug.findtext("{ns}sequences/{ns}sequence".format(ns = ns))!=None else []
    row['calculated_properties_kind_value_source'] = []
    for part in drug.iterfind('{ns}calculated-properties/{ns}property'.format(ns=ns)):
        # combine each information to one big string
        kind = part.findtext("{ns}kind".format(ns=ns))
        value = part.findtext("{ns}value".format(ns=ns))
        source = part.findtext("{ns}source".format(ns=ns))
        combined = kind + '::' + value + '::' + source
        row['calculated_properties_kind_value_source'].append(combined)

    row['experimental_properties_kind_value_source'] = []
    for part in drug.iterfind('{ns}experimental-properties/{ns}property'.format(ns=ns)):
        # combine each information to one big string
        kind = part.findtext("{ns}kind".format(ns=ns))
        value = part.findtext("{ns}value".format(ns=ns))
        source = part.findtext("{ns}source".format(ns=ns))
        combined = kind + '::' + value + '::' + source
        row['experimental_properties_kind_value_source'].append(combined)

    # prepare a list of external for with form: [source:id, source:id, ...]
    extern_ids_source = [salt.text for salt in
                         drug.findall("{ns}external-identifiers/{ns}external-identifier/{ns}resource".format(ns=ns))]
    extern_ids = [salt.text for salt in
                  drug.findall("{ns}external-identifiers/{ns}external-identifier/{ns}identifier".format(ns=ns))]
    row['external_identifiers'] = [i + ':' + j for i, j in zip(extern_ids_source, extern_ids)]

    row['external_links_resource_url'] = []
    for part in drug.iterfind('{ns}external-links/{ns}external-link'.format(ns=ns)):
        # combine each information to one big string
        resource = part.findtext("{ns}resource".format(ns=ns))
        url = part.findtext("{ns}url".format(ns=ns))
        combined = resource + '::' + url
        row['external_links_resource_url'].append(combined)

    """
    Generathe the pathway node with properties: pathway id (smpdb id), name and category.
    Additionally, the the drug pathway is added to the relationship drug-pathway. However, in pathway are more drugs. 
    This is also used for generate pathway-drug relationships. Also, in pathway are additonal information about enzymes.
    This information is used to generate realtionships between pathway and enzyme.
    """
    for part in drug.iterfind('{ns}pathways/{ns}pathway'.format(ns=ns)):
        pathway = collections.OrderedDict()
        drug_pathway = collections.OrderedDict()

        smpdb_id = part.findtext("{ns}smpdb-id".format(ns=ns))
        if smpdb_id not in dict_pathway_ids:
            name = part.findtext("{ns}name".format(ns=ns))
            category = part.findtext("{ns}category".format(ns=ns))
            pathway['pathway_id'] = smpdb_id
            pathway['name'] = name
            pathway['category'] = category

            pathways.append(pathway)
            dict_pathway_ids[smpdb_id] = ''

        drug_pathway['drugbank_id'] = db_ID
        drug_pathway['pathway_id'] = smpdb_id

        # add all drugbank id that are associated to this pathway to list
        for drug_ids in part.findall('{ns}drugs/{ns}drug'.format(ns=ns)):
            drug_pathway_addition = collections.OrderedDict()
            drug_pathway_addition['drugbank_id'] = drug_ids.findtext("{ns}drugbank-id".format(ns=ns))
            drug_pathway_addition['pathway_id'] = smpdb_id
            if not drug_pathway_addition in drug_pathways:
                drug_pathways.append(drug_pathway_addition)

        if not drug_pathway in drug_pathways:
            drug_pathways.append(drug_pathway)

        # generate pathway-enzyme relationships
        for enzym in part.findall('{ns}enzymes/{ns}uniprot-id'.format(ns=ns)):

            pathway_enzym = collections.OrderedDict()
            uniprot_id = enzym.text
            #            if smpdb_id=='SMP63607':
            #                print(uniprot_id )
            #                print(db_ID)
            #            uniprot_id=uniprot_id.replace(' ','')
            if not (smpdb_id, uniprot_id) in dict_pathway_enzyme:
                pathway_enzym['pathway_id'] = smpdb_id
                pathway_enzym['uniprot_id'] = uniprot_id
                pathway_enzymes.append(pathway_enzym)
                dict_pathway_enzyme[(smpdb_id, uniprot_id)] = 1

    """
    Reaction is an edge-node. This means it is an edge, but because it is not a one-to-one relationship it get there own
    tsv file. A reaction has as property a self generated id and a sequence.  Then the Reaction has a left element and
    a right element. The left and right element can be a metabolite or a drug. This generate the relationships.
    Howevere, the metabolite get his properties identifier and name from here. However, reaction has also enzymes in the
    reaction to produce out of the left the right element. These relationships are also added.
    """

    for part in drug.iterfind('{ns}reactions/{ns}reaction'.format(ns=ns)):
        reaction = collections.OrderedDict()
        # information for reaction node
        reaction['sequence'] = part.findtext("{ns}sequence".format(ns=ns))
        reaction['id'] = counter_reaction_ids
        reaction['start_drugbank_id'] = db_ID
        reaction_id = counter_reaction_ids
        counter_reaction_ids += 1
        left = part.findtext("{ns}left-element/{ns}drugbank-id".format(ns=ns))
        right = part.findtext("{ns}right-element/{ns}drugbank-id".format(ns=ns))
        reactions.append(reaction)

        # information for left edge and maybe generate a metabolite node
        reaction_to_left = collections.OrderedDict()
        reaction_to_left['reaction_id'] = reaction_id
        if left[0:5] == 'DBMET':
            reaction_to_left['meta_id'] = left
            reactions_left_dbmet.append(reaction_to_left)
            if not left in dict_metabolites_ids:
                metabolite = collections.OrderedDict()
                metabolite['drugbank_id'] = left
                metabolite['name'] = part.findtext("{ns}right-element/{ns}name".format(ns=ns))
                dict_metabolites_ids[left] = ''
                metabolites.append(metabolite)
        else:
            reaction_to_left['drug_id'] = left
            reactions_left_db.append(reaction_to_left)

        # information for right edge and maybe generate a metabolite node
        reaction_to_right = collections.OrderedDict()
        reaction_to_right['reaction_id'] = reaction_id
        if right[0:5] == 'DBMET':
            reaction_to_right['meta_id'] = right
            reactions_right_dbmet.append(reaction_to_right)
            if not right in dict_metabolites_ids:
                metabolite = collections.OrderedDict()
                metabolite['drugbank_id'] = right
                metabolite['name'] = part.findtext("{ns}right-element/{ns}name".format(ns=ns))
                dict_metabolites_ids[right] = ''
                metabolites.append(metabolite)
        else:
            reaction_to_right['drug_id'] = right
            reactions_right_db.append(reaction_to_right)

        enzymes_list = []
        # prepare relationships between enzymes and reactions
        for enzyme in part.findall('{ns}enzymes/{ns}enzyme'.format(ns=ns)):
            reaction_to_protein = collections.OrderedDict()

            reaction_to_protein['reaction_id'] = reaction_id

            enzyme_drugbank_id = enzyme.findtext("{ns}drugbank-id".format(ns=ns))
            enzyme_uniprot_id = enzyme.findtext("{ns}uniprot-id".format(ns=ns))
            reaction_to_protein['protein_id'] = enzyme_uniprot_id
            reaction_to_protein['protein_id_db'] = enzyme_uniprot_id
            enzymes_list.append(enzyme_drugbank_id + ':' + enzyme_uniprot_id)
            reactions_to_protein.append(reaction_to_protein)

    """
    There exists mutated gene or protein information nodes with properties protein name, gene symbol, uniprot id,
    rs id, allele, defining change and a id (rs id or gene symbol). The relationship between drugbank and the  mutated 
    gene or protein has additional information: description pubmed id and type.
    """
    for part in drug.iterfind('{ns}snp-effects/{ns}effect'.format(ns=ns)):
        snp_effect = collections.OrderedDict()
        mutated_gene_protein = collections.OrderedDict()

        uniprot_id = part.findtext("{ns}uniprot-id".format(ns=ns))
        rs_id = part.findtext("{ns}rs-id".format(ns=ns))
        gene_symbol = part.findtext("{ns}gene-symbol".format(ns=ns))
        # gather information for relationship
        snp_effect['drugbank_id'] = db_ID
        # check for unique identifier for mutated gene or protein
        if rs_id != '':
            snp_effect['partner_id'] = rs_id
            unique_id = rs_id
        else:
            snp_effect['partner_id'] = gene_symbol
            unique_id = gene_symbol
        snp_effect['description'] = part.findtext("{ns}description".format(ns=ns))
        snp_effect['pubmed_id'] = part.findtext("{ns}pubmed-id".format(ns=ns))
        snp_effect['type'] = 'Effect Directly Studied'
        # generate the mutated gene or protein node information
        if unique_id not in dict_mutated_gene_protein:
            mutated_gene_protein['protein_name'] = part.findtext("{ns}protein-name".format(ns=ns))
            mutated_gene_protein['gene_symbol'] = part.findtext("{ns}gene-symbol".format(ns=ns))
            mutated_gene_protein['uniprot_id'] = part.findtext("{ns}uniprot-id".format(ns=ns))
            mutated_gene_protein['rs_id'] = part.findtext("{ns}rs-id".format(ns=ns))
            mutated_gene_protein['allele'] = part.findtext("{ns}allele".format(ns=ns))
            mutated_gene_protein['defining_change'] = part.findtext("{ns}defining-change".format(ns=ns))
            mutated_gene_protein['connection_id'] = unique_id

            dict_mutated_gene_protein[unique_id] = ''

            mutated_gene_proteins.append(mutated_gene_protein)
        snp_effects.append(snp_effect)

    """
        There exists mutated gene or protein information nodes with properties protein name, gene symbol, uniprot id,
        rs id, allele, defining change and a id (rs id or gene symbol). The relationship between drugbank and the mutated 
        gene or protein has additional information: description pubmed id and type.
        """
    for part in drug.iterfind('{ns}snp-adverse-drug-reactions/{ns}reaction'.format(ns=ns)):
        snp_adverse_drug_reaction = collections.OrderedDict()
        mutated_gene_protein = collections.OrderedDict()

        uniprot_id = part.findtext("{ns}uniprot-id".format(ns=ns))
        rs_id = part.findtext("{ns}rs-id".format(ns=ns))
        gene_symbol = part.findtext("{ns}gene-symbol".format(ns=ns))

        # gather information for relationship
        snp_adverse_drug_reaction['drugbank_id'] = db_ID
        # check for unique identifier for mutated gene or protein
        if rs_id != '':
            snp_adverse_drug_reaction['partner_id'] = rs_id
            unique_id = rs_id
        else:
            snp_adverse_drug_reaction['partner_id'] = gene_symbol
            unique_id = gene_symbol

        snp_adverse_drug_reaction['description'] = part.findtext("{ns}description".format(ns=ns))
        snp_adverse_drug_reaction['pubmed_id'] = part.findtext("{ns}pubmed-id".format(ns=ns))
        snp_adverse_drug_reaction['type'] = 'ADR Directly Studied'
        # generate the mutated gene or protein node information
        if unique_id not in dict_mutated_gene_protein:
            mutated_gene_protein['protein_name'] = part.findtext("{ns}protein-name".format(ns=ns))
            mutated_gene_protein['gene_symbol'] = part.findtext("{ns}gene-symbol".format(ns=ns))
            mutated_gene_protein['uniprot_id'] = part.findtext("{ns}uniprot-id".format(ns=ns))
            mutated_gene_protein['rs_id'] = part.findtext("{ns}rs-id".format(ns=ns))
            mutated_gene_protein['allele'] = part.findtext("{ns}allele".format(ns=ns))
            mutated_gene_protein['defining_changes'] = part.findtext("{ns}adverse-reaction".format(ns=ns))
            mutated_gene_protein['connection_id'] = unique_id

            dict_mutated_gene_protein[unique_id] = ''

            mutated_gene_proteins.append(mutated_gene_protein)
        snp_adverse_drug_reactions.append(snp_adverse_drug_reaction)

    # target
    gather_target_infos( drug,'{ns}targets/{ns}target', drug_targets, targets, dict_target_ids, db_ID, False, True)

    # enzymes
    gather_target_infos(drug,'{ns}enzymes/{ns}enzyme', drug_enzymes, enzymes, dict_enzyme_ids, db_ID, True, False)

    # carries
    gather_target_infos(drug,'{ns}carriers/{ns}carrier', drug_carriers, carriers, dict_carrier_ids, db_ID, False, False)

    # transporter
    gather_target_infos(drug,'{ns}transporters/{ns}transporter', drug_transporters, transporters, dict_transporter_ids,
                        db_ID, False, False)

    # Add drug aliases
    aliases = {
        elem.text for elem in
        drug.findall("{ns}international-brands/{ns}international-brand".format(ns=ns)) +
        drug.findall("{ns}synonyms/{ns}synonym[@language='English']".format(ns=ns)) +
        drug.findall("{ns}international-brands/{ns}international-brand".format(ns=ns)) +
        drug.findall("{ns}products/{ns}product/{ns}name".format(ns=ns))

    }
    aliases.add(row['name'])
    row['aliases'] = sorted(aliases)
    #    print(row)

    rows.append(row)
#    if db_ID=='DB01470':
##        print(drug.findtext(ns + "name"))
#        file_test=open('data/tets_name.csv','w',encoding='utf8')
#        file_test.write(drug.findtext(ns + "name"))
#        file_test.close()
#        break

print('number of entries in drugbank:' + str(counter))
print(datetime.datetime.now())


def collapse_list_values(row):
    """
    Do some preparation for information with list. Like remove empty values and make the list to a string
    :param row:
    :return:
    """
    for key, value in row.items():
        if isinstance(value, list):
            #            print(key)
            #            print(value)
            i = 0
            if key == 'inchikeys' or key == 'uniis' or key == 'extra_names' or key == 'target' or key == 'transporter':
                list_delete = []
                for val in value:
                    if val == None:
                        list_delete.insert(0, i)
                    i += 1
                for j in list_delete:
                    del value[j]

            if len(value) > 0:
                string_value = '||'.join(value)
                row[key] = string_value.replace('\t', '').replace('\n', '').replace('\r', '')
            else:
                row[key] = ''

    return row


# prepare the list information
def preparation(list_information):
    list_information = list(map(collapse_list_values, list_information))
    return list_information


print(datetime.datetime.now())
print('preparation of information lists')
# prepare the information from the different different dictionaries
rows = preparation(rows)
drug_interactions = preparation(drug_interactions)
drug_pathways = preparation(drug_pathways)
pathway_enzymes = preparation(pathway_enzymes)
pathways = preparation(pathways)
reactions = preparation(reactions)
snp_effects = preparation(snp_effects)
mutated_gene_proteins = preparation(mutated_gene_proteins)
snp_adverse_drug_reactions = preparation(snp_adverse_drug_reactions)
drug_targets = preparation(drug_targets)
targets = preparation(targets)
drug_enzymes = preparation(drug_enzymes)
enzymes = preparation(enzymes)
drug_carriers = preparation(drug_carriers)
carriers = preparation(carriers)
drug_transporters = preparation(drug_transporters)
transporters = preparation(transporters)
drug_salts = preparation(drug_salts)
salts = preparation(salts)
products = preparation(products)
drug_products = preparation(drug_products)
metabolites = preparation(metabolites)
has_components = preparation(has_components)
pharmacologic_classes = preparation(pharmacologic_classes)
pharmacologic_class_drug = preparation(pharmacologic_class_drug)


# preparation and generation of an tsv
def generate_tsv_file(columns, list_information, file_name):
    # print(list_information)
    # print(columns)
    drugbank_information = pandas.DataFrame.from_dict(list_information)[columns]
    drugbank_information.head()

    path = os.path.join('drugbank', file_name)
    drugbank_information.to_csv(path, sep='\t', index=False, encoding='utf-8')


print(datetime.datetime.now())
print('malsehen')
# tsv header
columns = ['drugbank_id', 'alternative_ids', 'name', 'cas_number', 'unii', 'atc_codes',
           'state', 'groups', 'general_references_links_reference_id_title_url',
           'general_references_attachment_reference_id_title_url',
           'general_references_textbooks_reference_id_isbn_citation',
           'general_references_articles_reference_id_pubmed_citation',
           'synthesis_reference', 'indication', 'pharmacodynamics', 'mechanism_of_action', 'toxicity',
           'metabolism', 'absorption', 'half_life', 'protein_binding', 'route_of_elimination',
           'volume_of_distribution', 'clearance', 'classification_subclass', 'classification_class',
           'classification_superclass', 'classification_kingdom', 'classification_direct_parent',
           'classification_description', 'synonyms', 'international_brands_name_company',
           'mixtures_name_ingredients', 'packagers_name_url', 'manufacturers', 'prices_description_cost_unit',
           'affected_organisms', 'dosages_form_route_strength', 'atc_code_levels', 'ahfs_codes',
           'pdb_entries', 'fda_label', 'msds', 'patents_number_country_approved_expires_pediatric_extension',
           'food_interaction', 'sequences', 'calculated_properties_kind_value_source',
           'experimental_properties_kind_value_source', 'external_identifiers',
           'external_links_resource_url', 'type',
           'classification_alternative_parent', 'classification_substituent', 'inchi',
           'inchikey', 'smiles', 'formula', 'description']
# ['drugbank_id', 'drugbank_ids' ,'name', 'type', 'cas_number' , 'groups', 'atc_codes', 'categories', 'inchikey', 'inchi','inchikeys', 'synonyms', 'unii','uniis', 'external_identifiers','extra_names', 'brands', 'molecular_formula','molecular_formular_experimental','sequences','drug_interaction', 'drug_interaction_description','food_interaction', 'toxicity', 'targets', 'transporters','pathways', 'dosages','snps','enzymes','carriers', 'description']
drugbank_df = pandas.DataFrame.from_dict(rows)[columns]
drugbank_df.head()

# the different tsv header for the different tsv files
columns_drug_interaction = ['DB_ID1', 'DB_ID2', 'description']
# drugbank_df_drug_interaction = pandas.DataFrame.from_dict(drug_interactions)[columns_drug_interaction]
# drugbank_df_drug_interaction.head()
columns_drug_pathway = ['drugbank_id', 'pathway_id']
columns_pathway_enzymes = ['pathway_id', 'uniprot_id']
columns_pathway = ['pathway_id', 'name', 'category']
columns_reactions = ['sequence', 'left_element_drugbank_id', 'right_element_drugbank_id', 'enzymes']
columns_snp_effects = ['drugbank_id', 'partner_id', 'description', 'pubmed_id', 'type']
columns_mutated = ['connection_id', 'uniprot_id', 'rs_id', 'protein_name', 'gene_symbol', 'allele', 'defining_change']
columns_snp_adverse_drug_reactions = ['drugbank_id', 'partner_id', 'description', 'pubmed_id', 'type']
columns_drug_target = ['drugbank_id', 'targets_id', 'targets_id_drugbank', 'position', 'actions', 'ref_article',
                       'organism', 'ref_links', 'ref_attachment', 'ref_textbooks', 'known_action']
columns_drug_enzyme = ['drugbank_id', 'targets_id', 'targets_id_drugbank', 'position', 'actions', 'ref_article',
                       'organism', 'ref_links', 'ref_attachment', 'ref_textbooks', 'known_action',
                       'inhibition_strength', 'induction_strength']
columns_target = ['drugbank_id', 'name', 'id', 'id_source', 'general_function', 'specific_function', 'gene_name',
                  'locus', 'cellular_location', 'transmembrane_regions', 'signal_regions', 'organism', 'theoretical_pi',
                  'molecular_weight', 'go_classifiers', 'chromosome_location', 'pfams', 'gene_sequence',
                  'amino_acid_sequence', 'synonyms', 'xrefs']
columns_salt = ['id', 'name', 'unii', 'inchikey', 'cas_number', 'average_mass', 'monoisotopic_mass']
columns_drug_salts = ['drug_id', 'salt_id']
columns_products = ['id', 'name', 'labeller', 'ndc_id', 'ndc_product_code', 'dpd_id', 'ema_product_code',
                    'ema_ma_number', 'started_marketing_on', 'ended_marketing_on', 'dosage_form', 'strength', 'route',
                    'fda_application_number', 'generic', 'over_the_counter', 'approved', 'country', 'source']
columns_drug_products = ['drugbank_id', 'partner_id']
columns_metabolites = ['drugbank_id', 'name']
columns_has_component = ['target_id', 'petide_id']
columns_drug_pharmacologic_class = ['drugbank_id', 'category']
columns_pharmacologic_class = ['id', 'name', 'mesh_id']
columns_reaction = ['id', 'sequence', 'start_drugbank_id']
columns_reaction_left_db = ['reaction_id', 'drug_id']
columns_reaction_left_dbmet = ['reaction_id', 'meta_id']
columns_reaction_right_db = ['reaction_id', 'drug_id']
columns_reaction_right_dbmet = ['reaction_id', 'meta_id']
columns_reaction_enzyme = ['reaction_id', 'protein_id', 'protein_id_db']

# prepare slim drugbank drug versionbased on approved drug, has inchi and is a small molecule
drugbank_slim_df = drugbank_df[
    drugbank_df.groups.map(lambda x: 'approved' in x) &
    drugbank_df.inchi.map(lambda x: x is not None) &
    drugbank_df.type.map(lambda x: x == 'small molecule')
    ]
drugbank_slim_df.head()

# write drugbank tsv
path = os.path.join('drugbank', 'drugbank_drug.tsv')
drugbank_df.to_csv(path, sep='\t', index=False, encoding='utf-8-sig')

# write slim drugbank tsv
path = os.path.join('drugbank', 'drugbank-slim2_drug.tsv')
drugbank_slim_df.to_csv(path, sep='\t', index=False, encoding='utf-8')

# generate the tsv for all the different dictionaries and tsv headers
generate_tsv_file(columns_drug_interaction, drug_interactions, 'drugbank_interaction.tsv')
generate_tsv_file(columns_drug_pathway, drug_pathways, 'drugbank_drug_pathway.tsv')
generate_tsv_file(columns_pathway_enzymes, pathway_enzymes, 'drugbank_pathway_enzymes.tsv')
generate_tsv_file(columns_pathway, pathways, 'drugbank_pathway.tsv')
generate_tsv_file(columns_snp_effects, snp_effects, 'drugbank_snp_effects.tsv')
generate_tsv_file(columns_mutated, mutated_gene_proteins, 'drugbank_mutated_gene_protein.tsv')
generate_tsv_file(columns_snp_adverse_drug_reactions, snp_adverse_drug_reactions,
                  'drugbank_snp_adverse_drug_reaction.tsv')
generate_tsv_file(columns_drug_target, drug_targets, 'drugbank_drug_target.tsv')
generate_tsv_file(columns_target, targets, 'drugbank_targets.tsv')
generate_tsv_file(columns_drug_enzyme, drug_enzymes, 'drugbank_drug_enzyme.tsv')
generate_tsv_file(columns_target, enzymes, 'drugbank_enzymes.tsv')
generate_tsv_file(columns_drug_target, drug_carriers, 'drugbank_drug_carrier.tsv')
generate_tsv_file(columns_target, carriers, 'drugbank_carrier.tsv')
generate_tsv_file(columns_drug_target, drug_transporters, 'drugbank_drug_transporter.tsv')
generate_tsv_file(columns_target, transporters, 'drugbank_transporter.tsv')
generate_tsv_file(columns_drug_salts, drug_salts, 'drugbank_drug_salt.tsv')
generate_tsv_file(columns_salt, salts, 'drugbank_salt.tsv')
generate_tsv_file(columns_drug_products, drug_products, 'drugbank_drug_products.tsv')
generate_tsv_file(columns_products, products, 'drugbank_products.tsv')
generate_tsv_file(columns_metabolites, metabolites, 'drugbank_metabolites.tsv')
generate_tsv_file(columns_has_component, has_components, 'drugbank_target_peptide_has_component.tsv')
generate_tsv_file(columns_drug_pharmacologic_class, pharmacologic_class_drug, 'drugbank_drug_pharmacologic_class.tsv')
generate_tsv_file(columns_pharmacologic_class, pharmacologic_classes, 'drugbank_pharmacologic_class.tsv')
generate_tsv_file(columns_reaction, reactions, 'drugbank_reactions.tsv')
generate_tsv_file(columns_reaction_left_db, reactions_left_db, 'drugbank_reaction_to_left_db.tsv')
generate_tsv_file(columns_reaction_left_dbmet, reactions_left_dbmet, 'drugbank__reaction_to_left_dbmet.tsv')
generate_tsv_file(columns_reaction_right_db, reactions_right_db, 'drugbank_reaction_to_right_db.tsv')
generate_tsv_file(columns_reaction_right_dbmet, reactions_right_dbmet, 'drugbank_reaction_to_right_dbmet.tsv')
generate_tsv_file(columns_reaction_enzyme, reactions_to_protein, 'drugbank_reaction_to_protein.tsv')

# prepare atc integration


cypher_file = open('cypher_atc.cypher', 'w', encoding='utf-8')

# write info into tsv file
atc_file_name = 'atc_node.tsv'
atc_file = open(atc_file_name, 'w', encoding='utf-8')
csv_atc = csv.writer(atc_file, delimiter='\t')
csv_atc.writerow(['id', 'name'])
for identifier, name in dict_atc_nodes.items():
    csv_atc.writerow([identifier, name])
atc_file.close()

# prepare act node queries
query = " Create (n:atc_drugbank{identifier:line.id, name:line.name})"
query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/drugbank/' + atc_file_name, query)
cypher_file.write(query)
cypher_file.write(pharmebinetutils.prepare_index_query('atc_drugbank', 'identifier'))

# prepare atc edge file
atc_file_name = 'atc_edge.tsv'
atc_file = open(atc_file_name, 'w', encoding='utf-8')
csv_atc = csv.writer(atc_file, delimiter='\t')
csv_atc.writerow(['id_upper', 'id_down'])
for (identifier_upper, identifier_down) in set_atc_edges:
    csv_atc.writerow([identifier_upper, identifier_down])
atc_file.close()
# prepare atc edge query
query = " Match (n:atc_drugbank{identifier:line.id_upper}), (m:atc_drugbank{identifier:line.id_down}) Create (n)<-[:is_a]-(m)"
query = pharmebinetutils.get_query_import(path_of_directory, 'import_into_Neo4j/drugbank/' + atc_file_name, query)
cypher_file.write(query)

print(datetime.datetime.now())

# write drugbank tsv
# path = os.path.join('drugbank', 'drugbank_interaction.tsv')
# drugbank_df_drug_interaction.to_csv(path, sep='\t', index=False)
