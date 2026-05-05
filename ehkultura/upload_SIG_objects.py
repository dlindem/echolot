import csv, time, ehwbi

with open('SIG_Araba/uploaded_objects.csv', 'r') as f:
    reader = csv.reader(f, delimiter='\t')
    done_items = {}
    for row in reader:
        done_items[row[0]] = row[1]

with open('SIG_Araba/Site_ID_table.csv', 'r') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        objectid = row['objectid']
        if objectid in done_items:
            print(f"Already done in a former run: {objectid}\t{done_items[objectid]}")
            continue

        wb_item = ehwbi.wbi.item.new()

        if row['nombre'] != '':
            wb_item.labels.set(language="es", value=row["nombre"].strip())
        if row['izena'] != '':
            wb_item.labels.set(language="eu", value=row["izena"].strip())

        reference = ehwbi.Item(prop_nr="P13", value="Q12879")
        claim = ehwbi.String(prop_nr="P14", value=objectid, references=[reference])
        wb_item.claims.add(claim)

        lat = float(row['latitude'].replace(',', '.'))
        long = float(row['longitude'].replace(',', '.'))
        claim = ehwbi.GlobeCoordinate(prop_nr="P12", latitude=lat, longitude=long, references=[reference])
        wb_item.claims.add(claim)

        wb_item.write()
        with open('SIG_Araba/uploaded_objects.csv', 'a') as f:
            f.write(f"{row['objectid']}\t{wb_item.id}\n")
        print(f"Success with {objectid}: {wb_item.id}.")
        time.sleep(.34)
