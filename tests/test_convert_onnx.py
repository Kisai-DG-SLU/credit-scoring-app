from unittest.mock import patch, MagicMock
from src.model.convert_onnx import convert_model


@patch("joblib.load")
@patch("onnxmltools.convert_lightgbm")
@patch("src.model.loader.loader.get_client_data")
@patch("os.path.exists")
def test_convert_model_success(mock_exists, mock_get_data, mock_convert, mock_load):
    # Setup
    mock_exists.return_value = True

    mock_df = MagicMock()
    mock_df.drop.return_value.shape = (1, 10)  # 10 features
    mock_get_data.return_value = mock_df

    mock_onx = MagicMock()
    mock_onx.SerializeToString.return_value = b"fake_onnx_data"
    mock_convert.return_value = mock_onx

    # Exécution
    with patch("builtins.open", MagicMock()):
        convert_model()

    assert mock_load.called
    assert mock_convert.called


@patch("os.path.exists")
def test_convert_model_no_file(mock_exists):
    mock_exists.return_value = False
    # Ne doit pas crasher
    convert_model()
