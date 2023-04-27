import re
import json
import requests
from datetime import datetime
import sys
sys.path.append('../..')
import pharmebinetutils

headers = {'User-Agent': 'DataSource-Status Fetcher'}
source = requests.get('https://precision.fda.gov/uniisearch/archive', headers=headers).content.decode('utf-8')

#print(source)
start_date='2012-01-21'
latest_date=date_object = datetime.strptime(start_date, '%Y-%m-%d').date()
final_name=''
file_names_pattern=re.compile(r'([0-9]{4})-([0-9]{2})-([0-9]{2})/UNII_Data_\1\2\3\.zip')
for file_name in file_names_pattern.finditer(source):
    file_name_from_text=file_name.group()
    first_date=file_name_from_text.split('/',1)[0]
    date_object = datetime.strptime(first_date, '%Y-%m-%d').date()
    if date_object>latest_date:
        latest_date=date_object
        final_name=file_name_from_text

        print(date_object)

print(latest_date)
print('final name',final_name)

#source = requests.get('https://qnyqxh695c.execute-api.us-east-1.amazonaws.com/production/v1/get-file/' + final_name, headers=headers).content.decode('utf-8')
#download_url = json.loads(source)['url']
download_url='https://precision.fda.gov/uniisearch/archive/'+final_name
print(download_url)
print('blub')

#wget.download(download_url, out='.')
pharmebinetutils.download_file(download_url)