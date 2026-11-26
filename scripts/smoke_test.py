import sys

import httpx

client = httpx.Client(base_url="http://localhost:8000")
r = client.post("/notes", json={"title": "new_note", "content": ""})
if r.status_code == 201:
    print("Ok: created")
else:
    print(f"Didn't create: {r.status_code}")
    sys.exit(1)
id_note = r.json()["id"]

r = client.get(f"/notes/{id_note}")
if r.status_code == 200 and r.json()["title"] == "new_note":
    print("Ok: got")
else:
    print(f"Didn't get: {r.status_code}, title: {r.text}")
    sys.exit(1)

r = client.patch(f"/notes/{id_note}", json={"title": "new_note_title"})
if r.status_code == 200 and r.json()["title"] == "new_note_title":
    print("Ok: edited")
else:
    print(f"Didn't edit: {r.status_code}, title: {r.text} ")
    sys.exit(1)

r = client.delete(f"/notes/{id_note}")
if r.status_code == 204:
    print("Ok: deleted")
else:
    print(f"Didn't delete: {r.status_code}")
    sys.exit(1)

r = client.get(f"/notes/{id_note}")
if r.status_code == 404:
    print("Ok: really deleted")
else:
    print(f"Note still exists: {r.status_code}")
    sys.exit(1)

print("All 5 checks passed")
