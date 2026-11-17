import io
import re
import time

from docx import Document
from google.genai import types

from .llm import generate_text, _groq_chat

_MAX_FILE_BYTES = 10 * 1024 * 1024
_CHUNK_LIMIT = 6000
_MAX_CHUNKS = 20
_SUMMARIZE_LIMIT = 30000
_TASKS = ("translate", "summarize")

_GROQ_MAX_TOTAL = 10000
_GROQ_PART_LIMIT = 2500
_GROQ_MAX_PARTS = 4
_GROQ_PAUSE_DETIK = 3


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace")
    if name.endswith(".docx"):
        document = Document(io.BytesIO(data))
        parts = [paragraph.text for paragraph in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    parts.append(cell.text)
        return "\n".join(parts)
    raise ValueError("Format file tidak didukung.")


def _instruction(task: str, target_language: str) -> str:
    if task == "translate":
        return (
            f"Translate the document into {target_language}. "
            "Keep structure and paragraphs. Output only the translation."
        )
    return (
        f"Summarize the document in {target_language} as bullet points (max 15). "
        "Output only the summary."
    )


def _split_chunks(text: str, limit: int = _CHUNK_LIMIT) -> list[str]:
    chunks = []
    current = []
    for paragraph in text.split("\n\n"):
        trial = "\n\n".join(current + [paragraph]) if current else paragraph
        if len(trial) <= limit:
            current.append(paragraph)
        elif current:
            chunks.append("\n\n".join(current))
            current = [paragraph]
        else:
            chunks.append(paragraph)
            current = []
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _generate(parts: list, instruction: str) -> str:
    return generate_text([{"role": "user", "parts": parts}], instruction, timeout_ms=60000)


def process_document(
    filename: str, data: bytes, mime_type: str, task: str, target_language: str
) -> str:
    if len(data) > _MAX_FILE_BYTES:
        raise RuntimeError("File terlalu besar (maks 10 MB).")
    if task not in _TASKS:
        raise ValueError("Task tidak valid.")
    instruction = _instruction(task, target_language)
    name = filename.lower()
    if name.endswith((".pdf", ".png", ".jpg", ".jpeg", ".webp")):
        parts = [types.Part.from_bytes(data=data, mime_type=mime_type), {"text": instruction}]
        return _generate(parts, instruction)
    text = extract_text(filename, data)
    if task == "summarize":
        if len(text) > _SUMMARIZE_LIMIT:
            raise RuntimeError("Dokumen terlalu panjang")
        return _generate([{"text": text}], instruction)
    if len(text) > _CHUNK_LIMIT:
        chunks = _split_chunks(text)
        if len(chunks) > _MAX_CHUNKS:
            raise RuntimeError("Dokumen terlalu panjang")
        return "\n\n".join(_generate([{"text": chunk}], instruction) for chunk in chunks)
    return _generate([{"text": text}], instruction)


def to_docx_bytes(title: str, text: str) -> bytes:
    document = Document()
    document.core_properties.title = title
    for line in text.splitlines():
        document.add_paragraph(line)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _split_long_paragraph(paragraph: str, limit: int) -> list[str]:
    pieces = []
    current = ""

    def store(piece: str) -> None:
        nonlocal current
        if piece:
            pieces.append(piece)
        current = ""

    for sentence in re.split(r"(?<=[.!?])\s+", paragraph):
        trial = (current + " " + sentence).strip() if current else sentence
        if len(trial) <= limit:
            current = trial
        else:
            store(current)
            if len(sentence) <= limit:
                current = sentence
            else:
                for word in sentence.split(" "):
                    trial = (current + " " + word).strip() if current else word
                    if len(trial) <= limit:
                        current = trial
                    else:
                        store(current)
                        if len(word) <= limit:
                            current = word
                        else:
                            for i in range(0, len(word), limit):
                                store(word[i : i + limit])
    store(current)
    return pieces


def _split_into_parts(text: str) -> list[str]:
    parts = []
    current = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        if current:
            parts.append("\n\n".join(current))
            current = []
            current_len = 0

    for paragraph in text.split("\n\n"):
        if paragraph == "":
            continue
        para_len = len(paragraph)
        if para_len > _GROQ_PART_LIMIT:
            flush()
            for piece in _split_long_paragraph(paragraph, _GROQ_PART_LIMIT):
                if current and current_len + 2 + len(piece) <= _GROQ_PART_LIMIT:
                    current.append(piece)
                    current_len += 2 + len(piece)
                else:
                    flush()
                    current = [piece]
                    current_len = len(piece)
        else:
            trial = current_len + (2 if current else 0) + para_len
            if trial <= _GROQ_PART_LIMIT:
                current.append(paragraph)
                current_len = trial
            else:
                flush()
                current = [paragraph]
                current_len = para_len
    flush()
    return parts


def process_document_groq(text: str, task: str, target_language: str) -> str:
    if not text or not text.strip():
        raise ValueError("Teks dokumen kosong.")
    if len(text) > _GROQ_MAX_TOTAL:
        raise ValueError("Dokumen terlalu panjang untuk model cadangan")
    if task not in _TASKS:
        raise ValueError("Task tidak valid.")
    parts = _split_into_parts(text)
    if len(parts) > _GROQ_MAX_PARTS:
        raise ValueError("Dokumen terlalu panjang untuk model cadangan")

    hasil = []
    for index, part in enumerate(parts):
        if index > 0:
            time.sleep(_GROQ_PAUSE_DETIK)
        if task == "translate":
            system_prompt = (
                f"Terjemahkan teks persis ke {target_language}. "
                "Balas HANYA hasil terjemahan tanpa penjelasan."
            )
        else:
            system_prompt = (
                f"Rangkum teks berikut secara singkat dalam {target_language}. "
                "Balas HANYA rangkuman tanpa penjelasan."
            )
        hasil.append(_groq_chat(system_prompt, part))

    if task == "summarize" and len(parts) > 1:
        time.sleep(_GROQ_PAUSE_DETIK)
        gabungan = "\n\n".join(hasil)
        system_prompt = (
            f"Gabungkan rangkuman bagian-bagian berikut menjadi satu rangkuman akhir "
            f"dalam {target_language}. Balas HANYA rangkuman akhir tanpa penjelasan."
        )
        hasil = [_groq_chat(system_prompt, gabungan)]

    return "\n\n".join(hasil)