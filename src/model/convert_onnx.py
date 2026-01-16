import joblib
from onnxmltools.convert.common.data_types import FloatTensorType as ONNXFloatTensorType
import onnxmltools
from pathlib import Path


def convert_model():
    model_path = Path("src/model/model.joblib")
    onnx_path = Path("src/model/model.onnx")

    if not model_path.exists():
        print(f"Error: {model_path} not found.")
        return

    print(f"Loading model from {model_path}...")
    model = joblib.load(model_path)

    # Détection du nombre de features
    from src.model.loader import loader

    sample = loader.get_client_data(100004)
    if sample is not None:
        features = sample.drop(columns=["TARGET", "SK_ID_CURR"], errors="ignore")
        n_features = features.shape[1]
    else:
        print("Error: Could not determine feature count.")
        return

    print(f"Detected {n_features} features.")

    # Utilisation du type spécifique onnxmltools
    initial_type = [("float_input", ONNXFloatTensorType([None, n_features]))]

    print("Converting LightGBM to ONNX...")
    try:
        # Extraction du classifieur si c'est un Pipeline
        if hasattr(model, "named_steps"):
            lgbm_model = model.named_steps["clf"]
        else:
            lgbm_model = model

        onx = onnxmltools.convert_lightgbm(
            lgbm_model, initial_types=initial_type, target_opset=12
        )

        with open(onnx_path, "wb") as f:
            f.write(onx.SerializeToString())

        print(f"Success! Model saved to {onnx_path}")
    except Exception as e:
        print(f"Conversion failed: {e}")


if __name__ == "__main__":
    convert_model()
