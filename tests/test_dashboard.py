from unittest.mock import patch, MagicMock
from src.api.dashboard import get_cached_drift_report


@patch("src.api.dashboard.generate_drift_report")
def test_get_cached_drift_report(mock_generate):
    """Teste la fonction de cache du dashboard."""
    mock_generate.return_value = "report_path.html"
    result = get_cached_drift_report("dummy.sqlite", "output.html")
    assert result == "report_path.html"
    mock_generate.assert_called_once_with("dummy.sqlite", "output.html")


@patch("requests.get")
def test_get_prediction(mock_get):
    """Teste la fonction get_prediction du dashboard."""
    # On mocke le retour de requests.get
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"score": 0.5}
    mock_get.return_value = mock_response

    # On importe la fonction. Note: st.cache_data va poser problème avec les mocks
    # car il essaie de pickler les arguments/résultats.
    # On contourne en accédant à la fonction originale (.data) si possible
    # ou en mockant le décorateur avant l'import.
    from src.api.dashboard import get_prediction

    # Appel de la fonction originale (sans cache)
    response = get_prediction.__wrapped__("http://localhost:8000", 123)

    assert response.status_code == 200
    assert response.json()["score"] == 0.5
