import json
import subprocess

API_URL = "http://127.0.0.1:8001/process_query"
TOTAL_REQUESTS = 50
CONCURRENT_REQUESTS = 5

# JSON dosyasını oku
with open("queries.json", "r", encoding="utf-8") as file:
    queries = json.load(file)

# Her sorguyu Hey ile POST isteği olarak gönder
for query in queries:
    json_payload = json.dumps(query, ensure_ascii=False)  # Türkçe karakterleri koru
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
