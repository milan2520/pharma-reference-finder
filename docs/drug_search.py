import requests

def search_drugs(search_value):
    url = "https://api.fda.gov/drug/label.json"

    params = {
        "search": search_value,
        "limit": 10
    }

    try:
        response = requests.get(url, params=params, timeout=20)

        if response.status_code == 200:
            data = response.json()
            return data.get("results", [])

        return []

    except requests.RequestException as e:
        print("Drug search error:", e)
        return []
