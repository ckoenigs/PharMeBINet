import subprocess
import sys
import time

if len(sys.argv) != 4:
    print('something is missing neo4j path, password, cypher file')
neo4j_path = sys.argv[1]
password = sys.argv[2]
cypher_file = sys.argv[3]
try:
    subprocess.run([neo4j_path + '/cypher-shell', '-u', 'neo4j', '-p', password, '-f', cypher_file], check=True)
except subprocess.CalledProcessError as e:
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
    time.sleep(30)
    try:
        subprocess.run([neo4j_path + '/cypher-shell', '-u', 'neo4j', '-p', password, '-f', cypher_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Command {e.cmd} failed with error {e.returncode}')
        sys.exit(f'problem neo4j cypher from {cypher_file} with {e.returncode}')
