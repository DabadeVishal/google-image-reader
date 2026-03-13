import json
from urllib.parse import urlparse, quote_plus
import requests
from bs4 import BeautifulSoup

queries = [
    "PMSM motor diagram",
    "PMSM motor diagrams",
    "PMSM diagram",
    "PMSM machine diagram",
    "PMSM electric motor diagram",
    "PMSM motor schematic",
    "PMSM motor schematic diagram",
    "PMSM motor line diagram",
    "PMSM motor sketch",
    "PMSM motor drawing",
    "PMSM motor technical drawing",
    "PMSM motor blueprint",
    "PMSM motor illustration",
    "PMSM motor labeled diagram",
    "PMSM motor labelled diagram",
    "PMSM motor construction diagram",
    "PMSM motor structure diagram",
    "PMSM motor anatomy diagram",
    "PMSM motor internal diagram",
    "PMSM motor internal structure diagram",
    "PMSM motor cross section diagram",
    "PMSM motor cross sectional view",
    "PMSM motor sectional view",
    "PMSM motor cutaway diagram",
    "PMSM motor exploded view diagram",
    "PMSM stator rotor diagram",
    "PMSM rotor stator sketch",
    "PMSM stator diagram",
    "PMSM rotor diagram",
    "PMSM winding diagram",
    "PMSM winding layout diagram",
    "PMSM phase winding diagram",
    "PMSM slot pole diagram",
    "PMSM magnetic flux diagram",
    "PMSM flux path diagram",
    "PMSM field distribution diagram",
    "PMSM electromagnetic diagram",
    "PMSM equivalent circuit diagram",
    "PMSM control block diagram",
    "PMSM drive system diagram",
    "PMSM inverter motor diagram",
    "PMSM motor controller diagram",
    "PMSM motor circuit diagram",
    "PMSM motor connection diagram",
    "PMSM motor working principle diagram",
    "PMSM operation diagram",
    "PMSM torque production diagram",
    "PMSM dq axis diagram",
    "PMSM phasor diagram",
    "PMSM vector diagram",
    "IPMSM motor diagram",
    "SPMSM motor diagram",
    "surface PMSM diagram",
    "interior PMSM diagram",
    "permanent magnet synchronous motor diagram",
    "permanent magnet synchronous motor diagrams",
    "permanent magnet synchronous machine diagram",
    "permanent magnet motor diagram",
    "permanent magnet AC motor diagram",
    "PM synchronous motor diagram",
    "PM synchronous machine diagram",
    "PM motor diagram",
    "brushless PMSM diagram",
    "brushless permanent magnet synchronous motor diagram",
    "three phase PMSM motor diagram",
    "3 phase PMSM motor diagram",
    "three phase permanent magnet synchronous motor diagram",
    "PMSM motor 2D diagram",
    "PMSM motor 3D diagram",
    "PMSM CAD diagram",
    "PMSM Simulink motor diagram",
    "PMSM model diagram",
    "PMSM finite element diagram",
    "PMSM FEA diagram",
    "PMSM academic diagram",
    "PMSM journal diagram",
    "PMSM textbook diagram",
    "PMSM educational diagram",
    "PMSM research paper diagram",
    "PMSM machine cross section",
    "permanent magnet synchronous motor cross section",
    "permanent magnet synchronous machine cross section diagram",
    "PMSM motor topology diagram",
    "PMSM motor architecture diagram",
    "PMSM motor assembly diagram",
    "PMSM motor parts diagram",
    "PMSM motor component diagram",
    "PMSM magnet placement diagram",
    "PMSM rotor magnet diagram",
    "PMSM stator slot diagram",
    "PMSM slot winding diagram",
    "PMSM concentrated winding diagram",
    "PMSM distributed winding diagram",
    "PMSM machine structure sketch",
    "PMSM engineering sketch",
    "PMSM engineering schematic",
    "PMSM detailed diagram",
    "PMSM simplified diagram",
    "PMSM overview diagram",
    "PMSM annotated diagram",
    "PMSM high resolution diagram",
    "PMSM clear diagram",
    "PMSM black and white diagram",
    "PMSM vector schematic",
]
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})

seen_images = set()
seen_pages = set()

preferred_domains = [
    "mathworks.com",
    "mdpi.com",
]

sketch_keywords = [
    "diagram",
    "schematic",
    "cross section",
    "cross sectional",
    "sectional view",
    "structure",
    "stator",
    "rotor",
    "winding",
    "working principle",
    "topology",
]

def get_domain(url):
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def domain_score(domain):
    score = 0
    for d in preferred_domains:
        if d in domain:
            score += 20
    return score

def text_score(text, query):
    text = (text or "").lower()
    query = (query or "").lower()
    score = 0

    good_words = [
        "pmsm",
        "permanent magnet synchronous motor",
        "permanent magnet synchronous machine",
        "diagram",
        "schematic",
        "cross section",
        "cross sectional",
        "sectional view",
        "structure",
        "stator",
        "rotor",
        "winding",
        "working principle",
        "topology",
    ]

    for word in good_words:
        if word in text:
            score += 4

    if "mathworks" in text:
        score += 8
    if "mdpi" in text:
        score += 8

    if query in text:
        score += 5

    return score

def search_bing_images(query, limit=5):
    url = "https://www.bing.com/images/search"
    params = {"q": query, "form": "HDRSC2"}

    r = session.get(url, params=params, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    candidates = []

    for a in soup.select("a.iusc"):
        m = a.get("m")
        if not m:
            continue

        try:
            meta = json.loads(m)
            image_url = meta.get("murl")
            page_url = meta.get("purl")
            title = a.get("aria-label") or meta.get("t") or query

            if not image_url or not page_url:
                continue
            if image_url in seen_images or page_url in seen_pages:
                continue

            domain = get_domain(page_url)
            if not any(d in domain for d in preferred_domains):
                continue

            score = 0
            score += domain_score(domain)
            score += text_score(title, query)
            score += text_score(page_url, query)

            title_l = (title or "").lower()
            page_l = (page_url or "").lower()
            if any(k in title_l or k in page_l for k in sketch_keywords):
                score += 10

            candidates.append({
                "title": title,
                "image": image_url,
                "page": page_url,
                "domain": domain,
                "score": score,
            })

        except Exception:
            continue

    candidates.sort(key=lambda x: x["score"], reverse=True)

    results = []
    for item in candidates:
        if item["image"] in seen_images or item["page"] in seen_pages:
            continue

        seen_images.add(item["image"])
        seen_pages.add(item["page"])
        results.append(item)

        if len(results) >= limit:
            break

    return results

all_results = []

for q in queries:
    print(f"\nQuery: {q}")
    print("=" * 100)

    try:
        results = search_bing_images(q, limit=3)
    except Exception as e:
        print("Search failed:", e)
        continue

    if not results:
        print("No results found")
        continue

    for i, item in enumerate(results, 1):
        print(f"{i}. Title : {item['title']}")
        print(f"   Domain: {item['domain']}")
        print(f"   Score : {item['score']}")
        print(f"   Image : {item['image']}")
        print(f"   Page  : {item['page']}")
        print("-" * 100)
        all_results.append(item)

print("\nTop exact image links only:")
print("=" * 100)
for item in all_results:
    print(item["image"])

print("\nTop page links only:")
print("=" * 100)
for item in all_results:
    print(item["page"])

print("\nDirect Bing search links for manual check:")
print("=" * 100)
for q in queries:
    print("https://www.bing.com/images/search?q=" + quote_plus(q))
