import csv

path = "PathwayCommons9.All.hgnc.gmt"

read_file = open(path)
reader = csv.reader(read_file, delimiter='\t')
write_file = open("PathwayCommons9.All.hgnc_change.gmt", 'wb')
writer = csv.writer(write_file, delimiter='\t',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
for row in reader:
    if not row:
        continue
    url = row[0]
    description = row[1]
    description_update = ''
    # replace the ; in the names with a :
    for item in description.split('; '):
        if len(item.split(': ', 1)) == 2:
            description_update += item + '; '
        else:
            description_update = description_update[0:-2] + ': ' + item + '; '
    genes = list(set(row[2:]))
    list_write = [url, description_update[0:-2]]
    for gene in genes:
        list_write.append(gene)
    writer.writerow(list_write)
read_file.close()
