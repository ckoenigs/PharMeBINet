import datetime
import sys, csv

sys.path.append("../..")
import create_connection_to_databases
import pharmebinetutils


def create_connection_with_neo4j():
    """
    create connection to neo4j
    :return:
    """
    global g, driver
    driver = create_connection_to_databases.database_connection_neo4j_driver()
    g = driver.session(database='graph')

# all nodes id to node infos
dict_nodes = {}


# header for the tsv files
header = ['PUBCHEM_ATOM_UDEF_STEREO_COUNT', 'PUBCHEM_COMPONENT_COUNT',
          'PUBCHEM_SMILES', 'PUBCHEM_XLOGP3_AA', 'PUBCHEM_IUPAC_INCHIKEY', 'PUBCHEM_ATOM_DEF_STEREO_COUNT',
          'PUBCHEM_CACTVS_TAUTO_COUNT', 'PUBCHEM_CACTVS_HBOND_DONOR', 'PUBCHEM_COORDINATE_TYPE',
          'PUBCHEM_BOND_UDEF_STEREO_COUNT', 'PUBCHEM_MOLECULAR_FORMULA', 'PUBCHEM_TOTAL_CHARGE',
           'PUBCHEM_CACTVS_COMPLEXITY', 'PUBCHEM_HEAVY_ATOM_COUNT',
           'PUBCHEM_IUPAC_NAME_MARKUP', 'PUBCHEM_COMPOUND_CANONICALIZED',
          'PUBCHEM_CACTVS_HBOND_ACCEPTOR', 'PUBCHEM_IUPAC_CAS_NAME', 'PUBCHEM_IUPAC_NAME',
          'PUBCHEM_IUPAC_TRADITIONAL_NAME', 'PUBCHEM_MONOISOTOPIC_WEIGHT',
          'PUBCHEM_IUPAC_INCHI', 'PUBCHEM_CACTVS_ROTATABLE_BOND', 'PUBCHEM_EXACT_MASS',
          'PUBCHEM_BOND_DEF_STEREO_COUNT', 'PUBCHEM_IUPAC_OPENEYE_NAME', 'PUBCHEM_ISOTOPIC_ATOM_COUNT',
          'PUBCHEM_MOLECULAR_WEIGHT', 'PUBCHEM_CACTVS_TPSA', 'PUBCHEM_IUPAC_SYSTEMATIC_NAME', 'PUBCHEM_XLOGP3',
          'PUBCHEM_NONSTANDARDBOND'
        # , 'PUBCHEM_COMPOUND_CID', 'PUBCHEM_CONNECTIVITY_SMILES','PUBCHEM_BONDANNOTATIONS','PUBCHEM_CACTVS_SUBSKEYS',
          ]


def generate_node_tsv_and_query():
    """
    Generate node tsv file and cypher query
    :return:
    """
    global csv_writer
    file_name = 'chemical/node.tsv'
    file = open(file_name, 'w', encoding='utf-8')
    csv_writer = csv.writer(file, delimiter='\t')
    csv_writer.writerow(['chemical_id','resource', 'synonyms', 'computed_properties'])

    # dictionary pubchem identifier to resource and synonyms
    dict_identifier_to_synonyms = {}
    query = 'Match (n:Chemical) Where n.source starts with "PubChem" Return n.identifier, n.resource, n.synonyms'
    for identifier, resource, synonyms,  in g.run(query):
        synonyms = set(synonyms) if synonyms else set()
        dict_identifier_to_synonyms[identifier] = [set(resource),synonyms]

    properties_which_are_computed=set()
    query = 'Match (n:PubChem_compounds) Return n'
    for node, in g.run(query):
        identifier = node['identifier']
        synonyms= dict_identifier_to_synonyms[identifier][1]
        node=dict(node)
        computed_properties = []
        for key,value in node.items():
            key_lower=key.lower()
            if 'name' in key_lower:
                synonyms.add(value)
            elif 'cactvs' in key_lower:
                properties_which_are_computed.add(key)
                computed_properties.append(key.split('CACTVS_')[1].lower().replace('_',' ').title()+'::'+value+'::Cactvs')
            elif 'XLOGP3' in key:
                properties_which_are_computed.add(key)
                computed_properties.append(key.replace('PUBCHEM_','').lower().replace('_',' ').title()+'::'+value+'::XLogP3')
            elif 'stereo' in key_lower or 'atom' in key_lower or 'weight' in key_lower:
                properties_which_are_computed.add(key)
                computed_properties.append(key.replace('PUBCHEM_','').lower().replace('_',' ').title()+'::'+value+'::PubChem')
            elif key=='PUBCHEM_TOTAL_CHARGE':
                properties_which_are_computed.add(key)
                computed_properties.append(key.replace('PUBCHEM_','').lower().replace('_',' ').title()+'::'+value+'::PubChem')


        csv_writer.writerow([identifier, pharmebinetutils.resource_add_and_prepare(
                        dict_identifier_to_synonyms[identifier][0], "PubChem" ), '|'.join(synonyms), '|'.join(computed_properties) ])
    file.close()

    with open('chemical/cypher.cypher', 'w', encoding='utf-8') as f:
        #
        query = 'Match (m:Chemical{identifier:line.chemical_id}), (n:PubChem_compounds{identifier:line.chemical_id}) Set m.pubchem="yes", m.license ="https://www.ncbi.nlm.nih.gov/home/about/policies/", m.calculated_properties_kind_value_source= split(line.computed_properties,"|"), m.resource = split(line.resource,"|"), m.synonyms = split(line.synonyms,"|"),  m.url="https://pubchem.ncbi.nlm.nih.gov/compound/"+line.chemical_id,  %s  Create (m)-[:equal_to_pubchem]->(n)'
        query_prop = []
        for head in header:
            if not head in ['PUBCHEM_COMPOUND_CID','PUBCHEM_IUPAC_INCHIKEY','PUBCHEM_IUPAC_INCHI'] and not head in properties_which_are_computed:
                query_prop.append('m.'+head.replace('PUBCHEM_','').lower() + '=n.' + head)
            elif head in ['PUBCHEM_IUPAC_INCHIKEY','PUBCHEM_IUPAC_INCHI']:
                query_prop.append('m.'+head.replace('PUBCHEM_IUPAC_','').lower() + '=n.' + head)


        query = query % ', '.join(query_prop)
        query = pharmebinetutils.get_query_import(path_of_directory_pubchem, f'{file_name}', query)
        f.write(query)

def main():
    global license, path_of_directory_pubchem, path_to_data
    if len(sys.argv) > 1:
        path_of_directory = sys.argv[1]
        path_of_directory_pubchem = path_of_directory + 'mapping_and_merging_into_hetionet/pubchem/'
        # license = sys.argv[2]
    else:
        sys.exit('need a path and license and path to data ')

    print(datetime.datetime.now())
    print('diseaserate connection with neo4j')

    create_connection_with_neo4j()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())
    print('prepare query and tsv file')

    generate_node_tsv_and_query()

    driver.close()

    print(
        '###########################################################################################################################')

    print(datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
