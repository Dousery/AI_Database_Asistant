import json
import subprocess
import time 

API_URL = "http://127.0.0.1:8001/process-query/"
TOTAL_REQUESTS = 10
CONCURRENT_REQUESTS = 1

with open("queries.json", "r", encoding="utf-8") as file:
    queries = json.load(file)

for query in queries:
    json_payload = json.dumps(query, ensure_ascii=False) 
    command = [
        "hey",
        "-n", str(TOTAL_REQUESTS),
        "-c", str(CONCURRENT_REQUESTS),
        "-m", "POST",
        "-H", "Content-Type: application/json",
        "-d", json_payload,
        API_URL
    ]
    
    print(f"Executing: {' '.join(command)}")
    subprocess.run(command)
    
    time.sleep(60)