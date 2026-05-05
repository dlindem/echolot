import requests, time, json

def get_cat(cmtitle=None):
    cmcontinue = "0"
    complete = False
    result = []
    while not complete:


        base_url = "https://eu.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "cmtitle": cmtitle.replace(" ", "_"),
            "list": "categorymembers",
            "format": "json",
            "cmlimit": 100,
            "cmcontinue": cmcontinue,
        }

        headers = {"User-Agent": "User:DL2204 python script"}

        r = requests.get(url=base_url, params=params, headers=headers)

        data = r.json()
        result += data['query']['categorymembers']
        if "continue" in data:
            cmcontinue = data['continue']['cmcontinue']
        else:
            complete = True
        print(f"Getting categories for {cmtitle}; cmcontinue: {cmcontinue}")
        time.sleep(1)
    return result

with open("forbidden_categories.jsonl") as f:
    forbidden_kat = []
    for line in f.readlines():
        linejson = json.loads(line)
        forbidden_kat.append(linejson["cat_page_id"])
with open("categories.jsonl") as f:
    seen_kat = []
    for line in f.readlines():
        linejson = json.loads(line)
        seen_kat.append(str(linejson["cat_page_id"]))
with open("unseen_kat.json") as f:
    unseen_kat = json.load(f)
if len(unseen_kat) == 0:
    unseen_kat = {"root": "Kategoria:Euskal Herriko kultura"}

count = 0
while len(unseen_kat) > 0:
    count += 1
    print(f"{count} ({len(unseen_kat)} left)", end=": ")
    kat = next(iter(unseen_kat.items()))
    if kat[0] in seen_kat:
        continue
    kat_content = get_cat(cmtitle=kat[1])
    # print(kat_content)

    unseen_kat.pop(kat[0])
    content = {}
    for page in kat_content:
        if str(page["ns"]) not in content:
            content[str(page["ns"])] = []
        content[str(page["ns"])].append({"pageid": page["pageid"], "title": page["title"]})
        if page["ns"] == 14 and page["pageid"] not in forbidden_kat and not page['title'].startswith("Kategoria:Txikipedia"):
            unseen_kat[page["pageid"]] = page["title"]
        if str(page['pageid']) in seen_kat:
            continue
        if "0" in content:
            page_amount = len(content["0"])
        else:
            page_amount = 0
        if "14" in content:
            subcat_amount = len(content["14"])
        else:
            subcat_amount = 0
        with open("categories.jsonl", "a") as f:
            f.write(json.dumps({"cat_page_id": kat[0], "cat_page": kat[1], "pages": page_amount, "subcat": subcat_amount, "content": content})+"\n")
        seen_kat.append(kat[0])
        with open("unseen_kat.json", "w") as f:
            json.dump(unseen_kat, f, indent=2)



