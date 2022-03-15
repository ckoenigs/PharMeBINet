import datetime
import sys, csv

sys.path.append("..")
import change_xref_source_name_to_a_specifice_form

sys.path.append("../..")
import create_connection_to_databases

'''
create a connection with neo4j
'''


def create_connection_with_neo4j():
    # set up authentication parameters and connection
    global g
    g = create_connection_to_databases.database_connection_neo4j()



def get_all_metabolites_with_xrefs():
    """
    prepare the file and the cypher query to integrate the metabolite. Then load all metabolites of hmdb and prepare the
    xrefs. Then write into tsv file.
    :return:
    """
    file_name='metabolite/new.tsv'
    file=open(file_name,'w',encoding='utf-8')
    csv_writer=csv.writer(file,delimiter='\t')
    csv_writer.writerow(['identifier','xrefs'])

    # not consider: creation_date, spectra, update_date, version
    cypher_query='''Using Periodic Commit 10000 Load CSV  WITH HEADERS From "file:%smaster_database_change/mapping_and_merging_into_hetionet/hmdb/%s" As line FIELDTERMINATOR '\\t' Match (n:Metabolite_HMDB{identifier:line.identifier}) Create (m:Metabolite{identifier:n.identifier , average_molecular_weight:n.average_molecular_weight, biospecimen_locations:n.biospecimen_locations, cas_number:n.cas_registry_number,cellular_locations:n.cellular_locations,chemical_formula:n.chemical_formula,description:n.description,experimental_properties:n.experimental_properties,inchi:n.inchi,inchikey:n.inchikey,iupac_name:n.iupac_name, monisotopic_molecular_weight:n.monisotopic_molecular_weight, name:n.name,predicted_properties:n.predicted_properties,secondary_accessions:n.secondary_accessions,smiles:n.smiles, state:n.state, status:n.status, synonyms:n.synonyms, synthesis_reference:n.synthesis_reference,taxonomy_alternative_parents:n.taxonomy_alternative_parents,taxonomy_alternative_parents:n.taxonomy_alternative_parents,taxonomy_class:n.taxonomy_class,taxonomy_description:n.taxonomy_description,taxonomy_direct_parent:n.taxonomy_direct_parent,taxonomy_external_descriptors:n.taxonomy_external_descriptors,taxonomy_kingdom:n.taxonomy_kingdom,taxonomy_molecular_framework:n.taxonomy_molecular_framework,taxonomy_sub_class:n.taxonomy_sub_class,taxonomy_substituents:n.taxonomy_substituents, taxonomy_super_class:n.taxonomy_super_class,tissue_locations:n.tissue_locations,traditional_iupac:n.traditional_iupac, xrefs:split(line.xrefs,"|"), hmdb:'yes', resource:['HMDB'], source:"HMDB", license:'Creative Commons (CC) Attribution-NonCommercial (NC) 4.0 International Licensing '}) Create (m)-[:equal_to_hmdb_metabolite]->(n);\n'''
    cypher_query = cypher_query % (path_of_directory, file_name)
    cypher_file.write(cypher_query)

    # add an indice on metabolite
    query = 'Create Constraint On (node:Metabolite) Assert node.identifier Is Unique; \n'
    cypher_file.write(query)

    query='MATCH (p:Metabolite_HMDB) Return p.identifier, p.xrefs'
    results=g.run(query)
    for identifier, xrefs, in results:

        if xrefs:

            csv_writer.writerow([identifier, '|'.join(change_xref_source_name_to_a_specifice_form.go_through_xrefs_and_change_if_needed_source_name(xrefs,'Metabolite'))])


        else:
            csv_writer.writerow([identifier,''])


def main():
    print(datetime.datetime.now())

    global path_of_directory, cypher_file
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
    else:
        sys.exit('need a path hmdb metabolite')

    cypher_file = open('output/cypher.cypher', 'w', encoding='utf-8')

    print('##########################################################################')

    print(datetime.datetime.now())
    print('connection to db')

    create_connection_with_neo4j()

    print('##########################################################################')

    print(datetime.datetime.now())
    print('Load all hmdb Metabolite from database and write prepared information into tsv file')

    get_all_metabolites_with_xrefs()

    print('##########################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
