# src/quality/validation.py
import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    TODO: Tạo expectation suite cho anonymized patient data.
    """
    context = gx.get_context()
    suite = context.add_expectation_suite("patient_data_suite")

    # Lấy validator
    df = pd.read_csv("data/raw/patients_raw.csv")
    validator = context.sources.pandas_default.read_dataframe(df)

    # --- TASK: Thêm các expectations ---

    # 1. patient_id không được null
    validator.expect_column_values_to_not_be_null("patient_id")

    # 2. TODO: cccd phải có đúng 12 ký tự
    validator.expect_column_value_lengths_to_equal(
        column="cccd",
        value=12
    )

    # 3. TODO: ket_qua_xet_nghiem phải trong khoảng [0, 50]
    validator.expect_column_values_to_be_between(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50
    )

    # 4. TODO: benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"]
    validator.expect_column_values_to_be_in_set(
        column="benh",
        value_set=valid_conditions
    )

    # 5. TODO: email phải match regex pattern
    validator.expect_column_values_to_match_regex(
        column="email",
        regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )

    # 6. TODO: Không được có duplicate patient_id
    validator.expect_column_values_to_be_unique(column="patient_id")

    validator.save_expectation_suite()
    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    TODO: Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc dạng số thuần túy
    # (sau anonymization, cccd phải là fake hoặc masked)
    if "cccd" in df.columns:
        pure_numeric_cccd = df["cccd"].astype(str).str.fullmatch(r"\d{12}", na=False).sum()
        if pure_numeric_cccd > 0:
            results["success"] = False
            results["failed_checks"].append(
                f"Found {int(pure_numeric_cccd)} possible raw CCCD values"
            )

    # Check 2: Không có null values trong các cột quan trọng
    required_columns = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        results["success"] = False
        results["failed_checks"].append(
            f"Missing required columns: {', '.join(missing_columns)}"
        )
    else:
        null_counts = df[required_columns].isnull().sum()
        bad_cols = [col for col, count in null_counts.items() if count > 0]
        if bad_cols:
            results["success"] = False
            results["failed_checks"].append(
                f"Null values found in critical columns: {', '.join(bad_cols)}"
            )

    # Check 3: Số rows phải bằng original
    try:
        original_df = pd.read_csv("data/raw/patients_raw.csv")
        if len(df) != len(original_df):
            results["success"] = False
            results["failed_checks"].append(
                f"Row count mismatch: anonymized={len(df)} original={len(original_df)}"
            )
    except FileNotFoundError:
        results["failed_checks"].append("Original file data/raw/patients_raw.csv not found")

    return results
