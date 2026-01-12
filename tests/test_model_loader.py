import pandas as pd
from unittest.mock import patch
from src.model.loader import ModelLoader


def test_model_loader_singleton():
    """Vérifie que le loader est bien un singleton."""
    loader1 = ModelLoader()
    loader2 = ModelLoader()
    assert loader1 is loader2


def test_detect_db_fallback(tmp_path):
    """Vérifie le fallback de la détection de DB."""
    loader = ModelLoader()
    # On force un chemin inexistant pour tester le log de warning
    with patch("src.model.loader.BASE_DIR", tmp_path):
        loader._detect_db()
        assert "data/database.sqlite" in loader.db_path


def test_load_artifacts_not_found():
    """Vérifie le comportement quand le modèle n'est pas trouvé."""
    loader = ModelLoader()
    with patch("os.path.exists", return_value=False):
        model = loader.load_artifacts("non_existent_model.joblib")
        assert model is None


def test_get_client_data_db_not_found():
    """Vérifie le comportement quand la DB n'existe pas."""
    loader_instance = ModelLoader()
    with patch.object(loader_instance, "db_path", "non_existent_db.sqlite"):
        data = loader_instance.get_client_data(123)
        assert data is None


@patch("sqlite3.connect")
def test_get_client_data_success(mock_connect):
    """Vérifie la récupération réussie des données client."""
    loader_instance = ModelLoader()

    # Mock du dataframe retourné par read_sql_query
    mock_df = pd.DataFrame({"SK_ID_CURR": [123], "AMT_INCOME_TOTAL": [1000.0]})

    with patch.object(loader_instance, "db_path", "dummy.sqlite"):
        with patch("os.path.exists", return_value=True):
            with patch("pandas.read_sql_query", return_value=mock_df):
                data = loader_instance.get_client_data(123)
                assert data is not None
                assert data.iloc[0]["SK_ID_CURR"] == 123
