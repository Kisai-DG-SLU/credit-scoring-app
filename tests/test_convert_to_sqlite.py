from unittest.mock import patch
import pandas as pd
import os
from src.database.convert_to_sqlite import convert_csv_to_sqlite


def test_convert_csv_to_sqlite_success(tmp_path):
    csv_path = tmp_path / "test.csv"
    db_path = tmp_path / "test.sqlite"
    pd.DataFrame({"A": [1], "B": [2]}).to_csv(csv_path, index=False)

    convert_csv_to_sqlite(str(csv_path), str(db_path))
    assert os.path.exists(db_path)


@patch("os.path.exists")
def test_convert_csv_to_sqlite_no_file(mock_exists):
    mock_exists.return_value = False
    # Ne doit pas crasher
    convert_csv_to_sqlite("none.csv", "none.sqlite")
