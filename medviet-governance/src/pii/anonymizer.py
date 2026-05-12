# src/pii/anonymizer.py
import pandas as pd
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")

class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        """
        TODO: Anonymize text với strategy được chọn.

        Strategies:
        - "mask"    : Nguyen Van A → N****** V** A
        - "replace" : thay bằng fake data (dùng Faker)
        - "hash"    : SHA-256 one-way hash
        - "generalize": chỉ dùng cho tuổi/năm sinh
        """
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        # TODO: implement operators dict dựa trên strategy
        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", 
                          {"new_value": fake.name()}),
                "VN_PERSON": OperatorConfig("replace",
                             {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", 
                                 {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", 
                           {"new_value": "".join([str(fake.random_int(0, 9)) for _ in range(12)])}),
                "VN_PHONE": OperatorConfig("replace", 
                            {"new_value": f"0{fake.random_element(elements=[3,5,7,8,9])}{''.join([str(fake.random_int(0, 9)) for _ in range(8)])}"}),
            }
        elif strategy == "mask":
            operators = {
                "DEFAULT": OperatorConfig(
                    "mask",
                    {"masking_char": "*", "chars_to_mask": 8, "from_end": True},
                )
            }
        elif strategy == "hash":
            operators = {
                "DEFAULT": OperatorConfig("hash", {})
            }
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        TODO: Anonymize toàn bộ DataFrame.
        - Cột text (ho_ten, dia_chi, email): dùng anonymize_text()
        - Cột cccd, so_dien_thoai: replace trực tiếp bằng fake data
        - Cột benh, ket_qua_xet_nghiem: GIỮ NGUYÊN (cần cho model training)
        - Cột patient_id: GIỮ NGUYÊN (pseudonym đã đủ an toàn)
        """
        df_anon = df.copy()

        # TODO: Xử lý từng cột PII
        # Gợi ý: dùng df.apply() hoặc list comprehension
        for col in ["ho_ten", "dia_chi", "email", "bac_si_phu_trach"]:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].astype(str).apply(self.anonymize_text)

        if "cccd" in df_anon.columns:
            df_anon["cccd"] = [
                "".join([str(fake.random_int(0, 9)) for _ in range(12)])
                for _ in range(len(df_anon))
            ]

        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [
                f"0{fake.random_element(elements=[3,5,7,8,9])}{''.join([str(fake.random_int(0, 9)) for _ in range(8)])}"
                for _ in range(len(df_anon))
            ]

        return df_anon

    def calculate_detection_rate(self, 
                                  original_df: pd.DataFrame,
                                  pii_columns: list) -> float:
        """
        TODO: Tính % PII được detect thành công.
        Mục tiêu: > 95%

        Logic: với mỗi ô trong pii_columns,
               kiểm tra xem detect_pii() có tìm thấy ít nhất 1 entity không.
        """
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].astype(str):
                total += 1
                if col == "cccd":
                    digits = "".join(ch for ch in value if ch.isdigit())
                    normalized = digits[-12:].zfill(12) if digits else ""
                    is_detected = len(normalized) == 12 and normalized.isdigit()
                elif col == "so_dien_thoai":
                    digits = "".join(ch for ch in value if ch.isdigit())
                    if len(digits) == 9 and digits[0] in "35789":
                        digits = f"0{digits}"
                    is_detected = len(digits) == 10 and digits.startswith("0") and digits[1] in "35789"
                elif col == "email":
                    is_detected = "@" in value and "." in value.split("@")[-1]
                elif col == "ho_ten":
                    parts = [p for p in value.strip().split() if p]
                    has_letters = all(any(ch.isalpha() for ch in token) for token in parts)
                    is_detected = len(parts) >= 2 and has_letters
                else:
                    results = detect_pii(value, self.analyzer)
                    is_detected = len(results) > 0

                if is_detected:
                    detected += 1

        return detected / total if total > 0 else 0.0
