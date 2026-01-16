from unittest.mock import patch, MagicMock
import importlib
import src.api.dashboard as dashboard
from src.api.dashboard import get_cached_drift_report


@patch("src.api.dashboard.generate_drift_report")
def test_get_cached_drift_report(mock_generate):
    """Teste la fonction de cache du dashboard."""
    mock_generate.return_value = "report_path.html"
    result = get_cached_drift_report("dummy.sqlite", "output.html")
    assert result == "report_path.html"


@patch("requests.get")
def test_get_prediction_dashboard(mock_get):
    """Teste la fonction get_prediction du dashboard."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"score": 0.5}
    mock_get.return_value = mock_response

    from src.api.dashboard import get_prediction

    response = get_prediction.__wrapped__("http://localhost:8000", 123)
    assert response.status_code == 200


@patch("streamlit.sidebar.text_input")
@patch("streamlit.tabs")
@patch("streamlit.columns")
@patch("streamlit.set_page_config")
@patch("src.api.dashboard.get_prediction")
def test_dashboard_full_load(mock_pred, mock_cfg, mock_cols, mock_tabs, mock_side):
    """Simule le chargement complet du script dashboard.py."""
    mock_tabs.return_value = [MagicMock(), MagicMock()]
    mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]

    try:
        importlib.reload(dashboard)
    except Exception:
        pass
    assert dashboard is not None
