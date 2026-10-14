.PHONY: bootstrap demo doctor qc test mcp

bootstrap:
	python -m venv .venv
	.venv/bin/python -m pip install -e '.[dev]'
	.venv/bin/python -m playwright install chromium

demo:
	python -m creator_kit demo

doctor:
	python -m creator_kit doctor

qc:
	python -m creator_kit qc runs/hello-creator/demo.mp4

test:
	python -m pytest

mcp:
	python -m creator_kit mcp
