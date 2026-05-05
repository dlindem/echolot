import json

import requests, csv, time, re
result = []
count = 0
with open("soinuenea_commons.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    for row in reader:
        count += 1
        # print(row)
        page = row["title"]
        headers = {"User-Agent": "User:DL2204 python script"}
        params = {
            "action": "query",
            "format": "json",
            "list": "",
            "export": 1,
            "exportnowrap": 1,
            "titles": page,
            "formatversion": "2"
        }
        apiurl = "https://commons.wikimedia.org/w/api.php?"
        done = False
        while not done:
            try:
                r = requests.get(url=apiurl, headers=headers, params=params)
                time.sleep(1.1)
                done = True
            except requests.exceptions.ConnectionError:
                pass
        pagetext = r.text
        descre = re.search(r'\|description=\{\{eu\|1=([^\n\}]+)', pagetext)
        if descre:
            desc = descre.group(1)
        else:
            desc = "0"
        catlist = re.findall(r'\[\[(Category:[^\]]+)', pagetext)
        jsonre = re.search(r'xml:space="preserve">(\{[^<]+)</text>', pagetext)
        if jsonre:
            structured = json.loads(jsonre.group(1))
        else:
            structured = {}
        print(f"{count}\t{page}\t{desc}")
        result.append({
            "uri": f"https://commons.wikimedia.org/entity/{row['\ufeffmid']}",
            "page_title": page,
            "categories": catlist,
            "description": desc,
            "structured": structured
        })
        time.sleep(0.34)

with open("soinuenea_commons.json", "w") as jsonfile:
    json.dump(result, jsonfile)