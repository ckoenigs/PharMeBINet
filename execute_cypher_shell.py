import shutil
import subprocess
import sys
import time
import os, glob

if len(sys.argv) != 4:
    print('something is missing neo4j path, password, cypher file')
neo4j_path = sys.argv[1]
password = sys.argv[2]
cypher_file = sys.argv[3]

try:
    subprocess.run([neo4j_path + '/cypher-shell', '-u', 'neo4j', '-p', password, '-f', cypher_file], check=True)
except subprocess.CalledProcessError as e:

    # Getting All Files List
    fileList = glob.glob(neo4j_path + '/../logs/*.log', recursive=True)
    print(fileList)

    # Remove all files one by one
    for file in fileList:
        try:
            os.remove(file)
        except OSError:
            print("Error while deleting file")
    # Getting All Files List
    shutil.rmtree(neo4j_path + '/../data/transactions/graph')
    time.sleep(30)
    print(f'Command {e.cmd} failed with error {e.returncode}')
    try:
        subprocess.run([neo4j_path + '/neo4j', 'restart'], check=True)
    except subprocess.CalledProcessError as e:

        print(f'Command {e.cmd} failed with error {e.returncode}')
        time.sleep(120)
        try:
            subprocess.run([neo4j_path + '/neo4j', 'restart'], check=True)
        except subprocess.CalledProcessError as e:
            print(f'Command {e.cmd} failed with error {e.returncode}')
            sys.exit(f'problem neo4j restart in cypher execution {cypher_file}')
    print('wait')
    time.sleep(100)
    try:
        subprocess.run([neo4j_path + '/cypher-shell', '-u', 'neo4j', '-p', password, '-f', cypher_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Command {e.cmd} failed with error {e.returncode}')
        sys.exit(f'problem neo4j cypher from {cypher_file} with {e.returncode}')
