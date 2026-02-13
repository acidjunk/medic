"""Happy flow tests — mockt de Zotero API zodat er geen credentials nodig zijn."""

import os
from unittest.mock import MagicMock, patch

import pytest

# Stel dummy env vars in vóór import van examples
os.environ["ZOTERO_LIBRARY_ID"] = "12345"
os.environ["ZOTERO_API_KEY"] = "fake-api-key"
os.environ["ZOTERO_LIBRARY_TYPE"] = "user"

import examples


# -- Fixtures ----------------------------------------------------------------

FAKE_ITEMS = [
    {
        "key": "ABC123",
        "data": {
            "key": "ABC123",
            "itemType": "journalArticle",
            "title": "Test Article One",
            "tags": [],
            "version": 1,
        },
    },
    {
        "key": "DEF456",
        "data": {
            "key": "DEF456",
            "itemType": "book",
            "title": "Test Book Two",
            "tags": [],
            "version": 2,
        },
    },
]

FAKE_COLLECTIONS = [
    {
        "key": "COL001",
        "data": {
            "key": "COL001",
            "name": "Mijn Collectie",
            "numItems": 5,
        },
    },
]

FAKE_TAGS = [
    {"tag": "machine-learning"},
    {"tag": "python"},
]


@pytest.fixture
def mock_zotero():
    """Geeft een gemockte Zotero client terug."""
    mock = MagicMock()
    mock.top.return_value = FAKE_ITEMS
    mock.collections_top.return_value = FAKE_COLLECTIONS
    mock.tags.return_value = FAKE_TAGS
    mock.collection_items.return_value = FAKE_ITEMS
    mock.collection.return_value = FAKE_COLLECTIONS[0]
    mock.item.return_value = FAKE_ITEMS[0]
    mock.item_template.return_value = {
        "itemType": "book",
        "title": "",
        "creators": [{"creatorType": "author", "firstName": "", "lastName": ""}],
        "date": "",
        "abstractNote": "",
        "tags": [],
    }
    mock.create_items.return_value = {
        "success": {"0": "NEW123"},
        "successful": {"0": {"key": "NEW123"}},
        "failed": {},
        "unchanged": {},
    }
    mock.update_item.return_value = None
    mock.delete_item.return_value = None

    with patch("examples.get_client", return_value=mock):
        yield mock


# -- Tests -------------------------------------------------------------------


def test_items_ophalen(mock_zotero, capsys):
    items = examples.voorbeeld_items_ophalen()

    assert len(items) == 2
    assert items[0]["data"]["title"] == "Test Article One"
    mock_zotero.top.assert_called_once_with(limit=5)

    output = capsys.readouterr().out
    assert "Test Article One" in output
    assert "journalArticle" in output


def test_collecties(mock_zotero, capsys):
    collections = examples.voorbeeld_collecties()

    assert len(collections) == 1
    assert collections[0]["data"]["name"] == "Mijn Collectie"
    mock_zotero.collections_top.assert_called_once()

    output = capsys.readouterr().out
    assert "Mijn Collectie" in output


def test_zoeken(mock_zotero, capsys):
    results = examples.voorbeeld_zoeken("test")

    assert len(results) == 2
    mock_zotero.add_parameters.assert_called_once_with(q="test", qmode="titleCreatorYear")
    mock_zotero.top.assert_called_once_with(limit=10)

    output = capsys.readouterr().out
    assert "test" in output


def test_tags(mock_zotero, capsys):
    tags = examples.voorbeeld_tags()

    assert len(tags) == 2
    assert tags[0]["tag"] == "machine-learning"
    mock_zotero.tags.assert_called_once_with(limit=10)

    output = capsys.readouterr().out
    assert "machine-learning" in output
    assert "python" in output


def test_collectie_items(mock_zotero, capsys):
    items = examples.voorbeeld_collectie_items()

    assert len(items) == 2
    mock_zotero.collections_top.assert_called_once_with(limit=1)
    mock_zotero.collection_items.assert_called_once_with("COL001", limit=5)

    output = capsys.readouterr().out
    assert "Mijn Collectie" in output


def test_collectie_items_met_key(mock_zotero, capsys):
    items = examples.voorbeeld_collectie_items("COL001")

    assert len(items) == 2
    mock_zotero.collections_top.assert_not_called()
    mock_zotero.collection_items.assert_called_once_with("COL001", limit=5)


def test_item_aanmaken(mock_zotero, capsys):
    key = examples.voorbeeld_item_aanmaken()

    assert key == "NEW123"
    mock_zotero.item_template.assert_called_once_with("book")
    mock_zotero.create_items.assert_called_once()

    template = mock_zotero.create_items.call_args[0][0][0]
    assert template["title"] == "Voorbeeld Boek via Pyzotero"
    assert template["creators"][0]["lastName"] == "Jansen"

    output = capsys.readouterr().out
    assert "NEW123" in output


def test_item_bijwerken(mock_zotero, capsys):
    examples.voorbeeld_item_bijwerken("ABC123")

    mock_zotero.item.assert_called_once_with("ABC123")
    mock_zotero.update_item.assert_called_once()

    output = capsys.readouterr().out
    assert "pyzotero-voorbeeld" in output


def test_item_verwijderen(mock_zotero, capsys):
    examples.voorbeeld_item_verwijderen("ABC123")

    mock_zotero.item.assert_called_once_with("ABC123")
    mock_zotero.delete_item.assert_called_once()

    output = capsys.readouterr().out
    assert "prullenbak" in output
