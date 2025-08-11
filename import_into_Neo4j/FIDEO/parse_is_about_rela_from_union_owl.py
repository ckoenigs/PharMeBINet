import csv
import sys

# write the extra edges into the is-about tsv file
with open('data/relationships.tsv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file, delimiter='\t')
    # has parent id \t child id
    with open('output/rela_is_about.tsv', 'a', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        next(reader, None)
        for row in reader:
            if not '<http://purl.obolibrary.org/obo/fideo/' in row[0]:
                sys.exit('error in extra FIDO edge file!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            child_id = row[0].replace('<http://purl.obolibrary.org/obo/fideo/', '')[:-1].replace('_', ':')
            parent_id = row[2].replace('<http://purl.obolibrary.org/obo/fideo/', '')[:-1].replace('_', ':')
            rela_type = row[1]
            if rela_type != '<http://purl.obolibrary.org/obo/IAO_0000136>':
                sys.exit('Other relatype than is_about!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            print(parent_id, child_id)
            writer.writerow([parent_id, child_id])
