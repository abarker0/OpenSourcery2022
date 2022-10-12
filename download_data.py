# Downloads course data

import requests
import json

with open("data.json", "w") as f:
    raw_data = requests.get("https://api.umd.io/v1/courses").json()
    formatted_data = json.dumps(raw_data, indent=4)
    f.write(formatted_data)
