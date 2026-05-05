import csv, requests, json, sys

from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.wbi_helpers import execute_sparql_query
import ehwbi, time

# get existing category relations
query = """PREFIX ehwb: <https://ehkultura.wikibase.cloud/entity/>
PREFIX ehdp: <https://ehkultura.wikibase.cloud/prop/direct/>
PREFIX ehp: <https://ehkultura.wikibase.cloud/prop/>
PREFIX ehps: <https://ehkultura.wikibase.cloud/prop/statement/>

select ?subcat ?subcatLabel ?cat ?catLabel   where
{?subcat ehdp:P5 ehwb:Q2; ehp:P9 ?cat_st. ?cat_st ehps:P9 ?cat.
 
 SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],mul,eu". }
 }"""

bindings = execute_sparql_query(query=query)['results']['bindings']
print(f"Got {len(bindings)} results from Wikibase SPARQL endpoint.")
time.sleep(.3)
existing = {}
for binding in bindings:
    subcat = binding['subcat']['value'].replace("https://ehkultura.wikibase.cloud/entity/", "")
    cat = binding['cat']['value'].replace("https://ehkultura.wikibase.cloud/entity/", "")
    if subcat not in existing:
        existing[subcat] = []
    existing[subcat].append(cat)

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
    parent_cat_qid = uploaded_categories[data["cat_page_id"]]
    if "14" not in data['content']:
        continue
    for subcat in data["content"]["14"]:
        subcat_page_id = subcat["pageid"]
        if subcat_page_id not in uploaded_categories:
            print(f"Error, not found: {subcat['title']}")
            continue
        subcat_page_qid = uploaded_categories[subcat_page_id]
        if subcat_page_qid in existing:
            if parent_cat_qid in existing[subcat_page_qid]:
                print("Already uploaded, skipping")
                continue
        print(f"{count}: Will write, parent: {parent_cat_qid}, child: {subcat_page_qid}")
        # produce wikibase item

        item = ehwbi.wbi.item.get(subcat_page_qid)
        item.claims.add(ehwbi.Item(prop_nr="P9", value=parent_cat_qid, references=references), action_if_exists=ActionIfExists.APPEND_OR_REPLACE)


        item.write()

        print(f"Written data to https://ehkultura.wikibase.cloud/wiki/Item:{item.id}")


        time.sleep(.34)




