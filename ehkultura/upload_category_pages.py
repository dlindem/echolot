import csv, requests, json, sys
from wikibaseintegrator.wbi_helpers import execute_sparql_query
from wikibaseintegrator.wbi_enums import ActionIfExists

import ehwbi, time

# reference time of retrieval for wikibase
references = ehwbi.References()
reference = ehwbi.Reference()
reference.add(ehwbi.Time(prop_nr="P8", time="now"))
references.add(reference)

# Qid of the categories to get and upload the pages
query = """PREFIX ehwb: <https://ehkultura.wikibase.cloud/entity/>
PREFIX ehdp: <https://ehkultura.wikibase.cloud/prop/direct/>
PREFIX ehp: <https://ehkultura.wikibase.cloud/prop/>
PREFIX ehps: <https://ehkultura.wikibase.cloud/prop/statement/>
PREFIX ehpq: <https://ehkultura.wikibase.cloud/prop/qualifier/>
PREFIX ehpr: <https://ehkultura.wikibase.cloud/prop/reference/>
PREFIX ehno: <https://ehkultura.wikibase.cloud/prop/novalue/>

select ?subcat where
{?subcat ehdp:P5 ehwb:Q2; ehdp:P9* ehwb:Q613. # root element "Euskal Herriko Eraikinak"
 }"""

bindings = execute_sparql_query(query=query)['results']['bindings']
print(f"Got {len(bindings)} results from Wikibase SPARQL endpoint.")
time.sleep(.3)
cat_qid_to_upload = []
for binding in bindings:
    cat_qid_to_upload.append(binding['subcat']['value'].replace("https://ehkultura.wikibase.cloud/entity/", ""))

with open("uploaded_categories.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    uploaded_categories = {"root": "Q4"}
    for row in reader:
        if row["pageid"] == "root":
            continue
        uploaded_categories[int(row["pageid"])] = row['qid']
with open("uploaded_pages.csv") as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    uploaded_pages = {}
    for row in reader:
        uploaded_pages[int(row["pageid"])] = row['qid']

with open("categories.jsonl") as jsonlfile:
    lines = jsonlfile.readlines()
pages_dict = {}
for line in lines:
    data = json.loads(line)
    cat_id = data["cat_page_id"]
    cat_page = data["cat_page"]
    cat_qid = uploaded_categories[cat_id]
    if "0" not in data['content']:
        continue
    for page in data["content"]["0"]:
        page_id = page["pageid"]
        title = page["title"]
        if title not in pages_dict:
            pages_dict[title] = {"pageid": page_id, "cats": []}
        pages_dict[title]['cats'].append(cat_qid)

count = 0
for page_title in pages_dict:
    count += 1

    # check if the page is linked to relevant categories
    do_it = False
    for cat_qid in pages_dict[page_title]["cats"]:
        if cat_qid in cat_qid_to_upload:
            do_it = True
            break
    if not do_it:
        continue

    page_id = pages_dict[page_title]["pageid"]
    item_id = None
    if page_id in uploaded_pages:
        item_id = uploaded_pages[page_id]
        print(f"{page_id} already there as {item_id}.")

    print(f"{count} of {len(pages_dict)}: {page_title}.")

    # get wikidata info
    apiurl = f'https://www.wikidata.org/w/api.php?action=wbgetentities&sites=euwiki&format=json&titles={page_title.replace(" ", "_")}'
    print(apiurl)
    headers = {"User-Agent": "User:DL2204 python script"}
    wdjsonsource = requests.get(url=apiurl, headers=headers)
    wdjson = wdjsonsource.json()
    print(wdjson)
    # with open('entity.json', 'w') as jsonfile:
    #      json.dump(wdjson, jsonfile, indent=2)
    entity = next(iter(wdjson['entities'].items()))
    wd_claim = None
    eu_label = page_title.replace("_", " ")
    en_label = eu_label
    es_label = eu_label
    fr_label = eu_label
    if "missing" in entity[1]:
        wd_claim = ehwbi.ExternalID(prop_nr="P1", snaktype=ehwbi.WikibaseSnakType.NO_VALUE, references=references)
    elif entity[0].startswith("Q"):
        wd_claim = ehwbi.ExternalID(prop_nr="P1", value=entity[0], references=references)
        if 'eu' in wdjson['entities'][entity[0]]['labels']:
            eu_label = wdjson['entities'][entity[0]]['labels']['eu']['value']
        if 'en' in wdjson['entities'][entity[0]]['labels']:
            en_label = wdjson['entities'][entity[0]]['labels']['en']['value']
        if 'es' in wdjson['entities'][entity[0]]['labels']:
            es_label = wdjson['entities'][entity[0]]['labels']['es']['value']
        if 'fr' in wdjson['entities'][entity[0]]['labels']:
            fr_label = wdjson['entities'][entity[0]]['labels']['fr']['value']
    if not wd_claim:
        input(f"Problem. No 'entity' found in request result.")

    # produce wikibase item
    if not item_id:
        item = ehwbi.wbi.item.new()
    else:
        item = ehwbi.wbi.item.get(item_id)
    item.claims.add(wd_claim)
    item.claims.add(ehwbi.ExternalID(prop_nr="P6", value=page_title.replace(" ", "_"), references=references))
    item.claims.add(ehwbi.ExternalID(prop_nr="P7", value=str(page_id), references=references, qualifiers=[ehwbi.String(prop_nr="P11", value="0")]))
    item.labels.set(language="mul", value=eu_label)
    item.labels.set(language="eu", value=eu_label)
    item.labels.set(language="en", value=en_label)
    item.labels.set(language="es", value=es_label)
    item.labels.set(language="fr", value=fr_label)
    for cat_qid in pages_dict[page_title]["cats"]:
        item.claims.add(ehwbi.Item(prop_nr="P10", value=cat_qid, references=references), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
    # print(item)

    item.write()
    with open("uploaded_pages.csv", "a") as csvfile:
        csvfile.write(f"{page_id}\t{item.id}\n")
    print(f"Written data to https://ehkultura.wikibase.cloud/wiki/Item:{item.id}")
    uploaded_pages[page_id] = item.id

    time.sleep(.34)




