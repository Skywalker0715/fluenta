import os

from dotenv import load_dotenv

from .llm import generate_text, generate_text_ex

load_dotenv()

_translator = None
_tokenizer = None
_TOKENIZER = "Helsinki-NLP/opus-mt-id-en"


def translate_id_en(text: str) -> str:
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    global _translator, _tokenizer
    if _translator is None:
        _translator = AutoModelForSeq2SeqLM.from_pretrained(_TOKENIZER)
        _translator.eval()
        _tokenizer = AutoTokenizer.from_pretrained(_TOKENIZER)
    if not text or not text.strip():
        return ""
    inputs = _tokenizer(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        outputs = _translator.generate(**inputs, max_length=400)
    return _tokenizer.decode(outputs[0], skip_special_tokens=True)


def translate_text(text: str, target_language: str) -> str:
    if not text or not text.strip():
        return ""
    instruction = (
        f"Translate the user's text into {target_language}. Output only the translation."
    )
    return generate_text(
        [{"role": "user", "parts": [{"text": text}]}], instruction
    )


def translate_text_ex(text: str, target_language: str) -> tuple[str, str]:
    if not text or not text.strip():
        return "", "gemini"
    instruction = (
        f"Translate the user's text into {target_language}. Output only the translation."
    )
    result, provider = generate_text_ex(
        [{"role": "user", "parts": [{"text": text}]}], instruction
    )
    return result, provider

