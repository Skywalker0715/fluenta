import os
import torch

from dotenv import load_dotenv
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from .llm import generate_text

load_dotenv()

_translator = None
_TOKENIZER = "Helsinki-NLP/opus-mt-id-en"


def translate_id_en(text: str) -> str:
    global _translator
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

