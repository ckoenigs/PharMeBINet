import io
import os
import re
import csv
import time
import random
import urllib.request
import requests

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:101.0) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/35.0.1916.47 Safari/537.36 Gecko/20100101 Firefox/113.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Alt-Used':'go.drugbank.com',
        'Cookie':'_hjSessionUser_191585=eyJpZCI6ImQwZjFkNTRlLTk3ZmUtNWIyNi1iZmI5LWQ1OTgwZDI3NmIxOSIsImNyZWF0ZWQiOjE3MzE5MTI4MzU5NDgsImV4aXN0aW5nIjp0cnVlfQ==; __adroll_fpc=b65395dd1e3aab54e35065e2a5797ac6-1731912836344; __hssrc=1; cookieyes-consent=consentid:RTZHNkcyNEQzWTZEN08yeml0Sjk3bkltNFBRZENYNDc,consent:no,action:yes,necessary:yes,functional:no,analytics:no,performance:no,advertisement:no,other:no; cf_clearance=NevHS3Hhf6pQGk3pcOsDa1rn2qWLIweXklbu3_HsahA-1736855362-1.2.1.1-lnwHPfRhh1r4d.COKrJlN6WINGhwngWx8Ik3FLiupOwSmJSGtKMT_dhCD8Eu9F1ZBS32vTHmMG0Ef0ddW7fCzHk.eOaiTXL7PxHWFB_dYkVYhHuNqQ.swN803pctAwWvZtDdxsDiWv5IUN4pLK_5BedFISkFFld3NQpEJVmgbwaSc9OvgM.k0A5vDeIMewsm1MePtXbjNx0_rQWE0_N3u6VhgOs0WDGwO2jMOcPHZUdWtzX4A48UdC4E6E.UxOYZP1kFJfAG8P_2Q3hnKRisRqpU.U1z9_PXMY_qAoMcL80; _hjSession_191585=eyJpZCI6IjhmZGUyNzEzLWZiMDQtNDNlZC05MTUxLTJlZjI3NGI0YzY2MCIsImMiOjE3Mzk0MTk5ODgxNDAsInMiOjEsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjowLCJzcCI6MH0=; _omx_drug_bank_session=Wp1x1ccp9AgI7KYTFd1IgGb6%2FWkpbuU%2F5i4nrN5PN2Komzo3urjI8zWaz5nKyFWWoSX%2FLnILjA65WvPCkToLZd%2BPpWvPxsVo%2Bx9ue71%2BQZzbmjZINKTbblui%2BgyuuFs50QNEpjtGL6GXNFnmLldeYDp95uvGCJyXO6VAfzyJlS24BQEs4ocQ%2FGvlZBhHIsbVcaftMl40GeCTyDMRg3pW24k6HBvLJWhuF8znD668gkYPwZvfel8tONCs%2F2YAG6%2BVgIzCgdiqdhpBMgp3fVWFc7T7eAy6f0iHhUsTGjn5FKC70TDYlXf5AmlnUs1ysGfrObuoy0vKPg0PVCDbLm3asdp0hHmejCGMnz6p2obWEMFii%2BUVX4ZNtUWx%2BS04RaqHXuP5nId%2Bcn81urkiSNL73m8E%2BjokKiXa1YWB6%2BqA20k8GsUREER5RsYOo4pt0J4od%2Fz8RLgiOmEPn3dPT8rNl2yVDYRlsbiVas5ntgfr4BJN5ADCYrL5fI8Con7zLDmlvfCwHyDacnzy0Of3nGHWBdyF0acpAVyLGholfBrrhRQf%2BwYvDp6cxR%2BNp5%2Ba2aFr5ku%2BeGKGTCRR%2FFsVrKW5evRme6zK92lwCFOOEihmF1eo%2FBwzKyTIZUSC4qjULzaixskHc9hZyhUOEHWozAZnh85P5SaCvewroxU%2BPV5%2F2%2ByQQleKRgr8%2FkZMA56vChmgR3yMUH9oEubT8ZAJBfDn%2BGfZc0QkurHMv4EuHXkYlDkbQaEEf2AlXxwd51CrxApkVdVIDMtcJP6ebHC5PGQamMAQ%2F81oR9BkUDyS0b7P--OhYoZl5el%2BNJmXYn--5WaT%2FVnQrlC7j3295qkMRA%3D%3D; __hssc=49600953.3.1739420071822; __ar_v4=FAPGZQH4LBBKDJ7BEHFFXV%3A20250214%3A8%7CTAP76L6PNZHKTLZBWZQUKO%3A20250214%3A8%7CDA674JDALNFITKMDU7VWN6%3A20250214%3A8'

    }
    response = requests.get(url, headers=request_headers)
    web_page = response.text

    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=10) as response:
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
    print('last page',last_page_num)
    print('Download page %s of %s' % (page_number, last_page_num))
    print('https://go.drugbank.com/categories?page=%s' % page_number)
    # source = get_website_source('https://www.drugbank.ca/categories?page=%s' % page_number)
    source = get_website_source('https://go.drugbank.com/categories?page=%s' % page_number)
    process_categories_page(source)
    if '<li class="page-item last"><a class="page-link" href="/categories?page=' in source:
        last_page_num = int(
            source.split('<li class="page-item last"><a class="page-link" href="/categories?page=')[1].split('"')[0])
    page_number += 1
    time.sleep(random.randint(1, 1))

with io.open(os.path.join(os.path.dirname(__file__), 'drugbank/categories.tsv'), 'w', encoding='utf-8',
             newline='') as f:
    writer = csv.writer(f, delimiter='\t', quotechar='"')
    writer.writerow(['id', 'name'])
    for _id in categories:
        writer.writerow([_id, categories[_id]])
