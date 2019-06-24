# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 13:25:13 2017

https://github.com/dhimmel/drugbank/blob/gh-pages/parse.ipynb
"""

import os
import csv
import gzip
import collections
import re
import io
import json
import xml.etree.ElementTree as ET
import datetime
import sys

import requests
import pandas

xml_file = os.path.join('drugbank_all_full_database_april.xml/full_database.xml')
#xml_file = os.path.join('drugbank_all_full_database_dezember.xml/test.xml')
print (datetime.datetime.utcnow())

tree = ET.parse(xml_file)
root = tree.getroot()

print (datetime.datetime.utcnow())

ns = '{http://www.drugbank.ca}'
inchikey_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChIKey']/{ns}value"
inchi_template = "{ns}calculated-properties/{ns}property[{ns}kind='InChI']/{ns}value"
molecular_formular_template="{ns}calculated-properties/{ns}property[{ns}kind='Molecular Formula']/{ns}value"
molecular_formular_experimental_template="{ns}experimental-properties/{ns}property[{ns}kind='Molecular Formula']/{ns}value"                        

       
'''
gather the different target information
'''
def gather_target_infos(target,drug_targets_info,targets_info,dict_targets_ids,db_ID):
    
    for targets in drug.iterfind(target.format(ns = ns)):
#        print('drinnen ;)')
    
        db_targets=targets.findtext("{ns}id".format(ns = ns))
        
                        
        name= targets.findtext("{ns}name".format(ns = ns))
        
        position= targets.get('position')
        organism= targets.findtext("{ns}organism".format(ns = ns))
        known_action = targets.findtext("{ns}known-action".format(ns = ns))
        
        
        actions=[]
        for action in targets.findall('{ns}actions/{ns}action'.format(ns = ns)):
            actions.append(action.text)
            
        ref_article_list=[]
        for ref in targets.findall('{ns}references/{ns}articles/{ns}article'.format(ns = ns)):
            
            pubmed_id=ref.findtext("{ns}pubmed-id".format(ns = ns))
            citation=ref.findtext("{ns}citation".format(ns = ns))
            ref_article_list.append(pubmed_id+'::'+citation)
            
        ref_textbooks_list=[]
        for ref in targets.findall('{ns}references/{ns}textbooks/{ns}textbook'.format(ns = ns)):
            
            isbn=ref.findtext("{ns}isbn".format(ns = ns))
            citation=ref.findtext("{ns}citation".format(ns = ns))
            ref_textbooks_list.append(isbn+'::'+citation)
        
        ref_link_list=[]
        for ref in targets.findall('{ns}references/{ns}links/{ns}link'.format(ns = ns)):
            
            title=ref.findtext("{ns}title".format(ns = ns))
            url=ref.findtext("{ns}url".format(ns = ns))
            ref_link_list.append(title+'::'+url)
         
        polypetide_found=False
        peptide_list=[]
        dict_drug_targt={}
        for polypeptide in targets.findall("{ns}polypeptide".format(ns = ns)):
            polypetide_found=True
            drug_targets = collections.OrderedDict()
            targets_dict = collections.OrderedDict()
            
            drug_targets['drugbank_id']=db_ID
            uniprot_id=polypeptide.get('id')
            
            targets_dict['drugbank_id']= db_targets
            drug_targets['targets_id_drugbank'] = db_targets
            drug_targets['organism'] = organism
                        
            targets_dict['name']= name
            
            drug_targets['position']= position
#            targets_dict['organism']= organism
            
            drug_targets['actions']=actions
                     
            drug_targets['ref_article']=ref_article_list
                       
            drug_targets['ref_links']=ref_link_list
                       
            drug_targets['ref_textbooks']=ref_textbooks_list
                       
            drug_targets['known_action'] = known_action
                        
            
#        if not targets.find("{ns}polypeptide".format(ns = ns)) is None:
            uniprot_id=polypeptide.get('id')
            drug_targets['targets_id'] = polypeptide.get('id')
            targets_dict['id']=polypeptide.get('id')
            peptide_list.append(polypeptide.get('id'))
            targets_dict['id_source']=polypeptide.get('source')
            targets_dict['name']=polypeptide.findtext("{ns}name".format(ns = ns))
            targets_dict['general_function']= polypeptide.findtext("{ns}general-function".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['specific_function']= polypeptide.findtext("{ns}specific-function".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['gene_name']= polypeptide.findtext("{ns}gene-name".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['locus']= polypeptide.findtext("{ns}locus".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['cellular_location']= polypeptide.findtext("{ns}cellular-location".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['transmembrane_regions']= polypeptide.findtext("{ns}transmembrane-regions".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['signal_regions']= polypeptide.findtext("{ns}signal-regions".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['theoretical_pi']= polypeptide.findtext("{ns}theoretical-pi".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['molecular_weight']= polypeptide.findtext("{ns}molecular-weight".format(ns = ns)).replace('\n','').replace('\r','')
            targets_dict['chromosome_location']= polypeptide.findtext("{ns}chromosome-location".format(ns = ns)).replace('\n','').replace('\r','')
            
            xref_list=[]
            for xref in polypeptide.findall('{ns}external-identifiers/{ns}external-identifier'.format(ns = ns)):
                
                resource=xref.findtext("{ns}resource".format(ns = ns))
                identifier=xref.findtext("{ns}identifier".format(ns = ns))
                xref_list.append(resource+'::'+identifier)
            targets_dict['xrefs']=xref_list
            targets_dict['synonyms']= [salt.text for salt in
            polypeptide.findall("{ns}synonyms/{ns}synonym".format(ns = ns))]
            targets_dict['amino-acid-sequence']= polypeptide.findtext("{ns}amino-acid-sequence".format(ns = ns)).replace('\n','').replace('\r','')
            all_seq= polypeptide.findtext("{ns}amino-acid-sequence".format(ns = ns)).split('\n',1) if polypeptide.findtext("{ns}amino-acid-sequence".format(ns = ns))!=None else []
            if len(all_seq)==2:
                all_seq[0]=all_seq[0].replace(' ','_')
                all_seq[1]=all_seq[1].replace('\n','')
            targets_dict['amino_acid_sequence']=' '.join(all_seq)
                
            all_seq= polypeptide.findtext("{ns}gene-sequence".format(ns = ns)).split('\n',1) if polypeptide.findtext("{ns}amino-acid-sequence".format(ns = ns))!=None else []
            if len(all_seq)==2:
                all_seq[0]=all_seq[0].replace(' ','_')
                all_seq[1]=all_seq[1].replace('\n','')
            targets_dict['gene_sequence']=' '.join(all_seq)
            
            pfam_list=[]
            for pfam in polypeptide.findall('{ns}pfams/{ns}pfam'.format(ns = ns)):
                
                name=pfam.findtext("{ns}name".format(ns = ns))
                identifier=pfam.findtext("{ns}identifier".format(ns = ns))
                pfam_list.append(identifier+'::'+name)
            targets_dict['pfams']=pfam_list
            go_classifier_list=[]
            for goClass in polypeptide.findall('{ns}go-classifiers/{ns}go-classifier'.format(ns = ns)):
                
                category=goClass.findtext("{ns}category".format(ns = ns))
                description=goClass.findtext("{ns}description".format(ns = ns))
                go_classifier_list.append(category+'::'+description)
            targets_dict['go_classifiers']=go_classifier_list
                        
#            drug_targets_info.append(drug_targets)
            if not uniprot_id in dict_targets_ids:
                targets_info.append(targets_dict)
                dict_targets_ids[uniprot_id]=1
                                
            if not  (db_ID,uniprot_id) in dict_drug_targt:
                dict_drug_targt[(db_ID,uniprot_id)]=drug_targets
            else:
                sys.exit()
            
        if len(peptide_list)>1:
            drug_targets = collections.OrderedDict()
            targets_dict = collections.OrderedDict()
            drug_targets['drugbank_id']=db_ID
            targets_dict['drugbank_id']= db_targets
#            print(db_ID,db_targets)
            drug_targets['targets_id_drugbank'] = db_targets
            drug_targets['organism'] = organism
            targets_dict['name']=  targets.findtext("{ns}name".format(ns = ns))
            
            drug_targets['position']= position
#            targets_dict['organism']= organism
            
            
            drug_targets['actions']=actions
                     
            drug_targets['ref_article']=ref_article_list
                       
            drug_targets['ref_links']=ref_link_list
                       
            drug_targets['ref_textbooks']=ref_textbooks_list
                       
            drug_targets['known_action'] = known_action
            drug_targets_info.append(drug_targets)
            if not db_targets in dict_targets_ids:
                targets_info.append(targets_dict)
                dict_targets_ids[db_targets]=1
            for petide in peptide_list:
                
                if not (db_targets,petide) in dict_has_component:
                    target_peptite = collections.OrderedDict()
                    target_peptite['target_id']=db_targets
                    target_peptite['petide_id']=petide
                    dict_has_component[(db_targets,petide)]=1
                    has_components.append(target_peptite)
                    
            
        elif not polypetide_found :
            drug_targets = collections.OrderedDict()
            targets_dict = collections.OrderedDict()
            drug_targets['drugbank_id']=db_ID
            targets_dict['drugbank_id']= db_targets
            drug_targets['targets_id_drugbank'] = db_targets
            drug_targets['organism'] = organism
            targets_dict['name']=  targets.findtext("{ns}name".format(ns = ns))
            
            drug_targets['position']= position
#            targets_dict['organism']= organism
            
            drug_targets['actions']=actions
                     
            drug_targets['ref_article']=ref_article_list
                       
            drug_targets['ref_links']=ref_link_list
                       
            drug_targets['ref_textbooks']=ref_textbooks_list
                       
            drug_targets['known_action'] = known_action
            drug_targets_info.append(drug_targets)
            if not db_targets in dict_targets_ids:
                targets_info.append(targets_dict)
                dict_targets_ids[db_targets]=1
        else:
            for key, list_property in dict_drug_targt.items():
                
                drug_targets_info.append(list_property)
counter=0
rows = list()
drug_interactions=list()
drug_pathways=list()
pathway_enzymes=list()
pathways=list()
reactions=list()
snp_effects=list()
mutated_gene_enzymes=list()
snp_adverse_drug_reactions=list()
drug_targets=list()
targets=list()
drug_enzymes=list()
enzymes=list()
drug_carriers=list()
carriers=list()
drug_transporters=list()
transporters=list()
drug_salts=list()
salts=list()
drug_products=list()
products=list()
metabolites=list()
has_components=list()
pharmacologic_classes=list()
pharmacologic_class_drug=list()

#dictionaries for the different entities
dict_pharmacologic_class={}
dict_carrier_ids={}
dict_enzyme_ids={}
dict_target_ids={}
dict_transporter_ids={}
dict_products_ids={}
dict_metabolites_ids={}
dict_pathway_ids={}
dict_mutated_gene_enzyme={}
dict_has_component={}
dict_pathway_enzyme={}
for i, drug in enumerate(root):
    counter+=1
    row = collections.OrderedDict()
    
    assert drug.tag == ns + 'drug'
    
    row['type'] = drug.get('type')
    row['drugbank_id'] = drug.findtext(ns + "drugbank-id[@primary='true']")
    db_ID=drug.findtext(ns + "drugbank-id[@primary='true']")
    row['cas_number']= drug.findtext(ns +"cas-number")
#    print(row['drugbank_id'])
    
    alternative_ids=[group.text for group in
        drug.findall("{ns}drugbank-id".format(ns = ns))]
    alternative_ids.remove(db_ID)
    row['alternative_drugbank_ids'] = alternative_ids
    
    row['name'] = drug.findtext(ns + "name")

    
    row['description'] = drug.findtext(ns + "description").replace('\n','').replace('\r','')
#    print(row['description'])
    row['groups'] = [group.text for group in
        drug.findall("{ns}groups/{ns}group".format(ns = ns))]
    row['atc_codes'] = [code.get('code') for code in
        drug.findall("{ns}atc-codes/{ns}atc-code".format(ns = ns))]
    

#    row['categories'] = [x.findtext(ns + 'category') for x in
#        drug.findall("{ns}categories/{ns}category".format(ns = ns))]
    row['inchi'] = drug.findtext(inchi_template.format(ns = ns))
    row['inchikey'] = drug.findtext(inchikey_template.format(ns = ns))
    row['synonyms']= [salt.text for salt in
        drug.findall("{ns}synonyms/{ns}synonym".format(ns = ns))]
    row['unii']=drug.findtext(ns + "unii")
    row['state']=drug.findtext(ns + "state")
    row['general_references_articles_pubmed_citation']=[]
    for article in drug.iterfind('{ns}general-references/{ns}articles/{ns}article'.format(ns = ns)):
        pubmed_id = article.findtext("{ns}pubmed-id".format(ns = ns))
        citation=article.findtext("{ns}citation".format(ns = ns))
        combined=pubmed_id+'::'+citation
        row['general_references_articles_pubmed_citation'].append(combined)
        
    row['general_references_textbooks_isbn_citation']=[]
    for article in drug.iterfind('{ns}general-references/{ns}textbooks/{ns}textbook'.format(ns = ns)):
        isbn = article.findtext("{ns}isbn".format(ns = ns))
        citation=article.findtext("{ns}citation".format(ns = ns))
        combined=isbn+'::'+citation
        row['general_references_textbooks_isbn_citation'].append(combined)
        
    row['general_references_links_title_url']=[]
    for article in drug.iterfind('{ns}general-references/{ns}links/{ns}link'.format(ns = ns)):
        title = article.findtext("{ns}title".format(ns = ns))
        url=article.findtext("{ns}url".format(ns = ns))
        combined=title+'::'+url
        row['general_references_links_title_url'].append(combined)
        
    row['synthesis_reference']=drug.findtext(ns + "synthesis-reference").replace('\n','').replace('\r','')
    row['indication']=drug.findtext(ns + "indication").replace('\n','').replace('\r','')
    row['pharmacodynamics']=drug.findtext(ns + "pharmacodynamics").replace('\n','').replace('\r','')
    row['mechanism_of_action']=drug.findtext(ns + "mechanism-of-action").replace('\n','').replace('\r','')
    row['toxicity']= drug.findtext(ns + "toxicity").replace('\r\n',' ')
    row['metabolism']=drug.findtext(ns + "metabolism").replace('\n','').replace('\r','')
    row['absorption']=drug.findtext(ns + "absorption").replace('\n','').replace('\r','')
    row['half_life']=drug.findtext(ns + "half-life").replace('\n','').replace('\r','')
    row['protein_binding']=drug.findtext(ns + "protein-binding").replace('\n','').replace('\r','')
    row['route_of_elimination']=drug.findtext(ns + "route-of-elimination").replace('\n','').replace('\r','')
    row['volume_of_distribution']=drug.findtext(ns + "volume-of-distribution").replace('\n','').replace('\r','')
    row['clearance']=drug.findtext(ns + "clearance").replace('\n','').replace('\r','')
    
    row['classification_description']=drug.findtext(ns + "classification/{ns}description".format(ns = ns))
    row['classification_direct_parent']=drug.findtext(ns + "classification/{ns}direct-parent".format(ns = ns))
    row['classification_kingdom']=drug.findtext(ns + "classification/{ns}kingdom".format(ns = ns))
    row['classification_superclass']=drug.findtext(ns + "classification/{ns}superclass".format(ns = ns))
    row['classification_class']=drug.findtext(ns + "classification/{ns}class".format(ns = ns))
    row['classification_subclass']=drug.findtext(ns + "classification/{ns}subclass".format(ns = ns))
    row['classification_substituent']=[group.text for group in
        drug.findall("{ns}classification/{ns}substituent".format(ns = ns))]
#    drug.findtext(ns + "classification/{ns}substituent".format(ns = ns))
    row['classification_alternative_parent']=[group.text for group in
        drug.findall("{ns}classification/{ns}alternative-parent".format(ns = ns))]
#    drug.findtext(ns + "classification/{ns}alternative-parent".format(ns = ns))
    
    
    for salt in drug.iterfind('{ns}salts/{ns}salt'.format(ns = ns)):
        salt_dict = collections.OrderedDict()
        drug_salt = collections.OrderedDict()
        drug_id = salt.findtext("{ns}drugbank-id".format(ns = ns))
        salt_dict['id']=drug_id
        drug_salt['salt_id']=drug_id
        drug_salt['drug_id']=db_ID
        salt_dict['name']=salt.findtext("{ns}name".format(ns = ns))
        salt_dict['unii']=salt.findtext("{ns}unii".format(ns = ns))
        salt_dict['inchikey']=salt.findtext("{ns}inchikey".format(ns = ns))
        salt_dict['cas_number']=salt.findtext("{ns}cas-number".format(ns = ns))
        salt_dict['average_mass']=salt.findtext("{ns}average-mass".format(ns = ns))
        salt_dict['monoisotopic_mass']=salt.findtext("{ns}monoisotopic-mass".format(ns = ns))
        
        drug_salts.append(drug_salt)
        salts.append(salt_dict)
        
        
    for product in drug.iterfind('{ns}products/{ns}product'.format(ns = ns)):
        products_dict = collections.OrderedDict()
        drug_products_dict = collections.OrderedDict()
        ndc_product_code=product.findtext("{ns}ndc-product-code".format(ns = ns))
        dpd_id=product.findtext("{ns}dpd-id".format(ns = ns))
        ema_ma_number=product.findtext("{ns}ema-ma-number".format(ns = ns))
#        drug_products_dict['ndc_product_code']=ndc_product_code
        drug_products_dict['drugbank_id']=db_ID
#        drug_products_dict['dpd_id']=dpd_id
#        drug_products_dict['ema_ma_number'] = ema_ma_number
        if ndc_product_code =='' and dpd_id=='' and ema_ma_number=='':
            print('ohje')
            print(db_ID)
            
        
        if dpd_id!='':
            unique_id=dpd_id
        elif ndc_product_code!='':
            unique_id=ndc_product_code
        else:
            unique_id=ema_ma_number
        drug_products_dict['partner_id']=unique_id
        drug_products.append(drug_products_dict)
        if unique_id in dict_products_ids:
            continue
        
        dict_products_ids[unique_id]=''
        
        products_dict['id']=unique_id
        products_dict['name'] = product.findtext("{ns}name".format(ns = ns))
        products_dict['labeller']=product.findtext("{ns}labeller".format(ns = ns))
        products_dict['ndc_id']=product.findtext("{ns}ndc-id".format(ns = ns))
        products_dict['ndc_product_code']=ndc_product_code
        products_dict['dpd_id'] = dpd_id
        products_dict['ema_product_code'] = product.findtext("{ns}ema-product-code".format(ns = ns))
        products_dict['ema_ma_number'] = ema_ma_number
        products_dict['started_marketing_on'] = product.findtext("{ns}started-marketing-on".format(ns = ns))
        products_dict['ended_marketing_on'] = product.findtext("{ns}ended-marketing-on".format(ns = ns))
        products_dict['dosage_form'] = product.findtext("{ns}dosage-form".format(ns = ns))
        products_dict['strength'] = product.findtext("{ns}strength".format(ns = ns))
        products_dict['route'] = product.findtext("{ns}route".format(ns = ns))
        products_dict['fda_application_number'] = product.findtext("{ns}fda-application-number".format(ns = ns))
        products_dict['generic'] = product.findtext("{ns}generic".format(ns = ns))
        products_dict['over_the_counter'] = product.findtext("{ns}over-the-counter".format(ns = ns))
        products_dict['approved'] = product.findtext("{ns}approved".format(ns = ns))
        products_dict['country'] = product.findtext("{ns}country".format(ns = ns))
        products_dict['source'] = product.findtext("{ns}source".format(ns = ns))
#        print(products_dict)
        
        products.append(products_dict)
        
        
        
    
    row['international_brands_name_company']=[]
    for international_brand in drug.iterfind('{ns}international-brands/{ns}international-brand'.format(ns = ns)):
        name = international_brand.findtext("{ns}name".format(ns = ns))
        company=international_brand.findtext("{ns}company".format(ns = ns))
        combined=name+':'+company
        row['international_brands_name_company'].append(combined)
        
    row['mixtures_name_ingredients']=[]
    dict_mixtures_ingredients_combination_names={}
    for part in drug.iterfind('{ns}mixtures/{ns}mixture'.format(ns = ns)):
        name = part.findtext("{ns}name".format(ns = ns))
        ingredients=part.findtext("{ns}ingredients".format(ns = ns))
        if ingredients in dict_mixtures_ingredients_combination_names:
            dict_mixtures_ingredients_combination_names[ingredients].add(name)
        else:
            dict_mixtures_ingredients_combination_names[ingredients]=set([name])
    
    for ingredients, names in dict_mixtures_ingredients_combination_names.items():
        name=';;'.join(names)
        combined=name+':'+ingredients 
        row['mixtures_name_ingredients'].append(combined)
        
    row['packagers_name_url']=[]
    for part in drug.iterfind('{ns}packagers/{ns}packager'.format(ns = ns)):
        name = part.findtext("{ns}name".format(ns = ns))
        url=part.findtext("{ns}url".format(ns = ns))
        combined=name+':'+url
        row['packagers_name_url'].append(combined)
        
    row['manufacturers']= [salt.text for salt in
        drug.findall("{ns}manufacturers/{ns}manufacturer".format(ns = ns))]
    
    row['prices_description_cost_unit']=[]
    for part in drug.iterfind('{ns}prices/{ns}price'.format(ns = ns)):
        description = part.findtext("{ns}description".format(ns = ns))
        cost=part.find("{ns}cost".format(ns = ns)).get('currency')+':'+part.findtext("{ns}cost".format(ns = ns))
        unit = part.findtext("{ns}unit".format(ns = ns))
        combined=description+':'+cost+':'+unit
        row['prices_description_cost_unit'].append(combined)
        
    for part in drug.iterfind('{ns}categories/{ns}category'.format(ns = ns)):
        category = part.findtext("{ns}category".format(ns = ns))
        mesh_id=part.findtext("{ns}mesh-id".format(ns = ns))
        
        drug_pharmacological_class_dict = collections.OrderedDict()
        drug_pharmacological_class_dict['drugbank_id']=db_ID
        drug_pharmacological_class_dict['category']=category    
        pharmacologic_class_drug.append(drug_pharmacological_class_dict)
        if not category in dict_pharmacologic_class:
            pharmacologic_class_dict = collections.OrderedDict()
            pharmacologic_class_dict['id']=mesh_id
            pharmacologic_class_dict['name']=category
            pharmacologic_classes.append(pharmacologic_class_dict)
            dict_pharmacologic_class[category]=mesh_id
        
        
    row['affected_organisms']= [salt.text for salt in
        drug.findall("{ns}affected-organisms/{ns}affected-organism".format(ns = ns))]
    
    row['dosages_form_route_strength']=[]
    for part in drug.iterfind('{ns}dosages/{ns}dosage'.format(ns = ns)):
        form = part.findtext("{ns}form".format(ns = ns))
        route=part.findtext("{ns}route".format(ns = ns))
        strength=part.findtext("{ns}strength".format(ns = ns))
        combined=form+':'+route+':'+strength
        row['dosages_form_route_strength'].append(combined)
        
    row['atc_code_levels'] = [code.get('code') for code in
        drug.findall("{ns}atc-codes/{ns}atc-code/{ns}level".format(ns = ns))]
    
    row['ahfs_codes']= [salt.text for salt in
        drug.findall("{ns}ahfs-codes/{ns}ahfs-code".format(ns = ns))]
    
    row['pdb_entries']= [salt.text for salt in
        drug.findall("{ns}pdb-entries/{ns}pdb-entry".format(ns = ns))]
    row['fda_label']=drug.findtext(ns + "fda-label").replace('\n','').replace('\r','') if not drug.findtext(ns + "fda-label") is None else '' 
    row['msds']=drug.findtext(ns + "msds").replace('\n','').replace('\r','') if not drug.findtext(ns + "msds") is None else '' 
    
    row['patents_number_country_approved_expires_pediatric_extension']=[]
    for part in drug.iterfind('{ns}patents/{ns}patent'.format(ns = ns)):
        number = part.findtext("{ns}number".format(ns = ns))
        country=part.findtext("{ns}country".format(ns = ns))
        approved=part.findtext("{ns}approved".format(ns = ns))
        expires=part.findtext("{ns}expires".format(ns = ns))
        pediatric_extension=part.findtext("{ns}pediatric-extension".format(ns = ns))
        combined=number+':'+country+':'+approved+':'+expires+':'+pediatric_extension
        row['patents_number_country_approved_expires_pediatric_extension'].append(combined)
        
    row['food_interaction']= [salt.text for salt in
        drug.findall("{ns}food-interactions/{ns}food-interaction".format(ns = ns))]
    
    #muss noch geprüft werde das nicht jede verbindung doppelt ist
    for part in drug.iterfind('{ns}drug-interactions/{ns}drug-interaction'.format(ns = ns)):
        drug_interaction=collections.OrderedDict()
        drug_interaction['DB_ID1']=db_ID
        drug_interaction['DB_ID2']=part.findtext("{ns}drugbank-id".format(ns = ns))
        drug_interaction['description']=part.findtext("{ns}description".format(ns = ns))
        drug_interactions.append(drug_interaction)
        
    all_seq=[seq.text.split('\n',1) for seq in drug.findall("{ns}sequences/{ns}sequence".format(ns = ns))] if drug.findtext("{ns}sequences/{ns}sequence".format(ns = ns))!=None else []
    
    counter=0
    for all_spliter in all_seq:
        all_spliter[0]=all_spliter[0].replace(' ','_').replace('|','/')
        all_spliter[1]=all_spliter[1].replace('\n','')
        all_seq[counter]=' '.join(all_spliter)
        counter+=1
    row['sequences']=all_seq  
        
#    row['sequences']= [seq.text.replace('\n',' ',1).replace('\r',' ',1).replace('\t','').replace('\n','').replace('\r','') for seq in drug.findall("{ns}sequences/{ns}sequence".format(ns = ns))] if drug.findtext("{ns}sequences/{ns}sequence".format(ns = ns))!=None else []
    row['calculated_properties_kind_value_source']=[]
    for part in drug.iterfind('{ns}calculated-properties/{ns}property'.format(ns = ns)):
        kind = part.findtext("{ns}kind".format(ns = ns))
        value=part.findtext("{ns}value".format(ns = ns))
        source=part.findtext("{ns}source".format(ns = ns))
        combined=kind+'::'+value+'::'+source
        row['calculated_properties_kind_value_source'].append(combined)   
        
    row['experimental_properties_kind_value_source']=[]
    for part in drug.iterfind('{ns}experimental-properties/{ns}property'.format(ns = ns)):
        kind = part.findtext("{ns}kind".format(ns = ns))
        value=part.findtext("{ns}value".format(ns = ns))
        source=part.findtext("{ns}source".format(ns = ns))
        combined=kind+'::'+value+'::'+source
        row['experimental_properties_kind_value_source'].append(combined)      
        
    
    extern_ids_source=[salt.text for salt in
        drug.findall("{ns}external-identifiers/{ns}external-identifier/{ns}resource".format(ns = ns))]
    extern_ids=[salt.text for salt in
        drug.findall("{ns}external-identifiers/{ns}external-identifier/{ns}identifier".format(ns = ns))]   
    row['external_identifiers']=[i+':'+j for i,j in zip(extern_ids_source,extern_ids)]
    
    row['external_links_resource_url']=[]
    for part in drug.iterfind('{ns}external-links/{ns}external-link'.format(ns = ns)):
        resource = part.findtext("{ns}resource".format(ns = ns))
        url=part.findtext("{ns}url".format(ns = ns))
        combined=resource+'::'+url
        row['external_links_resource_url'].append(combined) 
    
    for part in drug.iterfind('{ns}pathways/{ns}pathway'.format(ns = ns)):
        pathway = collections.OrderedDict()
        drug_pathway = collections.OrderedDict()
        
        smpdb_id = part.findtext("{ns}smpdb-id".format(ns = ns))
        if smpdb_id not in dict_pathway_ids:
            
            name=part.findtext("{ns}name".format(ns = ns))
            category=part.findtext("{ns}category".format(ns = ns))
            pathway['pathway_id']=smpdb_id
            pathway['name']=name   
            pathway['category']=category
            
            pathways.append(pathway)
            dict_pathway_ids[smpdb_id]=''
               
        drug_pathway['drugbank_id']=db_ID
        drug_pathway['pathway_id']=smpdb_id
               
        drug_pathways.append(drug_pathway)
        
        
        for enzym in part.findall('{ns}enzymes/{ns}uniprot-id'.format(ns = ns)):
            
            pathway_enzym = collections.OrderedDict()
            uniprot_id=enzym.text
#            if smpdb_id=='SMP63607':
#                print(uniprot_id )
#                print(db_ID)
#            uniprot_id=uniprot_id.replace(' ','')
            if not (smpdb_id,uniprot_id) in dict_pathway_enzyme:
                pathway_enzym['pathway_id']=smpdb_id
                pathway_enzym['uniprot_id']=uniprot_id
                pathway_enzymes.append(pathway_enzym)
                dict_pathway_enzyme[(smpdb_id,uniprot_id)]=1
                        
    for part in drug.iterfind('{ns}reactions/{ns}reaction'.format(ns = ns)):
        reaction = collections.OrderedDict()
        
        reaction['sequence'] = part.findtext("{ns}sequence".format(ns = ns))
        left=part.findtext("{ns}left-element/{ns}drugbank-id".format(ns = ns))
        right=part.findtext("{ns}right-element/{ns}drugbank-id".format(ns = ns))
        reaction['left_element_drugbank_id']=left
        reaction['right_element_drugbank_id']=right
        if left[0:5]=='DBMET':
            if not left in dict_metabolites_ids:
                metabolite = collections.OrderedDict()
                metabolite['drugbank_id']=left
                metabolite['name']=part.findtext("{ns}right-element/{ns}name".format(ns = ns))
                dict_metabolites_ids[left]=''
                metabolites.append(metabolite)
                
        if right[0:5]=='DBMET':
            if not right in dict_metabolites_ids:
                metabolite = collections.OrderedDict()
                metabolite['drugbank_id']=right
                metabolite['name']=part.findtext("{ns}right-element/{ns}name".format(ns = ns))
                dict_metabolites_ids[right]=''
                metabolites.append(metabolite)
        
        enzymes_list=[]
        for enzyme in part.findall('{ns}enzymes/{ns}enzyme'.format(ns = ns)):
            
            enzyme_drugbank_id=enzyme.findtext("{ns}drugbank-id".format(ns = ns))
            enzyme_uniprot_id=enzyme.findtext("{ns}uniprot-id".format(ns = ns))
            enzymes_list.append(enzyme_drugbank_id+':'+enzyme_uniprot_id)
        reaction['enzymes']=enzymes_list
        reactions.append(reaction)
        
    for part in drug.iterfind('{ns}snp-effects/{ns}effect'.format(ns = ns)):
        snp_effect = collections.OrderedDict()
        mutated_gene_enzyme = collections.OrderedDict()
        
        uniprot_id=part.findtext("{ns}uniprot-id".format(ns = ns))
        rs_id=part.findtext("{ns}rs-id".format(ns = ns))
        gene_symbol=part.findtext("{ns}gene-symbol".format(ns = ns))
        
        snp_effect['drugbank_id'] = db_ID
        if rs_id!='':
            snp_effect['partner_id']=rs_id
            unique_id=rs_id
        else:
            snp_effect['partner_id']=gene_symbol
            unique_id=gene_symbol
        snp_effect['description']=part.findtext("{ns}description".format(ns = ns))
        snp_effect['pubmed_id']=part.findtext("{ns}pubmed-id".format(ns = ns))
        snp_effect['type']='Effect Directly Studied'
        
        if unique_id not in dict_mutated_gene_enzyme: 
            mutated_gene_enzyme['protein_name']=part.findtext("{ns}protein-name".format(ns = ns))
            mutated_gene_enzyme['gene_symbol']=part.findtext("{ns}gene-symbol".format(ns = ns))
            mutated_gene_enzyme['uniprot_id']=part.findtext("{ns}uniprot-id".format(ns = ns))
            mutated_gene_enzyme['rs_id']=part.findtext("{ns}rs-id".format(ns = ns))
            mutated_gene_enzyme['allele']=part.findtext("{ns}allele".format(ns = ns))
            mutated_gene_enzyme['defining_change']=part.findtext("{ns}defining-change".format(ns = ns))
            mutated_gene_enzyme['connection_id']=unique_id
                               
                               
            dict_mutated_gene_enzyme[unique_id]=''
        
            mutated_gene_enzymes.append(mutated_gene_enzyme)
        snp_effects.append(snp_effect)
    
    for part in drug.iterfind('{ns}snp-adverse-drug-reactions/{ns}reaction'.format(ns = ns)):
        snp_adverse_drug_reaction = collections.OrderedDict()
        mutated_gene_enzyme = collections.OrderedDict()
        
        uniprot_id=part.findtext("{ns}uniprot-id".format(ns = ns))
        rs_id=part.findtext("{ns}rs-id".format(ns = ns))
        gene_symbol=part.findtext("{ns}gene-symbol".format(ns = ns))
        
        snp_adverse_drug_reaction['drugbank_id'] = db_ID
        if rs_id!='':
            snp_adverse_drug_reaction['partner_id']=rs_id
            unique_id=rs_id
        else:
            snp_adverse_drug_reaction['partner_id']=gene_symbol
            unique_id=gene_symbol
            
        snp_adverse_drug_reaction['description']=part.findtext("{ns}description".format(ns = ns))
        snp_adverse_drug_reaction['pubmed_id']=part.findtext("{ns}pubmed-id".format(ns = ns))
        snp_adverse_drug_reaction['type']='ADR Directly Studied'
        if unique_id not in dict_mutated_gene_enzyme: 
            mutated_gene_enzyme['protein_name']=part.findtext("{ns}protein-name".format(ns = ns))
            mutated_gene_enzyme['gene_symbol']=part.findtext("{ns}gene-symbol".format(ns = ns))
            mutated_gene_enzyme['uniprot_id']=part.findtext("{ns}uniprot-id".format(ns = ns))
            mutated_gene_enzyme['rs_id']=part.findtext("{ns}rs-id".format(ns = ns))
            mutated_gene_enzyme['allele']=part.findtext("{ns}allele".format(ns = ns))
            mutated_gene_enzyme['defining_changes']=part.findtext("{ns}adverse-reaction".format(ns = ns))
            mutated_gene_enzyme['connection_id']=unique_id
                               
            dict_mutated_gene_enzyme[unique_id]=''
            
            mutated_gene_enzymes.append(mutated_gene_enzyme)
        snp_adverse_drug_reactions.append(snp_adverse_drug_reaction)
        

    # target 
    gather_target_infos('{ns}targets/{ns}target',drug_targets,targets,dict_target_ids, db_ID)
    
    # enzymes
    gather_target_infos('{ns}enzymes/{ns}enzyme',drug_enzymes,enzymes,dict_enzyme_ids, db_ID)
    
    # carries
    b=False
#    if db_ID=='DB00137':
#        print('jup')
#        b=True
    gather_target_infos('{ns}carriers/{ns}carrier',drug_carriers,carriers,dict_carrier_ids, db_ID)

   # transporter
    gather_target_infos('{ns}transporters/{ns}transporter',drug_transporters,transporters,dict_transporter_ids, db_ID)

    
    # Add drug aliases
    aliases = {
        elem.text for elem in 
        drug.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
        drug.findall("{ns}synonyms/{ns}synonym[@language='English']".format(ns = ns)) +
        drug.findall("{ns}international-brands/{ns}international-brand".format(ns = ns)) +
        drug.findall("{ns}products/{ns}product/{ns}name".format(ns = ns))

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
 
print('number of entries in drugbank:'+str(counter))
print (datetime.datetime.utcnow())   
#sys.exit()
alias_dict = {row['drugbank_id']: row['aliases'] for row in rows}
with open('./data/aliases.json', 'w') as fp:
    json.dump(alias_dict, fp, indent=2, sort_keys=True)
    
def collapse_list_values(row):
    for key, value in row.items():
        if isinstance(value, list):
#            print(key)
#            print(value)
            i=0
            if key=='inchikeys'or key=='uniis' or key=='extra_names' or key=='target' or key=='transporter' :
                list_delete=[]
                for val in value:
                    if val ==None:
                        list_delete.insert(0,i)
                    i+=1
                for j in list_delete:
                    del value[j]
                    
            if len(value)>0:
#                if key=='inchikeys':
#                    print(value)
                string_value = '||'.join(value)
                row[key]=string_value.replace('\t','').replace('\n','').replace('\r','')
#                if key=='food_interaction':
#                    print('blub')
            else :
                row[key]=''
        
    return row

# preperate the list 
def preperation(list_information):
    list_information=list(map(collapse_list_values,list_information))
    return list_information

print (datetime.datetime.utcnow())
print('preperation of information lists')
rows= preperation(rows)
drug_interactions=preperation(drug_interactions)
drug_pathways=preperation(drug_pathways)
pathway_enzymes=preperation(pathway_enzymes)
pathways=preperation(pathways)
reactions=preperation(reactions)
snp_effects=preperation(snp_effects)
mutated_gene_enzymes=preperation(mutated_gene_enzymes)
snp_adverse_drug_reactions=preperation(snp_adverse_drug_reactions)
drug_targets=preperation(drug_targets)
targets=preperation(targets)
drug_enzymes=preperation(drug_enzymes)
enzymes=preperation(enzymes)
drug_carriers=preperation(drug_carriers)
carriers=preperation(carriers)
drug_transporters=preperation(drug_transporters)
transporters=preperation(transporters)
drug_salts=preperation(drug_salts)
salts=preperation(salts)
products=preperation(products)
drug_products=preperation(drug_products)
metabolites=preperation(metabolites)
has_components=preperation(has_components)
pharmacologic_classes=preperation(pharmacologic_classes)
pharmacologic_class_drug=preperation(pharmacologic_class_drug)

# preperation and generation of an tsv
def generate_tsv_file(columns,list_information,file_name):
    
#    print(list_information)
#    print(columns)
    drugbank_information = pandas.DataFrame.from_dict(list_information)[columns]
    drugbank_information.head()
    
    path = os.path.join('data', file_name)
    drugbank_information.to_csv(path, sep='\t', index=False, encoding='utf-8')

print (datetime.datetime.utcnow())
print('malsehen')
columns = ['drugbank_id', 'alternative_drugbank_ids' ,'name','cas_number','unii',
           'state','groups','general_references_links_title_url' ,
           'general_references_textbooks_isbn_citation', 'general_references_articles_pubmed_citation',
           'synthesis_reference','indication','pharmacodynamics','mechanism_of_action','toxicity',
           'metabolism','absorption','half_life','protein_binding','route_of_elimination',
           'volume_of_distribution','clearance','classification_subclass','classification_class',
           'classification_superclass','classification_kingdom','classification_direct_parent',
           'classification_description','synonyms','international_brands_name_company',
           'mixtures_name_ingredients','packagers_name_url','manufacturers','prices_description_cost_unit',
           'affected_organisms','dosages_form_route_strength','atc_code_levels','ahfs_codes',
           'pdb_entries','fda_label','msds','patents_number_country_approved_expires_pediatric_extension',
           'food_interaction','sequences','calculated_properties_kind_value_source',
           'experimental_properties_kind_value_source','external_identifiers',
           'external_links_resource_url','type',
           'classification_alternative_parent','classification_substituent','inchi',
           'inchikey','description']
#['drugbank_id', 'drugbank_ids' ,'name', 'type', 'cas_number' , 'groups', 'atc_codes', 'categories', 'inchikey', 'inchi','inchikeys', 'synonyms', 'unii','uniis', 'external_identifiers','extra_names', 'brands', 'molecular_formula','molecular_formular_experimental','sequences','drug_interaction', 'drug_interaction_description','food_interaction', 'toxicity', 'targets', 'transporters','pathways', 'dosages','snps','enzymes','carriers', 'description']
drugbank_df = pandas.DataFrame.from_dict(rows)[columns]
drugbank_df.head()

columns_drug_interaction=['DB_ID1','DB_ID2','description']
#drugbank_df_drug_interaction = pandas.DataFrame.from_dict(drug_interactions)[columns_drug_interaction]
#drugbank_df_drug_interaction.head()
columns_drug_pathway=['drugbank_id','pathway_id']
columns_pathway_enzymes=['pathway_id','uniprot_id']
columns_pathway=['pathway_id','name','category']
columns_reactions=['sequence','left_element_drugbank_id','right_element_drugbank_id','enzymes']
columns_snp_effects=['drugbank_id','partner_id','description','pubmed_id','type']
columns_mutated=['connection_id','uniprot_id','rs_id','protein_name','gene_symbol','allele','defining_change']
columns_snp_adverse_drug_reactions=['drugbank_id','partner_id','description','pubmed_id','type']              
columns_drug_target=['drugbank_id','targets_id','targets_id_drugbank','position','organism','actions','ref_article','ref_links','ref_textbooks','known_action']
columns_target=['drugbank_id','name','id','id_source','general_function','specific_function','gene_name','locus','cellular_location','transmembrane_regions','signal_regions','theoretical_pi','molecular_weight','go_classifiers','chromosome_location','pfams','gene_sequence','amino_acid_sequence','synonyms','xrefs']
columns_salt=['id','name','unii','inchikey','cas_number','average_mass','monoisotopic_mass']
columns_drug_salts=['drug_id','salt_id']
columns_products=['id','name','labeller','ndc_id','ndc_product_code','dpd_id','ema_product_code','ema_ma_number','started_marketing_on','ended_marketing_on','dosage_form','strength','route','fda_application_number','generic','over_the_counter','approved','country','source']
columns_drug_products=['drugbank_id','partner_id']
columns_metabolites=['drugbank_id','name']
columns_has_component=['target_id','petide_id']
columns_drug_pharmacologic_class=['drugbank_id','category']
columns_pharmacologic_class=['id','name']



drugbank_slim_df = drugbank_df[
    drugbank_df.groups.map(lambda x: 'approved' in x) &
    drugbank_df.inchi.map(lambda x: x is not None) &
    drugbank_df.type.map(lambda x: x == 'small molecule')
]
drugbank_slim_df.head()



# write drugbank tsv
path = os.path.join('data', 'drugbank_drug.tsv')
drugbank_df.to_csv(path, sep='\t', index=False, encoding='utf-8-sig')

# write slim drugbank tsv
path = os.path.join('data', 'drugbank-slim2_drug.tsv')
drugbank_slim_df.to_csv(path, sep='\t', index=False, encoding='utf-8')

generate_tsv_file(columns_drug_interaction,drug_interactions,'drugbank_interaction.tsv')
generate_tsv_file(columns_drug_pathway,drug_pathways,'drugbank_drug_pathway.tsv')
generate_tsv_file(columns_pathway_enzymes,pathway_enzymes,'drugbank_pathway_enzymes.tsv')
generate_tsv_file(columns_pathway,pathways,'drugbank_pathway.tsv')
generate_tsv_file(columns_reactions,reactions,'drugbank_reactions.tsv')
generate_tsv_file(columns_snp_effects, snp_effects,'drugbank_snp_effects.tsv')
generate_tsv_file(columns_mutated, mutated_gene_enzymes,'drugbank_mutated_gene_enzyme.tsv')
generate_tsv_file(columns_snp_adverse_drug_reactions, snp_adverse_drug_reactions,'drugbank_snp_adverse_drug_reaction.tsv')
generate_tsv_file(columns_drug_target, drug_targets,'drugbank_drug_target.tsv')
generate_tsv_file(columns_target, targets,'drugbank_targets.tsv')
generate_tsv_file(columns_drug_target, drug_enzymes,'drugbank_drug_enzyme.tsv')
generate_tsv_file(columns_target, enzymes,'drugbank_enzymes.tsv')
generate_tsv_file(columns_drug_target, drug_carriers,'drugbank_drug_carrier.tsv')
generate_tsv_file(columns_target, carriers,'drugbank_carrier.tsv')
generate_tsv_file(columns_drug_target, drug_transporters,'drugbank_drug_transporter.tsv')
generate_tsv_file(columns_target, transporters,'drugbank_transporter.tsv')
generate_tsv_file(columns_drug_salts, drug_salts,'drugbank_drug_salt.tsv')
generate_tsv_file(columns_salt, salts,'drugbank_salt.tsv')
generate_tsv_file(columns_drug_products, drug_products,'drugbank_drug_products.tsv')
generate_tsv_file(columns_products, products,'drugbank_products.tsv')
generate_tsv_file(columns_metabolites,metabolites,'drugbank_metabolites.tsv')
generate_tsv_file(columns_has_component,has_components,'drugbank_target_peptide_has_component.tsv')
generate_tsv_file(columns_drug_pharmacologic_class, pharmacologic_class_drug,'drugbank_drug_pharmacologic_class.tsv')
generate_tsv_file(columns_pharmacologic_class, pharmacologic_classes,'drugbank_pharmacologic_class.tsv')
print (datetime.datetime.utcnow())


# write drugbank tsv
#path = os.path.join('data', 'drugbank_interaction.tsv')
#drugbank_df_drug_interaction.to_csv(path, sep='\t', index=False)


