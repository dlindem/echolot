import json, csv
import time

with open("uploaded_categories.csv", "r") as csvfile:
    csv_rows = csv.DictReader(csvfile, delimiter="\t")
    cat_map = {}
    for row in csv_rows:
        cat_map[row["pageid"]] = row['qid']

parentjson = {}
with open("categories.jsonl") as file:
    for line in file.readlines():
        data = json.loads(line)
        parent_page_id = data['cat_page_id']
        if "14" not in data['content']:
            continue
        for child in data['content']["14"]:
            child_page_id = child['pageid']
            if child_page_id not in parentjson.keys():
                parentjson[child_page_id] = []
            if parent_page_id not in parentjson[child_page_id]:
                parentjson[child_page_id].append(parent_page_id)

with open("categories_parents.json", "w") as file:
    json.dump(parentjson, file, indent=2)
