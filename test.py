import json
with open('settings.json')as f:
    j=json.load(f)
    print(j)