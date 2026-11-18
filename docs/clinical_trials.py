import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


API_URL = "https://clinicaltrials.gov/api/v2/studies"


def search_clinical_trials(search_value):
    search_value = search_value.strip()

    if not search_value:
        return []

    params = {
        "query.term": search_value,
        "format": "json",
        "pageSize": 10
    }

    url = API_URL + "?" + urlencode(params)

    request = Request(
        url,
        headers={"User-Agent": "PharmaReferenceFinder/1.0"}
    )

    try:
        with urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))

        results = []

        for study in data.get("studies", []):
            protocol = study.get("protocolSection", {})
            identification = protocol.get(
                "identificationModule", {}
            )

            nct_id = identification.get("nctId")
            title = identification.get("briefTitle", "")

            if nct_id:
                results.append({
                    "trial_id": nct_id,
                    "title": title,
                    "url": f"https://clinicaltrials.gov/study/{nct_id}",
                    "source": "ClinicalTrials.gov"
                })

        return results

    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        print("ClinicalTrials.gov API error:", error)
        return []
