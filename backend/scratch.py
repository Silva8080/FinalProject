import httpx

r = httpx.post("http://127.0.0.1:8765", json={"action": "version", "version": 6})
print(httpx.post("http://127.0.0.1:8765", json={"action": "deckNames", "version": 6}).json())
print(httpx.post("http://127.0.0.1:8765", json={"action": "modelNames", "version": 6}).json())