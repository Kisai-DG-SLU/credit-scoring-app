from unittest.mock import patch
from src.api.dashboard import get_cached_drift_report


@patch("src.api.dashboard.generate_drift_report")
def test_get_cached_drift_report(mock_generate):
    """Teste la fonction de cache du dashboard."""
    mock_generate.return_value = "report_path.html"
    result = get_cached_drift_report("dummy.sqlite", "output.html")
    assert result == "report_path.html"
    mock_generate.assert_called_once_with("dummy.sqlite", "output.html")
