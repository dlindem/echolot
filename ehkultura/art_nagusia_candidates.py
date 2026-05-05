import json, requests, re, time, csv

result = "cat_id\tcat_qid\tcat_title\tnagusia_candidate\tnagusia_onwiki\n"

with open("uploaded_categories.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    uploaded_categories = {"root": "Q4"}
    for row in reader:
        if row["pageid"] == "root":
            continue
        uploaded_categories[int(row["pageid"])] = row['qid']

with open("categories.jsonl") as jsonlfile:
    lines = jsonlfile.readlines()
count = 0
for line in lines:
    data = json.loads(line)
    cat_page_id = data["cat_page_id"]
    if cat_page_id == "root":
        continue
    cat_page = data['cat_page']
    candidate = cat_page.replace("Kategoria:", "")
    if "0" not in data['content']:
        continue

    for entry in data['content']['0']:
        if entry['title'] == candidate:
            count += 1
            print(f"{count}: Found match: {candidate}")
            apiurl = f'https://eu.wikipedia.org/w/api.php?action=query&format=json&export=1&exportnowrap=1&formatversion=2&pageids={cat_page_id}'
            print(apiurl)
            headers = {"User-Agent": "User:DL2204 python script"}
            r = requests.get(url=apiurl, headers=headers)
            time.sleep(0.34)
            pagetext = r.text
            nagusisearch = re.search(r'\{\{[Nn]agusia\|([^\}]*)\}\}', pagetext)
            if nagusisearch:
                nagusia = nagusisearch.group(1)
                if nagusia == "":
                    nagusia = candidate
            else:
                nagusia = "0"


            result += f"{cat_page_id}\t{uploaded_categories[cat_page_id]}\t{cat_page}\t{candidate}\t{nagusia}\n"



with open("nagusia_candidates.csv", "w") as outfile:
    outfile.write(result)