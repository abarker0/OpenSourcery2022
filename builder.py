import requests
import json


data = requests.get("https://api.umd.io/v1/courses")
# data = json.load(raw_json)
# print(json.dumps(data, indent=4, sort_keys=True))