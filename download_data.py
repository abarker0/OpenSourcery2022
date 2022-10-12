import requests

with open("data.json", "w") as f:
    f.write(requests.get("https://api.umd.io/v1/courses"))

