import json, time
from SPARQLWrapper import SPARQLWrapper, JSON

def get_matches(point):
    sparql = SPARQLWrapper(
        "https://qlever.dev/api/wikidata"
    )
    sparql.setReturnFormat(JSON)

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX geof: <http://www.opengis.net/def/function/geosparql/>
    PREFIX schema: <http://schema.org/>
    PREFIX wd: <http://www.wikidata.org/entity/>
    SELECT ?item ?name_eu ?name_es ?description_eu ?description_es ?dist ?location (GROUP_CONCAT(DISTINCT ?class; SEPARATOR="; ") AS ?classes) (GROUP_CONCAT(DISTINCT ?reg) AS ?registers) WHERE {
      {
        ?item wdt:P31/wdt:P279* wd:Q358.
      } # heritage sites
      UNION {
        ?item wdt:P31/wdt:P279* wd:Q839954.
      } # archaeological sites
      UNION {
        ?item wdt:P1435 [ rdfs:label ?reg ] . FILTER (LANG(?reg) = "eu")
      } # items in heritage registers
      ?item wdt:P625 ?location .
      ?item wdt:P31 [rdfs:label ?class]. filter(lang(?class)="eu")
      OPTIONAL {
        ?item rdfs:label ?name_eu .
        FILTER (LANG(?name_eu) = "eu") .
      }
      OPTIONAL {
        ?item schema:description ?description_eu .
        FILTER (LANG(?description_eu) = "eu") .
      }
      OPTIONAL {
        ?item rdfs:label ?name_es .
        FILTER (LANG(?name_es) = "es") .
      }
      OPTIONAL {
        ?item schema:description ?description_es .
        FILTER (LANG(?description_es) = "es") .
      }
      """
    query += f' BIND ("{point}"^^geo:wktLiteral AS ?point)'
    query += """ BIND (geof:distance(?location, ?point) AS ?dist)
      FILTER (?dist  <= 10)
    } group by ?item ?name_eu ?name_es ?description_eu ?description_es ?dist ?location ?classes ?registers
    ORDER BY ASC(?dist) LIMIT 10
        """
    # print(query)
    sparql.setQuery(query)
    done = False
    while not done:
        try:
            ret = sparql.queryAndConvert()["results"]["bindings"]
            print(f"Got {len(ret)} matches.")
            time.sleep(.51)
            return ret

        except Exception as e:
            print(e)
            time.sleep(5)

with open('sig_objects_wikibase.json') as f:
    sig_objects = json.load(f)

pointcount = 0
for sig_object in sig_objects:
    pointcount += 1
    csvlines = []
    point = sig_object['geo']
    print(f"{pointcount} of {len(sig_objects)}: {point}... ", end="")
    matches = get_matches(point)
    matchcount = 0
    for match in matches:
        if matchcount == 5:
            break
        matchcount += 1
        csvlines.append("\t".join([
            sig_object['item'],
            sig_object['eu_label'],
            sig_object['es_label'],
            str(matchcount),
            match['dist']['value'],
            match['item']['value'],
            match['name_eu']['value'] if 'name_eu' in match else '',
            match['description_eu']['value'] if 'description_eu' in match else '',
            match['name_es']['value'] if 'name_es' in match else '',
            match['description_es']['value'] if 'description_es' in match else '',
            match['classes']['value'] if 'classes' in match else '',
            match['registers']['value'] if 'registers' in match else ''
        ]))
    with open('points_matches.csv', 'a') as of:
        of.write("\n".join(csvlines)+"\n")

