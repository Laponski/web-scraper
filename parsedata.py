import json

with open('data.json', 'r') as json_data:
    data = json.load(json_data)

for i in data:
    print(i['date'])

for i in data:
    if "obama" in i['tweet'].lower():
        print(i)