import pandas as pd
import numpy as np
from unittest.mock import patch
from src.model import features


def test_one_hot_encoder():
    df = pd.DataFrame({"A": ["a", "b", "a"], "B": [1, 2, 3]})
    df_encoded, new_cols = features.one_hot_encoder(df, nan_as_category=False)

    assert "A_a" in df_encoded.columns
    assert "A_b" in df_encoded.columns
    assert "B" in df_encoded.columns
    assert "A_a" in new_cols
    assert "B" not in new_cols
    assert df_encoded.shape[1] == 3


def test_one_hot_encoder_with_nan():
    df = pd.DataFrame({"A": ["a", np.nan, "b"], "B": [1, 2, 3]})
    df_encoded, new_cols = features.one_hot_encoder(df, nan_as_category=True)

    assert "A_nan" in df_encoded.columns
    assert df_encoded["A_nan"].sum() == 1


@patch("src.model.features.pd.read_csv")
def test_preprocess_application_train_test(mock_read_csv):
    # Mock data
    data_train = pd.DataFrame(
        {
            "SK_ID_CURR": [100001, 100002],
            "CODE_GENDER": ["M", "F"],
            "FLAG_OWN_CAR": ["N", "Y"],
            "FLAG_OWN_REALTY": ["Y", "N"],
            "DAYS_EMPLOYED": [100, 365243],
            "DAYS_BIRTH": [-10000, -12000],
            "AMT_INCOME_TOTAL": [100000, 200000],
            "AMT_CREDIT": [500000, 1000000],
            "AMT_ANNUITY": [25000, 50000],
            "CNT_FAM_MEMBERS": [2, 3],
            "TARGET": [0, 1],
        }
    )

    data_test = pd.DataFrame(
        {
            "SK_ID_CURR": [100003],
            "CODE_GENDER": ["M"],
            "FLAG_OWN_CAR": ["Y"],
            "FLAG_OWN_REALTY": ["Y"],
            "DAYS_EMPLOYED": [-500],
            "DAYS_BIRTH": [-15000],
            "AMT_INCOME_TOTAL": [150000],
            "AMT_CREDIT": [600000],
            "AMT_ANNUITY": [30000],
            "CNT_FAM_MEMBERS": [1],
        }
    )

    # Return train first, then test
    mock_read_csv.side_effect = [data_train, data_test]

    df = features.preprocess_application_train_test("dummy_path", sample_size=100)

    assert "DAYS_EMPLOYED_PERC" in df.columns
    assert "INCOME_CREDIT_PERC" in df.columns
    # Check if 365243 was replaced by NaN
    assert np.isnan(df.loc[1, "DAYS_EMPLOYED"])
    # Check shape: 3 rows (2 train + 1 test)
    assert len(df) == 3


@patch("src.model.features.pd.read_csv")
def test_preprocess_bureau_and_balance(mock_read_csv):
    # Mock bureau
    bureau = pd.DataFrame(
        {
            "SK_ID_CURR": [100001, 100001, 100002],
            "SK_ID_BUREAU": [5001, 5002, 5003],
            "CREDIT_ACTIVE": ["Active", "Closed", "Active"],
            "DAYS_CREDIT": [-100, -200, -50],
            "DAYS_CREDIT_ENDDATE": [100, -100, 200],
            "DAYS_CREDIT_UPDATE": [-10, -20, -5],
            "CREDIT_DAY_OVERDUE": [0, 0, 0],
            "AMT_CREDIT_MAX_OVERDUE": [0, 0, 0],
            "AMT_CREDIT_SUM": [10000, 20000, 5000],
            "AMT_CREDIT_SUM_DEBT": [5000, 0, 1000],
            "AMT_CREDIT_SUM_OVERDUE": [0, 0, 0],
            "AMT_CREDIT_SUM_LIMIT": [0, 0, 0],
            "AMT_ANNUITY": [0, 0, 0],
            "CNT_CREDIT_PROLONG": [0, 0, 0],
        }
    )

    # Mock bureau_balance
    bb = pd.DataFrame(
        {
            "SK_ID_BUREAU": [5001, 5001, 5002],
            "MONTHS_BALANCE": [-1, -2, -1],
            "STATUS": ["0", "C", "X"],
        }
    )

    mock_read_csv.side_effect = [bureau, bb]

    df = features.preprocess_bureau_and_balance("dummy_path", sample_size=100)

    # Check if aggregation columns exist
    assert any(col.startswith("BURO_") for col in df.columns)
    assert any(col.startswith("ACTIVE_") for col in df.columns)
    assert any(col.startswith("CLOSED_") for col in df.columns)
    # 2 unique SK_ID_CURR
    assert len(df) == 2


@patch("src.model.features.pd.read_csv")
def test_preprocess_previous_applications(mock_read_csv):
    prev = pd.DataFrame(
        {
            "SK_ID_CURR": [100001, 100002],
            "SK_ID_PREV": [6001, 6002],
            "NAME_CONTRACT_STATUS": ["Approved", "Refused"],
            "AMT_ANNUITY": [5000, 0],
            "AMT_APPLICATION": [100000, 0],
            "AMT_CREDIT": [100000, 0],
            "AMT_DOWN_PAYMENT": [0, 0],
            "AMT_GOODS_PRICE": [100000, 0],
            "HOUR_APPR_PROCESS_START": [10, 12],
            "RATE_DOWN_PAYMENT": [0, 0],
            "DAYS_DECISION": [-100, -200],
            "CNT_PAYMENT": [12, 0],
            "DAYS_FIRST_DRAWING": [365243, 365243],
            "DAYS_FIRST_DUE": [365243, 365243],
            "DAYS_LAST_DUE_1ST_VERSION": [365243, 365243],
            "DAYS_LAST_DUE": [365243, 365243],
            "DAYS_TERMINATION": [365243, 365243],
        }
    )

    mock_read_csv.return_value = prev

    df = features.preprocess_previous_applications("dummy_path", sample_size=100)

    assert any(col.startswith("PREV_") for col in df.columns)
    assert any(col.startswith("APPROVED_") for col in df.columns)
    assert any(col.startswith("REFUSED_") for col in df.columns)
    assert len(df) == 2


@patch("src.model.features.pd.read_csv")
def test_preprocess_pos_cash_balance(mock_read_csv):
    pos = pd.DataFrame(
        {
            "SK_ID_CURR": [100001, 100001],
            "SK_ID_PREV": [7001, 7001],
            "MONTHS_BALANCE": [-1, -2],
            "SK_DPD": [0, 0],
            "SK_DPD_DEF": [0, 0],
            "NAME_CONTRACT_STATUS": ["Active", "Active"],
        }
    )

    mock_read_csv.return_value = pos

    df = features.preprocess_pos_cash_balance("dummy_path", sample_size=100)

    assert any(col.startswith("POS_") for col in df.columns)
    assert "POS_COUNT" in df.columns
    assert len(df) == 1


@patch("src.model.features.pd.read_csv")
def test_preprocess_installments_payments(mock_read_csv):
    ins = pd.DataFrame(
        {
            "SK_ID_CURR": [100001],
            "SK_ID_PREV": [8001],
            "NUM_INSTALMENT_VERSION": [1],
            "AMT_INSTALMENT": [5000],
            "AMT_PAYMENT": [5000],
            "DAYS_ENTRY_PAYMENT": [-30],
            "DAYS_INSTALMENT": [-30],
        }
    )

    mock_read_csv.return_value = ins

    df = features.preprocess_installments_payments("dummy_path", sample_size=100)

    assert any(col.startswith("INSTAL_") for col in df.columns)
    assert "INSTAL_COUNT" in df.columns
    assert len(df) == 1


@patch("src.model.features.pd.read_csv")
def test_preprocess_credit_card_balance(mock_read_csv):
    cc = pd.DataFrame(
        {
            "SK_ID_CURR": [100001],
            "SK_ID_PREV": [9001],
            "AMT_BALANCE": [0],
            "AMT_CREDIT_LIMIT_ACTUAL": [10000],
            "NAME_CONTRACT_STATUS": ["Active"],
        }
    )

    mock_read_csv.return_value = cc

    df = features.preprocess_credit_card_balance("dummy_path", sample_size=100)

    assert any(col.startswith("CC_") for col in df.columns)
    assert "CC_COUNT" in df.columns
    assert len(df) == 1
