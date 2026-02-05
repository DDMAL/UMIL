from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import requests
import time
import pandas as pd

CATALOGUE_API = "https://vocabulary.mimo-international.com/rest/v1/InstrumentsKeywords/data"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

LANGUAGE_NAMES = {
    "en": "English",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "pl": "Polish",
    "nl": "Dutch",
    "sv": "Swedish",
    "ca": "Catalan",
    "ko": "Korean",
    "zh": "Chinese",
    "eu": "Basque",
    "dk": "Danish",
}

# -------------------------
# PLAYWRIGHT SIDEBAR
# -------------------------

def expand_all_nodes(page):
    while True:
        collapsed = page.query_selector_all("#sidebar li.jstree-closed > .jstree-ocl")
        if not collapsed:
            break
        for toggle in collapsed:
            try:
                toggle.click()
                page.wait_for_timeout(100)
            except Exception:
                pass

def get_instrument_ids_and_urls(page):
    sidebar = page.query_selector("#sidebar")
    links = sidebar.query_selector_all("a.jstree-anchor")

    instruments = []
    for link in links:
        href = link.get_attribute("href")
        if not href or "/page/" not in href:
            continue

        instrument_id = href.split("/page/")[-1].strip("/")
        label = link.inner_text().strip()

        instruments.append({
            "id": instrument_id,
            "name": label,
            "url": urljoin("https://vocabulary.mimo-international.com", href)
        })

    return instruments

# -------------------------
# JSON-LD HELPERS
# -------------------------

def normalize_lang_values(value):
    if isinstance(value, str):
        return {"": value}
    if isinstance(value, list):
        return {
            item.get("lang", ""): item.get("value", "")
            for item in value if isinstance(item, dict)
        }
    if isinstance(value, dict):
        return {value.get("lang", ""): value.get("value", "")}
    return {}

def extract_umil_mappings(node):
    umil_uris = []

    for key in ("skos:exactMatch", "skos:closeMatch", "owl:sameAs"):
        val = node.get(key)
        if isinstance(val, dict):
            uri = val.get("uri", "")
            if "umil.linkedmusic.ca" in uri:
                umil_uris.append(uri)
        elif isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    uri = item.get("uri", "")
                    if "umil.linkedmusic.ca" in uri:
                        umil_uris.append(uri)

    return umil_uris

# -------------------------
# FETCH MIMO DATA
# -------------------------

def fetch_mimo_data(instrument_id):
    params = {
        "uri": f"http://www.mimo-db.eu/InstrumentsKeywords/{instrument_id}",
        "format": "application/ld+json"
    }

    try:
        r = requests.get(CATALOGUE_API, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        pref = {}
        alt = {}
        editorial = {}
        umil_uris = []

        for node in data.get("graph", []):
            if node.get("type") == "skos:Concept":
                pref = normalize_lang_values(node.get("prefLabel"))
                alt = normalize_lang_values(node.get("altLabel"))
                editorial = normalize_lang_values(
                    node.get("editorialNote") or node.get("skos:editorialNote")
                )
                umil_uris = extract_umil_mappings(node)

        return pref, alt, editorial, umil_uris

    except Exception as e:
        print(f"Error fetching {instrument_id}: {e}")
        return {}, {}, {}, []

# -------------------------
# WIKIDATA CHECK
# -------------------------

def check_wikidata_match(english_label):
    params = {
        "action": "wbsearchentities",
        "search": english_label,
        "language": "en",
        "format": "json",
        "limit": 5
    }

    try:
        r = requests.get(WIKIDATA_API, params=params, timeout=10)
        r.raise_for_status()
        for item in r.json().get("search", []):
            if item.get("label", "").lower() == english_label.lower():
                return "Yes"
    except Exception:
        pass

    return "No"

# -------------------------
# FORMATTING
# -------------------------

def format_lang_block(data):
    lines = []
    for lang, val in data.items():
        if not val:
            continue
        lang_name = LANGUAGE_NAMES.get(lang, lang if lang else "General")
        lines.append(f"{lang_name}: {val}")
    return "\n".join(lines)

# -------------------------
# EXCEL
# -------------------------

def save_to_excel(instruments, filename="mimo_instruments_umil_wikidata.xlsx"):
    rows = []

    for inst in instruments:
        pref = inst["pref"]
        alt = inst["alt"]
        editorial = inst["editorial"]
        umil_uris = inst["umil_uris"]

        english = pref.get("en", inst["name"])

        rows.append({
            "Instrument URL": inst["url"],
            "English": english,
            "Other Languages": format_lang_block({k: v for k, v in pref.items() if k != "en"}),
            "Alternative Labels": format_lang_block(alt),
            "Editorial Notes": format_lang_block(editorial),
            "UMIL Mapping Present": "Yes" if umil_uris else "No",
            "UMIL URI(s)": "\n".join(umil_uris),
            "Wikidata Match": check_wikidata_match(english)
        })

    df = pd.DataFrame(rows)

    with pd.ExcelWriter(filename, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Instruments")
        worksheet = writer.sheets["Instruments"]
        workbook = writer.book

        wrap = workbook.add_format({"text_wrap": True})
        link = workbook.add_format({"font_color": "blue", "underline": 1})

        worksheet.set_column(0, 0, 55)
        worksheet.set_column(2, 6, 45, wrap)

        for r, url in enumerate(df["Instrument URL"], start=1):
            worksheet.write_url(r, 0, url, link)

    print(f"Saved {len(df)} instruments → {filename}")

# -------------------------
# MAIN
# -------------------------

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://vocabulary.mimo-international.com/InstrumentsKeywords/en/")

        input("Click the Hierarchy tab, then press Enter...")
        expand_all_nodes(page)

        instruments = get_instrument_ids_and_urls(page)
        print(f"Collected {len(instruments)} instruments")

    for i, inst in enumerate(instruments, 1):
        print(f"[{i}/{len(instruments)}] {inst['id']}")
        inst["pref"], inst["alt"], inst["editorial"], inst["umil_uris"] = fetch_mimo_data(inst["id"])
        time.sleep(0.02)

    save_to_excel(instruments)

if __name__ == "__main__":
    main()
