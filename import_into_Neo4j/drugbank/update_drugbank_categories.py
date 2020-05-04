import io
import os
import re
import csv
import time
import random
from utils import html_utils

dbcat_pattern = re.compile(r'DBCAT[0-9]+')

categories = {}


def process_categories_page(source: str):
    table = html_utils.parse_table(source, False)
    for row in table[1]:
        category_id = list(dbcat_pattern.finditer(row[0]))[0].group(0)
        name = row[0][row[0].index('>') + 1:-4]
        categories[category_id] = name


page_number = 1
last_page_num = 1
while page_number <= last_page_num:
    print('Download page %s of %s' % (page_number, last_page_num))
    source = html_utils.get_website_source('https://www.drugbank.ca/categories?page=%s' % page_number)
    process_categories_page(source)
    if '<li class="page-item last"><a class="page-link" href="/categories?page=' in source:
        last_page_num = int(
            source.split('<li class="page-item last"><a class="page-link" href="/categories?page=')[1].split('"')[0])
    page_number += 1
    time.sleep(random.randint(1, 1))

with io.open(os.path.join(os.path.dirname(__file__), '../../data/DrugBank/categories.csv'), 'w', encoding='utf-8',
             newline='') as f:
    writer = csv.writer(f, delimiter=',', quotechar='"')
    writer.writerow(['id', 'name'])
    for _id in categories:
        writer.writerow([_id, categories[_id]])
