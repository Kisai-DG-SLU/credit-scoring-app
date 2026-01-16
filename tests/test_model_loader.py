import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
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


def test_predict_proba_no_data():
    """Vérifie predict_proba quand aucune donnée client n'est trouvée."""
    loader_instance = ModelLoader()
    with patch.object(loader_instance, "get_client_data", return_value=None):
        assert loader_instance.predict_proba(123) is None


def test_predict_proba_onnx_success():
    """Vérifie l'inférence réussie via ONNX."""
    loader_instance = ModelLoader()
    mock_data = pd.DataFrame({"SK_ID_CURR": [123], "FEATURE1": [1.0]})

    mock_session = MagicMock()
    # Simuler la structure de retour de ONNX : [label, [probas]]
    mock_session.run.return_value = [None, np.array([[0.4, 0.6]])]
    mock_input = MagicMock()
    mock_input.name = "float_input"
    mock_session.get_inputs.return_value = [mock_input]

    loader_instance.onnx_session = mock_session

    with patch.object(loader_instance, "get_client_data", return_value=mock_data):
        score = loader_instance.predict_proba(123)
        assert score == 0.6


def test_predict_proba_onnx_error_fallback():
    """Vérifie le fallback sur Joblib si ONNX échoue pendant l'inférence."""
    loader_instance = ModelLoader()
    mock_data = pd.DataFrame({"SK_ID_CURR": [123], "FEATURE1": [1.0]})

    mock_session = MagicMock()
    mock_session.run.side_effect = Exception("ONNX Crash")
    loader_instance.onnx_session = mock_session

    mock_model = MagicMock()
    mock_model.predict_proba.return_value = np.array([[0.2, 0.8]])
    loader_instance.model = mock_model

    with patch.object(loader_instance, "get_client_data", return_value=mock_data):
        score = loader_instance.predict_proba(123)
        assert score == 0.8


def test_get_shap_values_cached_success():
    """Vérifie le calcul et le cache des SHAP values."""
    loader_instance = ModelLoader()
    mock_data = pd.DataFrame({"SK_ID_CURR": [123], "FEATURE1": [1.0]})

    mock_explainer = MagicMock()
    mock_explainer.return_value = "fake_shap_values"
    loader_instance.explainer = mock_explainer

    with patch.object(loader_instance, "get_client_data", return_value=mock_data):
        # On vide le cache avant le test
        loader_instance.get_shap_values_cached.cache_clear()

        res1 = loader_instance.get_shap_values_cached(123)
        assert res1 == "fake_shap_values"

        res2 = loader_instance.get_shap_values_cached(123)
        assert res2 == "fake_shap_values"
        assert mock_explainer.call_count == 1


def test_get_shap_values_no_data():
    """Vérifie get_shap_values_cached quand aucune donnée client n'est trouvée."""
    loader_instance = ModelLoader()
    with patch.object(loader_instance, "get_client_data", return_value=None):
        assert loader_instance.get_shap_values_cached(123) is None


def test_load_artifacts_joblib_success():
    """Vérifie le chargement réussi du modèle Joblib et de SHAP."""
    loader_instance = ModelLoader()
    loader_instance.model = None
    loader_instance.explainer = None

    mock_model = MagicMock()
    # Simuler un Pipeline scikit-learn
    mock_model.named_steps = {"clf": MagicMock()}

    with patch("os.path.exists", return_value=True):
        with patch("joblib.load", return_value=mock_model):
            with patch("shap.TreeExplainer", return_value=MagicMock()):
                model = loader_instance.load_artifacts()
                assert model is not None
                assert loader_instance.explainer is not None
