import io
import os
import re
import csv
import time
import random
import urllib.request

from typing import Tuple, List

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup


sub_sup_replacements = {
    '<sub>2</sub>': '&#8322;',
    '<sup>a</sup>': 'ᵃ',
    '<sup>b</sup>': 'ᵇ',
    '<sup>c</sup>': 'ᶜ',
    '<sup>d</sup>': 'ᵈ'
}


def get_website_source(url: str) -> str:
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/35.0.1916.47 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request) as response:
        return response.read().decode(response.headers.get_content_charset())


def get_cell_contents(cell, interpret_cells: bool) -> str:
    if interpret_cells:
        parts = [x.strip() for x in cell.text.split('\n')]
        return ' '.join(parts).replace(u'\xa0', ' ')
    else:
        return ''.join([str(x) for x in cell.contents]).strip()


def parse_table_from_file(file: str, interpret_cells: bool = True) -> Tuple[List[str], List[List[str]]]:
    with io.open(file, 'r', encoding='utf-8') as f:
        source = f.read()
    return parse_table(source, interpret_cells)


def parse_table(source: str, interpret_cells: bool = True) -> Tuple[List[str], List[List[str]]]:
    if interpret_cells:
        for replacement in sub_sup_replacements:
            source = source.replace(replacement, sub_sup_replacements[replacement])
    parsed_html = BeautifulSoup(source, "lxml")
    column_count = None
    header = []
    rows = []
    current_rowspans = []
    for row in parsed_html.find_all('tr'):
        cells = [x for x in row.find_all('td')]
        if len(cells) == 0:
            cells = [x.text.strip() for x in row.find_all('th')]
            column_count = len(cells)
            current_rowspans = [[0, None]] * column_count
            header = cells
        else:
            if column_count is None:
                column_count = len(cells)
                current_rowspans = [[0, None]] * column_count
            for i in range(0, len(current_rowspans)):
                if current_rowspans[i][0] > 0:
                    cells.insert(i, current_rowspans[i][1])
                    current_rowspans[i][0] -= 1
            for i in range(0, len(cells)):
                if 'rowspan' in cells[i].attrs:
                    current_rowspans[i][0] = int(cells[i].attrs['rowspan']) - 1
                    del cells[i].attrs['rowspan']
                    current_rowspans[i][1] = cells[i]
            rows.append([get_cell_contents(x, interpret_cells) for x in cells])
    return header, rows


dbcat_pattern = re.compile(r'DBCAT[0-9]+')

categories = {}


def process_categories_page(source: str):
    table = parse_table(source, False)
    for row in table[1]:
        category_id = list(dbcat_pattern.finditer(row[0]))[0].group(0)
        name = row[0][row[0].index('>') + 1:-4]
        categories[category_id] = name


page_number = 1
last_page_num = 1
while page_number <= last_page_num:
    print('Download page %s of %s' % (page_number, last_page_num))
    source = get_website_source('https://www.drugbank.ca/categories?page=%s' % page_number)
    process_categories_page(source)
    if '<li class="page-item last"><a class="page-link" href="/categories?page=' in source:
        last_page_num = int(
            source.split('<li class="page-item last"><a class="page-link" href="/categories?page=')[1].split('"')[0])
    page_number += 1
    time.sleep(random.randint(1, 1))

with io.open(os.path.join(os.path.dirname(__file__), 'drugbank/categories.csv'), 'w', encoding='utf-8',
             newline='') as f:
    writer = csv.writer(f, delimiter=',', quotechar='"')
    writer.writerow(['id', 'name'])
    for _id in categories:
        writer.writerow([_id, categories[_id]])
