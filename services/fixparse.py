TAG_LABELS = {
    "past_tense": "Past tense",
    "present_tense": "Present tense",
    "future_tense": "Future tense",
    "articles": "Artikel (a/an/the)",
    "prepositions": "Preposisi",
    "subject_verb_agreement": "Subject-verb agreement",
    "plural_singular": "Plural dan singular",
    "word_order": "Urutan kata",
    "word_choice": "Pilihan kata",
    "collocation": "Kolokasi",
    "code_mixing": "Campur bahasa",
    "other": "Lainnya",
}


def parse_fix(text: str | None) -> dict:
    if not text:
        return {"corrected": None, "explanation": text or "", "tag": "other", "structured": False}
    parts = [part.strip() for part in text.split(" || ")]
    if len(parts) >= 2:
        corrected, explanation = parts[0], parts[1]
        tag = parts[2] if len(parts) >= 3 and parts[2] else "other"
        if tag not in TAG_LABELS:
            tag = "other"
        return {
            "corrected": corrected,
            "explanation": explanation,
            "tag": tag,
            "structured": True,
        }
    return {"corrected": None, "explanation": text, "tag": "other", "structured": False}
