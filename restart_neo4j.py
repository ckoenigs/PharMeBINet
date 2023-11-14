import subprocess
import sys
import time

if len(sys.argv) !=2:
    print('something is missing')
neo4j_path=sys.argv[1]
print(neo4j_path)
try:
    subprocess.run([neo4j_path+'/neo4j', 'restart'],check=True)
except subprocess.CalledProcessError as e:
    print(f'Command {e.cmd} failed with error {e.returncode}')
    time.sleep(120)
    try:
        subprocess.run([neo4j_path + '/neo4j', 'restart'], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Command {e.cmd} failed with error {e.returncode}')
        sys.exit('problem neo4j 2')