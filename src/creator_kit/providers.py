"""Opt-in provider calls; all credentials stay in environment variables or ignored files."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .paths import write_json_new
from .config import load_config


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _post_json(url: str, headers: dict[str, str], payload: dict[str, object]) -> bytes:
    request = Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urlopen(request, timeout=90) as response:
            return response.read()
    except HTTPError as error:
        raise RuntimeError(f"provider request failed with HTTP status {error.code}") from None
    except URLError:
        raise RuntimeError("provider request failed before receiving a response") from None


def _duration(path: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("provider returned audio that ffprobe could not read")
    duration = float(result.stdout.strip())
    if duration <= 0:
        raise RuntimeError("provider returned audio with no duration")
    return duration


def synthesize_elevenlabs(job: Path, *, approve_text: bool, model_id: str | None = None, language_code: str | None = None) -> Path:
    if not approve_text:
        raise PermissionError("pass --approve-text after reviewing spoken-script.txt; this call may incur provider charges")
    text = (job / "spoken-script.txt").read_text(encoding="utf-8").strip()
    text_hash = _text_hash(text)
    manifest = job / "tts-manifest.json"
    key = os.environ.get("ELEVENLABS_API_KEY")
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID")
    if not key or not voice_id:
        raise RuntimeError("set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in your environment")
    selected_model = model_id or str(load_config()["elevenlabs"]["model_id"])
    voice_hash = _text_hash(voice_id)
    fingerprint = {"text_sha256": text_hash, "model_id": selected_model, "language_code": language_code, "voice_sha256": voice_hash}
    if manifest.exists():
        prior = json.loads(manifest.read_text(encoding="utf-8"))
        if all(prior.get(key) == value for key, value in fingerprint.items()) and (job / "narration.mp3").exists():
            return job / "narration.mp3"
        raise FileExistsError("a different narration attempt already exists; create a new job slug")
    payload: dict[str, object] = {"text": text, "model_id": selected_model}
    if language_code:
        payload["language_code"] = language_code
    audio = _post_json(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        {"xi-api-key": key, "accept": "audio/mpeg", "content-type": "application/json"},
        payload,
    )
    output = job / "narration.mp3"
    if not audio:
        raise RuntimeError("provider returned an empty audio response")
    output.write_bytes(audio)
    try:
        duration = _duration(output)
    except Exception:
        output.unlink(missing_ok=True)
        raise
    write_json_new(manifest, {"provider": "elevenlabs", **fingerprint, "duration_seconds": duration, "output": output.name})
    return output


def _chat(endpoint: str, deployment: str, key: str, messages: list[dict[str, str]], max_tokens: int) -> str:
    raw = _post_json(
        f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-10-21",
        {"api-key": key, "content-type": "application/json"},
        {"messages": messages, "temperature": 0, "max_tokens": max_tokens},
    )
    response = json.loads(raw)
    content = response.get("choices", [{}])[0].get("message", {}).get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("provider returned no draft content")
    return content


def draft_with_azure(job: Path, source: Path, *, approve_model_call: bool, kind: str = "article") -> Path:
    if not approve_model_call:
        raise PermissionError("pass --approve-model-call after reviewing the source; this call can consume a paid model budget")
    if kind not in {"article", "post"}:
        raise ValueError("kind must be article or post")
    if not source.is_file() or source.stat().st_size > 1_000_000:
        raise ValueError("source must be a regular text file smaller than 1 MB")
    text = source.read_text(encoding="utf-8")
    settings = load_config()["azure_openai"]
    max_input = int(settings["max_input_characters"])
    max_output = int(settings["max_output_tokens"])
    if len(text) > max_input:
        raise ValueError(f"source exceeds the configured {max_input}-character budget")
    source_hash = _text_hash(text)
    manifest = job / "content-manifest.json"
    if manifest.exists():
        prior = json.loads(manifest.read_text(encoding="utf-8"))
        output = job / f"model-{kind}-draft.md"
        if prior.get("source_sha256") == source_hash and prior.get("kind") == kind and output.exists():
            return output
        raise FileExistsError("a different content draft already exists; create a new job slug")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    writer_env = str(settings["writer_deployment_env"])
    reviewer_env = str(settings["reviewer_deployment_env"])
    deployment = os.environ.get(writer_env)
    reviewer_deployment = os.environ.get(reviewer_env) or deployment
    key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not endpoint or not deployment or not reviewer_deployment or not key:
        raise RuntimeError("set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and the configured writer/reviewer deployment variables")
    draft = _chat(endpoint, deployment, key, [{"role": "system", "content": f"Write a factual {kind} using only supplied source. Mark uncertainty. Do not publish."}, {"role": "user", "content": text}], max_output)
    review = _chat(endpoint, reviewer_deployment, key, [{"role": "system", "content": "Review this draft against its supplied source. Return concise factual corrections and missing provenance only. Do not publish."}, {"role": "user", "content": f"SOURCE:\n{text}\n\nDRAFT:\n{draft}"}], max_output)
    output = job / f"model-{kind}-draft.md"
    output.write_text(f"# MODEL {kind.upper()} DRAFT — REVIEW REQUIRED\n\n{draft}\n\n## Model reviewer notes\n\n{review}\n", encoding="utf-8")
    write_json_new(manifest, {"provider": "azure-openai-compatible-chat-completions", "source_sha256": source_hash, "source_name": source.name, "kind": kind, "writer_deployment_env": writer_env, "reviewer_deployment_env": reviewer_env, "max_input_characters": max_input, "max_output_tokens_per_pass": max_output, "status": "draft-only"})
    return output
