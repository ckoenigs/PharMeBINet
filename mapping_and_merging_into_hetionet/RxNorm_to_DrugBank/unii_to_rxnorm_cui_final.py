import datetime, csv
from zipfile import ZipFile
import io, os

# dictionary inchikey to rxnorm_ids
dict_inchikey_to_rxnorm_ids = {}

'''
go through all date in file UNIIs  Records.txt and remember only the one with a rxcui
file has properties:
    0:UNII
    1:PT	
    2:RN	
    3:EC	
    4:NCIT	
    5:RXCUI	
    6:ITIS	
    7:NCBI	
    8:PLANTS	
    9:GRIN	
    10:MPNS	
    11:INN_ID	
    12:MF	
    13:INCHIKEY	
    14:SMILES	
    15:UNII_TYPE
'''


def load_all_inchikey_and_rxnorm_in_dict():
    zip_file_name=''
    for file in os.listdir('.'):
        if file.endswith('.zip'):
            zip_file_name=file
    print(zip_file_name)
    with ZipFile(zip_file_name, 'r') as zipObj:
        for name in zipObj.namelist():
            if name.startswith('UNII'):
                f = zipObj.open(name,'r')
                csv_reader=csv.DictReader(io.TextIOWrapper(f, 'LATIN1'),delimiter='\t')
                g = open('results/UNIIs_with_RXCUI.tsv', 'w', encoding='utf-8')
                csv_writer=csv.writer(g, delimiter='\t')
                csv_writer.writerow(['unii','rxcui'])

                print (datetime.datetime.now())
                for line in csv_reader:
                    unii=line['UNII']
                    rxcui=line['RXCUI']
                    if rxcui!='':
                        csv_writer.writerow([unii,rxcui])
                g.close()
                f.close()
                break


print (datetime.datetime.now())


def main():
    print (datetime.datetime.now())
    print('load all information over rxcui and inchikey in a dictionary and generate a file with unii and rxnorm')

    load_all_inchikey_and_rxnorm_in_dict()

    print(
    '###########################################################################################################################')
    print (datetime.datetime.now())


if __name__ == "__main__":
    # execute only if run as a script
    main()
