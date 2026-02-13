"""
Pyzotero voorbeelden — laat de belangrijkste functionaliteit zien.

Gebruik:
  1. Kopieer .env.example naar .env en vul je Zotero-gegevens in
  2. pip install -r requirements.txt
  3. python examples.py
"""

import os
import sys

from dotenv import load_dotenv
from pyzotero import zotero

load_dotenv()

LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID")
API_KEY = os.getenv("ZOTERO_API_KEY")
LIBRARY_TYPE = os.getenv("ZOTERO_LIBRARY_TYPE", "user")


def get_client() -> zotero.Zotero:
    if not LIBRARY_ID or not API_KEY:
        sys.exit("Vul ZOTERO_LIBRARY_ID en ZOTERO_API_KEY in je .env bestand")
    return zotero.Zotero(LIBRARY_ID, LIBRARY_TYPE, API_KEY)


# ---------------------------------------------------------------------------
# 1. Items ophalen
# ---------------------------------------------------------------------------
def voorbeeld_items_ophalen():
    """Haal de laatste 5 items op en toon titel + type."""
    zot = get_client()
    items = zot.top(limit=5)
    print("=== Laatste 5 items ===")
    for item in items:
        data = item["data"]
        print(f"  [{data['itemType']}] {data.get('title', '(geen titel)')}")
    return items


# ---------------------------------------------------------------------------
# 2. Collecties bekijken
# ---------------------------------------------------------------------------
def voorbeeld_collecties():
    """Toon alle top-level collecties."""
    zot = get_client()
    collections = zot.collections_top()
    print("\n=== Collecties ===")
    for col in collections:
        data = col["data"]
        print(f"  {data['name']}  (key={data['key']}, items={data['numItems']})")
    return collections


# ---------------------------------------------------------------------------
# 3. Zoeken
# ---------------------------------------------------------------------------
def voorbeeld_zoeken(zoekterm: str = "medicine"):
    """Zoek items op titel/auteur."""
    zot = get_client()
    zot.add_parameters(q=zoekterm, qmode="titleCreatorYear")
    results = zot.top(limit=10)
    print(f"\n=== Zoekresultaten voor '{zoekterm}' ===")
    for item in results:
        data = item["data"]
        print(f"  {data.get('title', '(geen titel)')}")
    return results


# ---------------------------------------------------------------------------
# 4. Item aanmaken
# ---------------------------------------------------------------------------
def voorbeeld_item_aanmaken():
    """Maak een nieuw boek-item aan in je bibliotheek."""
    zot = get_client()
    template = zot.item_template("book")
    template["title"] = "Voorbeeld Boek via Pyzotero"
    template["creators"] = [
        {"creatorType": "author", "firstName": "Jan", "lastName": "Jansen"}
    ]
    template["date"] = "2025"
    template["abstractNote"] = (
        "Dit item is aangemaakt via het pyzotero voorbeeld-script."
    )

    resp = zot.create_items([template])
    if resp["success"]:
        key = resp["success"]["0"]
        print(f"\n=== Item aangemaakt (key={key}) ===")
        return key
    else:
        print(f"\n=== Aanmaken mislukt: {resp['failed']} ===")
        return None


# ---------------------------------------------------------------------------
# 5. Tags beheren
# ---------------------------------------------------------------------------
def voorbeeld_tags():
    """Toon de 10 meest gebruikte tags."""
    zot = get_client()
    tags = zot.tags(limit=10)
    print("\n=== Tags ===")
    for tag in tags:
        print(f"  - {tag['tag']}")
    return tags


# ---------------------------------------------------------------------------
# 6. Items in een collectie
# ---------------------------------------------------------------------------
def voorbeeld_collectie_items(collection_key: str | None = None):
    """Toon items uit de eerste beschikbare collectie."""
    zot = get_client()
    if not collection_key:
        cols = zot.collections_top(limit=1)
        if not cols:
            print("\n=== Geen collecties gevonden ===")
            return []
        collection_key = cols[0]["data"]["key"]

    items = zot.collection_items(collection_key, limit=5)
    col_name = zot.collection(collection_key)["data"]["name"]
    print(f"\n=== Items in collectie '{col_name}' ===")
    for item in items:
        data = item["data"]
        print(f"  {data.get('title', '(geen titel)')}")
    return items


# ---------------------------------------------------------------------------
# 7. Item bijwerken
# ---------------------------------------------------------------------------
def voorbeeld_item_bijwerken(item_key: str):
    """Voeg een tag toe aan een bestaand item."""
    zot = get_client()
    item = zot.item(item_key)
    item["data"]["tags"].append({"tag": "pyzotero-voorbeeld"})
    zot.update_item(item)
    print(f"\n=== Tag 'pyzotero-voorbeeld' toegevoegd aan {item_key} ===")


# ---------------------------------------------------------------------------
# 8. Item verwijderen
# ---------------------------------------------------------------------------
def voorbeeld_item_verwijderen(item_key: str):
    """Verwijder een item (verplaatst naar prullenbak)."""
    zot = get_client()
    item = zot.item(item_key)
    zot.delete_item(item)
    print(f"\n=== Item {item_key} naar prullenbak verplaatst ===")


# ---------------------------------------------------------------------------
# Main — voer alle voorbeelden uit
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Lees-voorbeelden (veilig)
    voorbeeld_items_ophalen()
    voorbeeld_collecties()
    voorbeeld_zoeken("medicine")
    voorbeeld_tags()
    voorbeeld_collectie_items()

    # Schrijf-voorbeelden (maakt/wijzigt/verwijdert een item)
    print("\n--- Schrijf-voorbeelden ---")
    antwoord = input("Wil je ook de schrijf-voorbeelden uitvoeren? (j/n): ")
    if antwoord.lower() == "j":
        key = voorbeeld_item_aanmaken()
        if key:
            voorbeeld_item_bijwerken(key)
            verwijder = input("Testitem weer verwijderen? (j/n): ")
            if verwijder.lower() == "j":
                voorbeeld_item_verwijderen(key)

    print("\nKlaar!")
