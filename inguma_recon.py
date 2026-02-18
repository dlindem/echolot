import time

from wikidata_query import wikidata_query
import json, csv, time

with open('inguma_recon/gold_standard.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    counter = 0
    for row in reader:
        counter += 1
        print(f"{counter}")
        querystring = f"{row['authorname']} - gender: {row['gender']}: {row['affs'][:30]}: {row['year']}: {row['argitalpenak'][:100]}"
        print(querystring)
        results = wikidata_query(querystring=querystring)
        count = 0
        if results:
            print(f"Got {len(results)} results for {row['authorname']}")

            for result in results:
                count += 1
                if result['QID'] == row['wikidata']:
                    print(f"Found {row['authorname']} as result No. {count}!")
                    break

        else:
            print(f"No results for {row['authorname']}")

        resultline = {'person': row['author'], 'name': row['authorname'], 'found as result': count, 'result': results}
        with open('inguma_recon/gold_standard_results_reranked.jsonl', 'a') as outfile:
            outfile.write(f"{json.dumps(resultline)}\n")
        time.sleep(1)