# Medic — Pyzotero Voorbeeldproject

[![CI](https://github.com/acidjunk/medic/actions/workflows/ci.yml/badge.svg)](https://github.com/acidjunk/medic/actions/workflows/ci.yml)

Een klein Python-project dat de belangrijkste functionaliteit van
[pyzotero](https://pyzotero.readthedocs.io/en/latest/) demonstreert.
Pyzotero is een Python-wrapper rond de [Zotero Web API v3](https://www.zotero.org/support/dev/web_api/v3/start)
waarmee je je Zotero-bibliotheek kunt lezen, doorzoeken en beheren vanuit Python.

## Vereisten

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (aanbevolen) of pip
- Een [Zotero](https://www.zotero.org/) account
- Een Zotero API-key (zie [Configuratie](#configuratie))

## Installatie

```bash
# Clone het project
git clone https://github.com/acidjunk/medic.git
cd medic

# Met uv (aanbevolen)
uv sync

# Of met pip
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

## Configuratie

Voordat je de voorbeelden kunt draaien heb je twee dingen nodig uit je
Zotero-account:

| Gegeven | Waar te vinden |
|---------|----------------|
| **Library ID** | https://www.zotero.org/settings/keys — staat bovenaan als *"Your userID for use in API calls is ..."* |
| **API Key** | https://www.zotero.org/settings/keys/new — maak een nieuwe key aan met de gewenste rechten |

Kopieer het `.env.example` bestand en vul je gegevens in:

```bash
cp .env.example .env
```

```env
ZOTERO_LIBRARY_ID=123456
ZOTERO_API_KEY=aBcDeFgHiJkLmNoPqRsTuVwX
ZOTERO_LIBRARY_TYPE=user
```

> **Let op:** Het `.env` bestand staat in `.gitignore` en wordt niet meegecommit.

### Library type

| Type | Wanneer |
|------|---------|
| `user` | Je wilt je persoonlijke bibliotheek benaderen |
| `group` | Je wilt een groepsbibliotheek benaderen — gebruik dan het **groeps-ID** als `LIBRARY_ID` |

Het groeps-ID vind je in de URL van de groepspagina op zotero.org
(bijv. `https://www.zotero.org/groups/12345/naam` → ID is `12345`).

## Gebruik

```bash
# Met uv
uv run python examples.py

# Of met geactiveerde venv
source .venv/bin/activate
python examples.py
```

Het script voert eerst alle **lees-voorbeelden** uit (veilig, wijzigt niets)
en vraagt daarna of je ook de **schrijf-voorbeelden** wilt draaien.

## Voorbeelden in detail

### 1. Items ophalen

```python
zot = Zotero(library_id, library_type, api_key)
items = zot.top(limit=5)
for item in items:
    print(item["data"]["title"])
```

Haalt de laatste 5 top-level items op. `top()` geeft alleen items op het
hoogste niveau terug (geen bijlagen of notities). Standaard retourneert
pyzotero maximaal 100 items; gebruik `zot.everything(zot.top)` om alles
op te halen.

### 2. Collecties bekijken

```python
collections = zot.collections_top()
for col in collections:
    print(col["data"]["name"], col["data"]["numItems"])
```

Toont alle top-level collecties met het aantal items. Gebruik
`zot.collections_sub(key)` om subcollecties van een specifieke collectie
op te halen.

### 3. Zoeken

```python
zot.add_parameters(q="medicine", qmode="titleCreatorYear")
results = zot.top(limit=10)
```

Doorzoekt je bibliotheek op titel, auteur en jaar. Beschikbare zoekmodi:

| `qmode` | Zoekt in |
|---------|----------|
| `titleCreatorYear` | Titel, auteur en jaar (standaard) |
| `everything` | Alle velden inclusief full-text inhoud van PDF's |

### 4. Item aanmaken

```python
template = zot.item_template("book")
template["title"] = "Mijn Boek"
template["creators"] = [
    {"creatorType": "author", "firstName": "Jan", "lastName": "Jansen"}
]
resp = zot.create_items([template])
nieuwe_key = resp["success"]["0"]
```

Maakt een nieuw item aan op basis van een template. Beschikbare item-types
kun je opvragen met `zot.item_types()`. Veelgebruikte types:

- `journalArticle` — tijdschriftartikel
- `book` — boek
- `bookSection` — hoofdstuk
- `conferencePaper` — conferentiebijdrage
- `report` — rapport
- `thesis` — scriptie/proefschrift
- `webpage` — webpagina

### 5. Tags beheren

```python
tags = zot.tags(limit=10)
for tag in tags:
    print(tag["tag"])
```

Haalt tags op uit je bibliotheek. Je kunt ook tags toevoegen aan een item:

```python
item = zot.item("ABC123")
item["data"]["tags"].append({"tag": "nieuwe-tag"})
zot.update_item(item)
```

### 6. Items in een collectie

```python
items = zot.collection_items("COLLECTION_KEY", limit=5)
```

Haalt items op uit een specifieke collectie. De `collection_key` vind je
via `zot.collections()`.

### 7. Item bijwerken

```python
item = zot.item("ABC123")
item["data"]["title"] = "Nieuwe Titel"
item["data"]["tags"].append({"tag": "bijgewerkt"})
zot.update_item(item)
```

Haal het item eerst op, wijzig de `data`-dict, en stuur het terug met
`update_item()`. Pyzotero handelt de versie-tracking automatisch af.

### 8. Item verwijderen

```python
item = zot.item("ABC123")
zot.delete_item(item)
```

Verplaatst het item naar de prullenbak in Zotero. Het item is daarna nog
te herstellen via de Zotero-client.

## Projectstructuur

```
medic/
├── .env.example      # Template voor credentials
├── .env              # Jouw credentials (niet in git)
├── .gitignore
├── LICENSE           # Apache License 2.0
├── pyproject.toml    # Project configuratie en dependencies
├── uv.lock           # Lockfile voor reproduceerbare installaties
├── examples.py       # Alle voorbeeldcode
└── README.md
```

## Veelgebruikte pyzotero-patronen

### Alles ophalen (pagination)

Standaard retourneert pyzotero maximaal 100 items per aanroep. Om alles
op te halen:

```python
alle_items = zot.everything(zot.top)
```

### Sorteren

```python
zot.add_parameters(sort="dateAdded", direction="desc")
items = zot.top(limit=10)
```

Beschikbare sorteervelden: `dateAdded`, `dateModified`, `title`,
`creator`, `itemType`, `date`, `publisher`.

### Filteren op item-type

```python
zot.add_parameters(itemType="journalArticle")
artikelen = zot.top()
```

Meerdere types combineren met `||`:

```python
zot.add_parameters(itemType="book || bookSection")
```

### Filteren op tag

```python
zot.add_parameters(tag="machine learning")
items = zot.top()
```

Meerdere tags (AND-logica):

```python
zot.add_parameters(tag=["climate", "adaptation"])
```

### Bijlagen downloaden

```python
# Als bytes
pdf = zot.file("ITEM_KEY")
with open("artikel.pdf", "wb") as f:
    f.write(pdf)

# Of met de handige dump-methode
zot.dump("ITEM_KEY", "artikel.pdf", "./downloads")
```

### BibTeX export

```python
zot.add_parameters(format="bibtex")
bibtex = zot.top(limit=5)
```

## Foutafhandeling

Pyzotero gooit specifieke exceptions:

| Exception | Betekenis |
|-----------|-----------|
| `zotero_errors.UserNotAuthorised` | Ongeldige API key of geen rechten |
| `zotero_errors.ResourceNotFound` | Item/collectie niet gevonden |
| `zotero_errors.PreConditionFailed` | Item is ondertussen gewijzigd (versie-conflict) |
| `zotero_errors.RequestNotSuccessful` | Overige API-fouten |

```python
from pyzotero import zotero_errors

try:
    item = zot.item("ONGELDIG")
except zotero_errors.ResourceNotFound:
    print("Item niet gevonden")
```

## Meer informatie

- [Pyzotero documentatie](https://pyzotero.readthedocs.io/en/latest/)
- [Zotero Web API v3](https://www.zotero.org/support/dev/web_api/v3/start)
- [Pyzotero GitHub](https://github.com/urschrei/pyzotero)
