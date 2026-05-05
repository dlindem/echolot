import json, re, time

with open("20250113_erregistroak.json", "r") as f:
    data = json.load(f)

fields_to_look_at = [
    "100",
    "245",
    "260",
    "500",
    "520",
    "583",
    "775"
]

context = ""
birth_year = None
death_year = None
for entry in data:
    for field in entry['fields']:
        for key, value in field.items():
            if key == "100":
                for subfield in value["subfields"]:
                    for subkey, subvalue in subfield.items():
                        if subkey == "9":
                            author_id = subvalue
                        elif subkey == "d":
                            author_dates = subvalue
                birth_re = re.search(r'\((\d{4})', author_dates)
                death_re = re.search(r'\-(\d{4})\)', author_dates)
                if birth_re:
                    birth_year = birth_re.group(1)
                if death_re:
                    death_year = death_re.group(1)

            if key in fields_to_look_at:
                for subfield in value["subfields"]:
                    for subkey, subvalue in subfield.items():
                        context += subvalue.replace("\n", " ") + " "


    print(context)