# views.py
from django.http import JsonResponse
from django.views import View
import requests
from django.conf import settings

SOLR_SUGGEST_URL = f"{settings.SOLR_URL}/suggest"


class SolrSuggest(View):
    """
    Returns suggestions from Solr suggester directly.
    """

    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return JsonResponse({"suggestions": []})
        solr_query = f"{query}*"

        # Hit Solr suggest endpoint
        try:
            response = requests.get(
                SOLR_SUGGEST_URL, params={"q": solr_query, "wt": "json"}
            )
            response.raise_for_status()
        except requests.RequestException:
            return JsonResponse({"suggestions": []}, status=500)

        data = response.json()
        suggestions = []

        # Extract terms from Solr response and limit to top 5
        try:
            suggest_data = data.get("suggest", {}).get("default", {})
            if suggest_data:
                first_key = list(suggest_data.keys())[0]
                entries = suggest_data[first_key].get("suggestions", [])
                suggestions = [e["term"] for e in entries][:5]
        except Exception:
            suggestions = []

        return JsonResponse({"suggestions": suggestions})
