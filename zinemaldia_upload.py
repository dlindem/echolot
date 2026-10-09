import json, csv, time, re, sys, ehwbi

from wikibaseintegrator.wbi_enums import ActionIfExists

with open('zinemaldia/herrialdeak-vlookup.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    herrialdeak = {}
    for row in reader:
        herrialdeak[row['izena']] = row['Wikibase']
unknown_herrialdeak = {}

with open('zinemaldia/zinemaldia_aldiak.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    aldiak = {}
    for row in reader:
        aldiak[row['year']] = row['item']

with open('zinemaldia/zinemaldia-openrefine-wikidata.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='\t')
    count = 0
    for row in reader:
        unknown_herrialde = None
        count += 1
        if count < 7009:
            continue
        print(f"[{count}] {row}")
        if row['Wikibase'].startswith('Q'):
            wb_item = ehwbi.wbi.item.get(entity_id=row['Wikibase'])
        else:
            wb_item = ehwbi.wbi.item.new()
        wb_item.claims.add(ehwbi.Item(prop_nr="P5", value="Q163123"))
        description = "pelikula, zuz. "
        description_en = "film by "
        for key, value in row.items():
            if value == '' or not value:
                continue
            if key == "Izenburua":
                wb_item.claims.add(ehwbi.String(prop_nr="P25", value=value))
            elif key == "Izenburua2":
                wb_item.labels.set(language="mul", value=value)
            elif key == "Wikidata":
                if value.startswith("Q"):
                    wb_item.claims.add(ehwbi.ExternalID(prop_nr="P1", value=value))
            elif key == "Edizioa":
                saila = row['Saila'].strip()
                if saila != "":
                    qualifiers = [ehwbi.String(prop_nr="P28", value=saila)]
                else:
                    qualifiers = []
                edizioa = aldiak[value]
                wb_item.claims.add(ehwbi.Item(prop_nr="P3", value=edizioa, qualifiers=qualifiers))
            elif key == "Urtea":
                if not re.search(r'^\d{4}$', value):
                    continue
                wb_item.claims.add(ehwbi.Time(prop_nr="P26", time=f"+{value}-01-01T00:00:00Z", precision=9))
                description = f"{value}ko " + description
                description_en = f"{value} " + description_en
            elif key == "Herrialdea":
                for herrialde in value.split(','):
                    if herrialde.strip() in herrialdeak:
                        wb_item.claims.add(ehwbi.Item(prop_nr="P29", value=herrialdeak[herrialde.strip()]), action_if_exists=ActionIfExists.MERGE_REFS_OR_APPEND)
                    else:
                        print(f"Unknown herrialde: {herrialde}")
                        unknown_herrialde = herrialde.strip()
            elif key.startswith("Zuzendaria"):
                wb_item.claims.add(ehwbi.String(prop_nr="P27", value=value.strip()), action_if_exists=ActionIfExists.MERGE_REFS_OR_APPEND)
                if len(description) < 200:
                    description += f"{value.strip()}, "
                if len(description_en) < 200:
                    description_en += f"{value.strip()}, "
        description = re.sub(r' zuz\. $', '', description)
        description_en = re.sub(r' by $', '', description_en)
        description = re.sub(r', $', '', description)
        description_en = re.sub(r', $', '', description_en)
        wb_item.descriptions.set(language="eu", value=description)
        wb_item.descriptions.set(language="en", value=description_en)
        wb_item.write()
        print(f"Success with https://ehkultura.wikibase.cloud/entity/{wb_item.id}")
        if unknown_herrialde:
            if unknown_herrialde not in unknown_herrialdeak:
                unknown_herrialdeak[unknown_herrialde] = [wb_item.id]
            else:
                unknown_herrialdeak[unknown_herrialde].append(row)
        time.sleep(.34)

with open('zinemaldia/unknown_herrialdeak.json', 'w') as outfile:
    json.dump(unknown_herrialdeak, outfile, indent=2)


