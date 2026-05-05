from pymarc import MARCReader
import json

with open('20250113_erregistroak.mrc', 'rb') as f:
    reader = MARCReader(f)
    mrc_json = []
    for record in reader:
        mrc_json.append(json.loads(record.as_json()))

with open('20250113_erregistroak.json', 'w') as f:
    json.dump(mrc_json, f, indent=2)