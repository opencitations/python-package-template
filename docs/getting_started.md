<!--
SPDX-FileCopyrightText: [year] Author Name <author@example.com>

SPDX-License-Identifier: ISC
-->

# Getting started

## Prerequisites

- **UV**: Install from https://docs.astral.sh/uv/getting-started/installation/
- **Python 3.10+**: UV can install Python for you with `uv python install`

## Using the template

1. Click the **Use this template** button on GitHub
2. Select **Create a new repository**
3. Clone your new repository
4. Run the setup script:

```bash
uv run python setup.py
```

The script will ask for:
- Package name
- Description
- Author name and email
- GitHub username/organization
- Whether to include documentation

## After setup

Configure your GitHub repository:

1. **Add PyPI token** (for publishing releases)
   - Create a token at https://pypi.org/manage/account/token/
   - Go to Settings > Secrets and variables > Actions
   - Add a new secret named `PYPI_TOKEN`

2. **Enable GitHub Pages** (if you included documentation)
   - Go to Settings > Pages
   - Set Source to "GitHub Actions"

## Development

```bash
# Install dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest tests/

# Build documentation locally
uv run jupyter-book build --builder dirhtml docs
```
