import csv, re, ehwbi, sys, json, time

wikibase_map = {}
with open('arkeoikuska/wikibase_map.csv') as file:
    reader = csv.DictReader(file, delimiter="\t")
    for row in reader:
        wikibase_map[row['pdf']] = row['item']
    print(f"Wikibase items: {len(wikibase_map)}")

with open('arkeoikuska/done_uploads_round_2.txt') as file:
    done_items = file.read().split("\n")
    print(f"done items: {len(done_items)}: {done_items}")
    input("Press any key to continue...")

with open('arkeoikuska/arkeoikuska_metadata.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter="\t")
    count = 0
    for row in reader:
        count += 1
        print(f"\n{count}: {row}")
        pdf_name = row['DONOMBRE'].strip()
        if pdf_name in done_items:
            print(f"Item already done: {pdf_name}")
            continue
        wb_id = wikibase_map[pdf_name]

        wb_item = ehwbi.wbi.item.get(entity_id=wb_id)
        wb_item.claims.add(ehwbi.Item(prop_nr="P5", value="Q183597"))

        qualifiers = []
        page_re = re.search(r' ([\d\-]+) ', row['PBLFUEPREES'])
        if page_re:
            qualifiers.append(ehwbi.String(prop_nr="P52", value=page_re.group(1)))
        wb_item.claims.add(ehwbi.String(prop_nr="P42", value=row['ARKEOIKUSKA_ZBK'].strip(), qualifiers=qualifiers), action_if_exists=ehwbi.ActionIfExists.REPLACE_ALL)

        pub_year = row['PBLANO'].strip()
        wb_item.descriptions.set(language="eu", value=f"{pub_year}ko Arkeoikuska txostena")
        wb_item.descriptions.set(language="es", value=f"Artículo en Arkeoikuska, año {pub_year}")

        try:
            wb_item.write()
        except Exception as e:
            if "using the same description text" in str(e):
                wb_item.descriptions.set(language="eu", value=f"{pub_year}ko Arkeoikuska txostena (2)")
                wb_item.descriptions.set(language="es", value=f"Artículo en Arkeoikuska, año {pub_year} (2)")
                try:
                    wb_item.write()
                except Exception as e:
                    if "using the same description text" in str(e):
                        wb_item.descriptions.set(language="eu", value=f"{pub_year}ko Arkeoikuska txostena (3)")
                        wb_item.descriptions.set(language="es", value=f"Artículo en Arkeoikuska, año {pub_year} (3)")
                        wb_item.write()

        with open('arkeoikuska/done_uploads_round_2.txt', 'a') as file:
            file.write(f"{pdf_name}\n")
        print(f"Success writing to https://ehkultura.wikibase.cloud/entity/{wb_item.id}")
        time.sleep(.34)









