# Contributing
We want to make contributing to this project as easy and transparent as
possible.

## Pull Requests
We actively welcome your pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. If you haven't already, complete the Contributor License Agreement ("CLA").

## Development Setup

```bash
# create venv and install in editable mode
python -m venv .venv && source .venv/bin/activate
pip install -e .[all]
pip install ruff flake8 flake8-bugbear flake8-comprehensions bandit pip-audit pytest pytest-cov

# lint (must pass in CI)
ruff check vizseq tests get_example_data.py
ruff format --check vizseq tests get_example_data.py
flake8 vizseq tests get_example_data.py

# security
bandit -r vizseq -ll -ii
pip-audit --ignore-vuln PYSEC-2026-3740  # NLTK advisory not applicable to VizSeq

# tests (79% coverage)
python -m pytest tests/ -q
pytest tests/ --cov=vizseq --cov-report=term-missing
```

Run `ruff format vizseq tests get_example_data.py` to auto-format before committing.
Formatting is enforced in CI via `ruff format --check` (see `pyproject.toml`
`[tool.ruff.format]` — `quote-style = "single"`).

## Contributor License Agreement ("CLA")
In order to accept your pull request, we need you to submit a CLA. You only need
to do this once to work on any of Facebook's open source projects.

Complete your CLA here: <https://code.facebook.com/cla>

## Issues
We use GitHub issues to track public bugs. Please ensure your description is
clear and has sufficient instructions to be able to reproduce the issue.

## License
By contributing to this project, you agree that your contributions will be licensed
under the LICENSE file in the root directory of this source tree.
