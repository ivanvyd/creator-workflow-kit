"""Small non-secret configuration loader for repository-local defaults."""

from __future__ import annotations

import tomllib
from copy import deepcopy

from .paths import repo_root

DEFAULTS: dict[str, dict[str, object]] = {
    "paths": {"runs_dir": "runs"},
    "elevenlabs": {"model_id": "eleven_multilingual_v2"},
    "azure_openai": {
        "writer_deployment_env": "AZURE_OPENAI_WRITER_DEPLOYMENT",
        "reviewer_deployment_env": "AZURE_OPENAI_REVIEWER_DEPLOYMENT",
        "max_input_characters": 24000,
        "max_output_tokens": 800,
    },
}


def load_config() -> dict[str, dict[str, object]]:
    config = deepcopy(DEFAULTS)
    path = repo_root() / "config.toml"
    if not path.exists():
        return config
    parsed = tomllib.loads(path.read_text(encoding="utf-8"))
    for section, values in parsed.items():
        if section in config and isinstance(values, dict):
            config[section].update(values)
    return config
