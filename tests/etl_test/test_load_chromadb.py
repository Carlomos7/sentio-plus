import chromadb
from etl.load_chromadb import query_reviews


class FakeCollection:
    def query(self, *args, **kwargs):
        return {
            "documents": [["example review"]],
            "metadatas": [[{"app_name": "Test App"}]],
            "distances": [[0.5]]
        }


class FakeClient:
    def get_collection(self, name):
        return FakeCollection()


def test_query_reviews_returns_expected_keys(monkeypatch):
    monkeypatch.setattr(
        chromadb,
        "PersistentClient",
        lambda *args, **kwargs: FakeClient()
    )

    result = query_reviews("some random query", n_results=2)

    assert "documents" in result
    assert "metadatas" in result
    assert "distances" in result


def test_query_reviews_handles_no_matches_gracefully(monkeypatch):
    class NoMatchCollection:
        def query(self, *args, **kwargs):
            return {
                "documents": [["irrelevant"]],
                "metadatas": [[{"app_name": "Test App"}]],
                "distances": [[999.0]]  # large distance → filtered empty
            }

    class NoMatchClient:
        def get_collection(self, name):
            return NoMatchCollection()

    monkeypatch.setattr(
        chromadb,
        "PersistentClient",
        lambda *args, **kwargs: NoMatchClient()
    )

    result = query_reviews("no matches")

    assert "documents" in result
    assert "metadatas" in result
    assert "distances" in result
    assert "message" in result
