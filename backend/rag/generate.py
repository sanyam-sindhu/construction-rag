"""Answer generation with numbered, checkable citations.

Backends (LLM_BACKEND):
  openai    – any OpenAI-compatible server: Ollama (default), LM Studio, vLLM, llama.cpp, OpenAI…
  anthropic – Claude, if ANTHROPIC_API_KEY is set
  none      – no LLM: return the top passages as an extractive answer
  auto      – anthropic if a key is set, else openai if the server answers, else none
"""

import json
import os
import re
from collections.abc import Iterator

import httpx

from .config import ANTHROPIC_MODEL, DOCS, LLM_BACKEND, LLM_MODEL, OPENAI_API_KEY, OPENAI_BASE_URL
from .retrieval import Hit

SYSTEM = """You are an assistant for Indian construction professionals. Answer ONLY from the numbered sources provided.

Rules:
- Cite every factual sentence with the source number in square brackets, e.g. [2] or [1][3]. Never cite a number that is not in the list.
- Quote numbers exactly as written in the source: rates with their unit (e.g. "Rs. 161.00 per Mtr."), dimensions, percentages, clause/item numbers.
- For a rate question, name the matching item code and its description, and point out close variants (other sizes/grades) if they are in the sources.
- Sources may come from OCR and contain small recognition errors; read through them sensibly but never invent values.
- Some sources are in Hindi. Answer in the language of the question; when quoting a Hindi source in an English answer, translate it.
- If the sources do not contain the answer, say so plainly and suggest what to search for instead. Do not use outside knowledge.
- Be concise: a direct answer first, then supporting detail as short bullets if needed."""


def format_sources(hits: list[Hit], max_words: int = 230) -> str:
    blocks = []
    for n, h in enumerate(hits, 1):
        c = h.chunk
        words = c.text.split()
        text = " ".join(words[:max_words]) + (" …" if len(words) > max_words else "")
        blocks.append(f"[{n}] {DOCS[c.doc_id]['short']} — {c.ref} (page {c.page_label})\n{text}")
    return "\n\n".join(blocks)


def build_messages(question: str, hits: list[Hit]) -> list[dict]:
    user = f"Sources:\n\n{format_sources(hits)}\n\nQuestion: {question}"
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def resolve_backend() -> str:
    if LLM_BACKEND != "auto":
        return LLM_BACKEND
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    try:
        httpx.get(f"{OPENAI_BASE_URL}/models", timeout=2, headers={"Authorization": f"Bearer {OPENAI_API_KEY}"})
        return "openai"
    except httpx.HTTPError:
        return "none"


def backend_info() -> dict:
    b = resolve_backend()
    model = {"openai": LLM_MODEL, "anthropic": ANTHROPIC_MODEL}.get(b, "extractive (no LLM)")
    return {"backend": b, "model": model}


def stream_answer(question: str, hits: list[Hit]) -> Iterator[str]:
    backend = resolve_backend()
    if not hits:
        yield "I couldn't find anything relevant in the indexed documents."
        return
    if backend == "none":
        yield from _extractive(hits)
    elif backend == "anthropic":
        yield from _anthropic(build_messages(question, hits))
    else:
        yield from _openai(build_messages(question, hits))


def _openai(messages) -> Iterator[str]:
    body = {"model": LLM_MODEL, "messages": messages, "temperature": 0.1, "stream": True}
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    with httpx.stream("POST", f"{OPENAI_BASE_URL}/chat/completions", json=body, headers=headers, timeout=300) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line.startswith("data: ") or line.strip() == "data: [DONE]":
                continue
            delta = json.loads(line[6:])["choices"][0].get("delta", {}).get("content")
            if delta:
                yield delta


def _anthropic(messages) -> Iterator[str]:
    import anthropic

    client = anthropic.Anthropic()
    with client.messages.stream(model=ANTHROPIC_MODEL, max_tokens=1024, system=messages[0]["content"],
                                messages=messages[1:]) as stream:
        yield from stream.text_stream


def _extractive(hits: list[Hit]) -> Iterator[str]:
    yield "No LLM is configured, so here are the most relevant passages:\n\n"
    for n, h in enumerate(hits[:3], 1):
        snippet = " ".join(h.chunk.text.split()[:60])
        yield f"- {snippet} … [{n}]\n"


def cited_numbers(answer: str, n_sources: int) -> list[int]:
    nums = {int(n) for group in re.findall(r"\[(\d{1,2}(?:\s*,\s*\d{1,2})*)\]", answer) for n in group.split(",")}
    return sorted(n for n in nums if 1 <= n <= n_sources)
