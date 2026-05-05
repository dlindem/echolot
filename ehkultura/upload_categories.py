import csv, requests, json

import ehwbi, time

# reference time of retrieval for wikibase
references = ehwbi.References()
reference = ehwbi.Reference()
reference.add(ehwbi.Time(prop_nr="P8", time="now"))
references.add(reference)

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
    count += 1
    data = json.loads(line)
    print(f"{count}: {data}")
    if data["cat_page_id"] == "root":
        continue
    if int(data["cat_page_id"]) in uploaded_categories:
        print(f"{data['cat_page_id']} done before.")
        continue
    # get wikidata info
    apiurl = f'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=euwiki&format=json&titles={data['cat_page'].replace(
        " ", "_")}'
    print(apiurl)
    headers = {"User-Agent": "User:DL2204 python script"}
    wdjsonsource = requests.get(url=apiurl, headers=headers)
    wdjson = wdjsonsource.json()
    print(wdjson)
    # with open('entity.json', 'w') as jsonfile:
    #      json.dump(wdjson, jsonfile, indent=2)
    entity = next(iter(wdjson['entities'].items()))
    wd_claim = None
    if "missing" in entity[1]:
        wd_claim = ehwbi.ExternalID(prop_nr="P1", snaktype=ehwbi.WikibaseSnakType.NO_VALUE, references=references)
    elif entity[0].startswith("Q"):
        wd_claim = ehwbi.ExternalID(prop_nr="P1", value=entity[0], references=references)
    if not wd_claim:
        input(f"Problem. No 'entity' found in request result.")
    # produce wikibase item

    item = ehwbi.wbi.item.new()
    item.claims.add(ehwbi.Item(prop_nr="P5", value="Q2", references=references))
    item.claims.add(wd_claim)
    item.claims.add(ehwbi.ExternalID(prop_nr="P6", value=data["cat_page"].replace(" ", "_"), references=references))
    item.claims.add(ehwbi.ExternalID(prop_nr="P7", value=str(data["cat_page_id"]), references=references, qualifiers=[ehwbi.String(prop_nr="P11", value="14")]))
    item.labels.set(language="mul", value=data["cat_page"].replace("_", " "))
    item.labels.set(language="eu", value=data["cat_page"].replace("_", " "))
    item.descriptions.set(language="eu", value="Kategoria euskarazko Wikipedian")
    # print(item)
    try:
        item.write()
        with open("uploaded_categories.csv", "a") as csvfile:
            csvfile.write(f"{data["cat_page_id"]}\t{item.id}\n")
        print(f"Written data to https://ehkultura.wikibase.cloud/wiki/Item:{item.id}")
        uploaded_categories[int(data["cat_page_id"])] = item.id
    except:
        pass

    time.sleep(1)




