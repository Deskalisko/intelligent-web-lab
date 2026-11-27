"""Kontrola inicjalizacji bez serwera; nie zastępuje próby z Elasticsearch."""
from unittest.mock import patch
from urllib.error import HTTPError
import search


def check():
    for exists in (True, False):
        search.elastic_index.cache_clear()
        calls = []

        def request(method, path, payload=None, content_type="application/json"):
            calls.append((method, path, payload, content_type))
            if method == "GET" and path == "/" + search.INDEX and not exists:
                raise HTTPError(path, 404, "missing", {}, None)
            return {"errors": False}

        with patch.object(search, "elastic_request", side_effect=request):
            search.elastic_index()
            search.elastic_index()
        bulk = [call for call in calls if call[1].startswith("/_bulk")]
        assert len(bulk) == 1
        assert len(bulk[0][2].decode().splitlines()) == 2 * len(search.documents)
        assert bulk[0][2].endswith(b"\n")
        assert bulk[0][3] == "application/x-ndjson"
        assert sum(method == "PUT" for method, *_ in calls) == int(not exists)

    search.elastic_index.cache_clear()
    attempts = []

    def fail_then_retry(method, path, payload=None, content_type="application/json"):
        if path.startswith("/_bulk"):
            attempts.append(path)
            return {"errors": len(attempts) == 1}
        return {}

    with patch.object(search, "elastic_request", side_effect=fail_then_retry):
        try:
            search.elastic_index()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Nie zgłoszono błędu importu")
        search.elastic_index()
    assert len(attempts) == 2
    search.elastic_index.cache_clear()
    print("OK: istniejący/nowy indeks, cache sukcesu, ponowienie po błędzie bulk")


if __name__ == "__main__":
    check()
