import json

with open('UEU/2026_maiatzean_Wikidatan_ez_dauden_58.json', 'r') as f:
    content = json.load(f)

with open('UEU/2026_may_58_not_on_Wikidata.json', 'w') as f:
    json.dump(content, f, indent=2)