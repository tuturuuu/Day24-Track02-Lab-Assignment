# src/pii/detector.py
import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_analyzer.nlp_engine import NlpEngineProvider


class _FallbackAnalyzer:
    """Simple regex-based fallback when spaCy model is unavailable."""

    def analyze(self, text: str, language: str = "vi", entities: list | None = None) -> list:
        del language
        requested = set(entities or ["PERSON", "VN_PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"])
        results = []

        patterns = [
            ("VN_CCCD", r"\b\d{12}\b", 0.9),
            ("VN_PHONE", r"\b0[35789]\d{8}\b", 0.85),
            ("EMAIL_ADDRESS", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", 0.9),
            (
                "VN_PERSON",
                r"\b[A-ZÀÁẠẢÃĂẮẰẶẲẴÂẤẦẬẨẪĐÈÉẸẺẼÊẾỀỆỂỄÌÍỊỈĨÒÓỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÙÚỤỦŨƯỨỪỰỬỮỲÝỴỶỸ][a-zàáạảãăắằặẳẵâấầậẩẫđèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹ]+(?:\s+[A-ZÀÁẠẢÃĂẮẰẶẲẴÂẤẦẬẨẪĐÈÉẸẺẼÊẾỀỆỂỄÌÍỊỈĨÒÓỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÙÚỤỦŨƯỨỪỰỬỮỲÝỴỶỸ][a-zàáạảãăắằặẳẵâấầậẩẫđèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹ]+){1,3}\b",
                0.65,
            ),
        ]

        for entity, pattern, score in patterns:
            if entity not in requested and not (entity == "VN_PERSON" and "PERSON" in requested):
                continue
            for match in re.finditer(pattern, text):
                mapped_entity = "PERSON" if entity == "VN_PERSON" and "PERSON" in requested else entity
                results.append(
                    RecognizerResult(
                        entity_type=mapped_entity,
                        start=match.start(),
                        end=match.end(),
                        score=score,
                    )
                )

        return results

def build_vietnamese_analyzer() -> AnalyzerEngine:
    """
    TODO: Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN.
    """

    # --- TASK 2.2.1 ---
    # Tạo CCCD recognizer: số CCCD VN có đúng 12 chữ số
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{12}\b",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[cccd_pattern],
        supported_language="vi",
        context=["cccd", "căn cước", "chứng minh", "cmnd"]
    )

    # --- TASK 2.2.2 ---
    # Tạo phone recognizer: số điện thoại VN (0[3|5|7|8|9]xxxxxxxx)
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b0[35789]\d{8}\b",
            score=0.85
        )],
        supported_language="vi",
        context=["điện thoại", "sdt", "phone", "liên hệ"]
    )

    # Fallback recognizer cho tên tiếng Việt khi model NER không detect tốt.
    person_recognizer = PatternRecognizer(
        supported_entity="VN_PERSON",
        patterns=[Pattern(
            name="vn_person_name",
            regex=r"\b[A-ZÀÁẠẢÃĂẮẰẶẲẴÂẤẦẬẨẪĐÈÉẸẺẼÊẾỀỆỂỄÌÍỊỈĨÒÓỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÙÚỤỦŨƯỨỪỰỬỮỲÝỴỶỸ][a-zàáạảãăắằặẳẵâấầậẩẫđèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹ]+(?:\s+[A-ZÀÁẠẢÃĂẮẰẶẲẴÂẤẦẬẨẪĐÈÉẸẺẼÊẾỀỆỂỄÌÍỊỈĨÒÓỌỎÕÔỐỒỘỔỖƠỚỜỢỞỠÙÚỤỦŨƯỨỪỰỬỮỲÝỴỶỸ][a-zàáạảãăắằặẳẵâấầậẩẫđèéẹẻẽêếềệểễìíịỉĩòóọỏõôốồộổỗơớờợởỡùúụủũưứừựửữỳýỵỷỹ]+){1,3}\b",
            score=0.65
        )],
        supported_language="vi",
        context=["bệnh nhân", "họ tên", "tên", "bs", "bác sĩ"]
    )

    # --- TASK 2.2.3 ---
    # Tạo NLP engine dùng spaCy Vietnamese model
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "vi", "model_name": "vi_core_news_lg"}],
    })
    try:
        nlp_engine = provider.create_engine()
    except BaseException:
        return _FallbackAnalyzer()

    # --- TASK 2.2.4 ---
    # Khởi tạo AnalyzerEngine và add các recognizer
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["vi"])
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(person_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    TODO: Detect PII trong text tiếng Việt.
    Trả về list các RecognizerResult.
    Entities cần detect: PERSON, EMAIL_ADDRESS, VN_CCCD, VN_PHONE
    """
    results = analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "VN_PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results
