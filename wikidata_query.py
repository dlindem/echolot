from urllib import request, parse
import json

def wikidata_query(querystring="", instanceof="Q5"):
    # Base URL
    base_url = "https://wd-vectordb.wmcloud.org/item/query/"

    # Parameters
    params = {
        "query": querystring,
        "lang": "all",
        "K": 50,
        "instanceof": instanceof,
        "rerank": "true",
        "return_vectors": "false"
    }

    # Headers
    headers = {
        "accept": "application/json",
        "X-API-SECRET": "1234",
        "User-Agent": "david.lindemann@ehu.eus python urllib"
    }

    # Encode parameters and build URL
    encoded_params = parse.urlencode(params)
    url = f"{base_url}?{encoded_params}"

    # Create request
    req = request.Request(url, headers=headers, method="GET")

    try:
        # Send request
        with request.urlopen(req) as response:
            # Read and decode response
            response_data = response.read().decode('utf-8')

            # Parse JSON response
            result = json.loads(response_data)

            # Print results
            print(f"Status Code: {response.status}")
            print(f"Response Headers: {dict(response.headers)}")
            # print(f"Response: {json.dumps(result, indent=2)}")
            return result

    except Exception as e:
        print(f"Error: {e}")