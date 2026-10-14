#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ ! -d "$root/.venv" ]; then
  python3 -m venv "$root/.venv"
fi
python="$root/.venv/bin/python"
"$python" -m pip install --upgrade pip
"$python" -m pip install -e "$root[dev]"
if [ "${SKIP_CHROMIUM:-0}" != "1" ]; then
  "$python" -m playwright install chromium
fi
if [ ! -f "$root/config.toml" ]; then
  cp "$root/config.example.toml" "$root/config.toml"
  printf '%s\n' 'Created config.toml from the template. It contains environment-variable names only.'
fi
claude_skills="$root/.claude/skills"
expected_skills="$root/.agents/skills"
if [ -e "$claude_skills" ] || [ -L "$claude_skills" ]; then
  current_skills=$("$python" -c 'from pathlib import Path; import sys; print(Path(sys.argv[1]).resolve())' "$claude_skills")
  if [ "$current_skills" != "$expected_skills" ]; then
    printf '%s\n' "Refusing to replace existing $claude_skills" >&2
  fi
else
  mkdir -p "$root/.claude"
  ln -s ../.agents/skills "$claude_skills"
fi
printf '%s\n' 'Ready: .venv/bin/python -m creator_kit doctor'
