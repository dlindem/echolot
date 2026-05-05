import json, time, re, csv, os, ehwbi

types = {
    "CORPO_NAME": "Q23560",
    "PERSO_NAME": "Q23559",
    "TOPIC_TERM": "Q23561"
}
done_items = {}
with open('uploaded_objects.csv', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    for row in reader:
        done_items[row[0]] = row[1]

with open('20260113_autoritateak_guztiak.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Type'] not in types:
            print(f"Skipped: type {row['Type']} not defined.")
            continue
        if row['ID'] in done_items:
            print(f"Already done in a former run: {row['ID']}\t{done_items[row['ID']]}")
            continue

        wb_item = ehwbi.wbi.item.new()
        references = [ehwbi.Item(prop_nr="P13", value="Q23557")]

        wb_item.claims.add(ehwbi.ExternalID(prop_nr="P15", value=row['ID'], references=references))
        wb_item.claims.add(ehwbi.Item(prop_nr="18", value=types[row['Type']], references=references))

        wb_item.claims.add(ehwbi.ExternalID(prop_nr="P16", value=row['Name'].strip(), references=references))
        wb_item.labels.set(language="mul", value=row['Name'].strip())

        for field in ["ext_id1", "ext_id2", "ext_id3", "ext_id4"]:
            wikidata_re = re.search(r'wikidata.org/[^/]+/(Q\d+)', row[field])
            if wikidata_re:
                wb_item.claims.add(ehwbi.ExternalID(prop_nr="P1", value=wikidata_re.group(1), references=references))
            viaf_re = re.search(r'viaf.org/viaf/(\d+)', row[field])
            if viaf_re:
                wb_item.claims.add(ehwbi.ExternalID(prop_nr="P17", value=viaf_re.group(1), references=references))

        wb_item.write()
        with open('uploaded_objects.csv', 'a') as f:
            f.write(f"{row['ID']}\t{wb_item.id}\n")
        print(f"Success with {row['ID']}: https://ehkultura.wikibase.cloud/entity/{wb_item.id}.")
        time.sleep(.34)



