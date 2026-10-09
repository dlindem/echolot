import csv, re, ehwbi, sys, json, time

with open('arkeoikuska/done_uploads.txt') as file:
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

        wb_item = ehwbi.wbi.item.new()
        wb_item.claims.add(ehwbi.ExternalID(prop_nr="P41", value=pdf_name))
        wb_item.claims.add(ehwbi.String(prop_nr="P42", value=row['ARKEOIKUSKA_ZBK'].strip()))

        label_eu = re.sub(r' +', ' ',re.sub(r'[\t\n]', ' ', row['PBLTITULOEU'][:599].strip()))
        wb_item.labels.set(language="eu", value=label_eu)
        label_es = re.sub(r' +', ' ',re.sub(r'[\t\n]', ' ', row['PBLTITULOES'][:599].strip()))
        wb_item.labels.set(language="es", value=label_es)
        print(f"Labels are: {label_eu} // {label_es}")

        qualifiers = []
        place_literal_eu_re = re.search(r'^([^\(]+) \(([^\)]+)\)', label_eu)
        if place_literal_eu_re:
            izen_hutsa = place_literal_eu_re.group(1).strip()
            toki_hutsa = place_literal_eu_re.group(2).strip()
            print(f"Extracted EU: {izen_hutsa} >> tokia >> {toki_hutsa}")
            qualifiers.append(ehwbi.MonolingualText(language="eu", text=izen_hutsa, prop_nr="P40"))
            qualifiers.append(ehwbi.MonolingualText(language="eu", text=toki_hutsa, prop_nr="P39"))
        wb_item.claims.add(ehwbi.MonolingualText(prop_nr="P51", language="eu", text=label_eu, qualifiers=qualifiers), action_if_exists=ehwbi.ActionIfExists.APPEND_OR_REPLACE)

        qualifiers = []
        place_literal_es_re = re.search(r'^([^\(]+) \(([^\)]+)\)', label_es)
        if place_literal_es_re:
            izen_hutsa = place_literal_es_re.group(1).strip()
            toki_hutsa = place_literal_es_re.group(2).strip()
            print(f"Extracted ES: {izen_hutsa} >> tokia >> {toki_hutsa}")
            qualifiers.append(ehwbi.MonolingualText(language="es", text=izen_hutsa, prop_nr="P40"))
            qualifiers.append(ehwbi.MonolingualText(language="es", text=toki_hutsa, prop_nr="P39"))
        wb_item.claims.add(ehwbi.MonolingualText(prop_nr="P51", language="es", text=label_es, qualifiers=qualifiers), action_if_exists=ehwbi.ActionIfExists.APPEND_OR_REPLACE)

        jarduera_raw = row['ACTIVIDADES_EU'].strip()
        jarduerak = re.sub(r'\.', '|', jarduera_raw).split('|')
        for jard in jarduerak:
            if len(jard) > 0:
                jarduera = jarduera_map[jard.strip()]
                wb_item.claims.add(ehwbi.Item(prop_nr="P43", value=jarduera), action_if_exists=ehwbi.ActionIfExists.APPEND_OR_REPLACE)

        zuzendaria = row['DIRECTOR'].strip()
        if len(zuzendaria) > 0:
            wb_item.claims.add(ehwbi.String(prop_nr="P44", value=zuzendaria))

        pub_year = row['PBLANO'].strip()
        wb_item.claims.add(ehwbi.Time(prop_nr="P26", time=f"+{pub_year}-01-01T00:00:00Z", precision=9))

        zona = row['ZONA_EU'].strip()
        if len(zona) > 0:
            wb_item.claims.add(ehwbi.MonolingualText(language="eu", text=zona, prop_nr="P45"))

        try:
            qualifiers = []
            lurraldea = "{:02d}".format(int(row['TERRITORIO_COD'].strip()))
            qualifiers.append(ehwbi.String(prop_nr="P33", value=lurraldea))
            herria = "{:03d}".format(int(row['MUNICIPIO_COD'].strip()))
            qualifiers.append(ehwbi.String(prop_nr="P34", value=herria))
            herri_code = lurraldea + herria
            herri_item = herriak_map[herri_code]
            print(f"Herria: {herri_code} >> {herri_item}")
            wb_item.claims.add(ehwbi.Item(prop_nr="P46", value=herri_item, qualifiers=qualifiers))
        except:
            pass

        wb_item.claims.add(ehwbi.String(prop_nr="P47", value=row['DOID'].strip()))
        wb_item.claims.add(ehwbi.String(prop_nr="P48", value=row['PBLFUECOD'].strip()))
        wb_item.claims.add(ehwbi.String(prop_nr="P49", value=row['DOELEMID'].strip()))
        wb_item.claims.add(ehwbi.String(prop_nr="P50", value=row['DOTAMANO'].strip()))

        # print(json.dumps(wb_item.get_json(), indent=2))
        wb_item.write()
        with open('arkeoikuska/done_uploads.txt', 'a') as file:
            file.write(f"{pdf_name}\n")
        print(f"Success writing to https://ehkultura.wikibase.cloud/entity/{wb_item.id}")
        time.sleep(.34)









