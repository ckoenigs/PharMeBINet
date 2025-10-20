import time
import sys

sys.path.append("../..")
import create_connection_to_databases

# create connection
driver = create_connection_to_databases.database_connection_neo4j_driver()
g = driver.session(database='graph')

POLL_INTERVAL = 5  # Seconds between polling attempts

def check_indices_status():
    # Query to list indices and their states
    result = g.run("SHOW INDEXES")
    indices = result.data()
    incomplete = [index for index in indices if index.get("state", "") != "ONLINE"]
    return incomplete

def wait_for_indices():
    print("Waiting for all indices to be ONLINE...")
    while True:
        not_ready = check_indices_status()
        if len(not_ready)==0:
            print("All indices are ONLINE!")
            break
        else:
            print(f"{len(not_ready)} index(es) still not ONLINE. Retrying in {POLL_INTERVAL}s...")
            time.sleep(POLL_INTERVAL)
try:
    wait_for_indices()
finally:
    driver.close()
