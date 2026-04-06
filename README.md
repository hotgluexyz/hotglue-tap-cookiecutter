# Hotglue Singer tap — Cookiecutter template

Scaffold a [Singer](https://www.singer.io/) tap that uses Hotglue’s Python SDK: PyPI package [`hotglue-singer-sdk`](https://pypi.org/project/hotglue-singer-sdk/), import name `hotglue_singer_sdk`.

This template mirrors the layout of [Meltano’s tap cookiecutter](https://github.com/meltano/sdk/tree/main/cookiecutter/tap-template) (streams, client, optional `meltano.yml`, CI hooks) but defaults dependencies and imports to **Hotglue**, not `singer-sdk` / `singer_sdk`.

## Usage

Install [Cookiecutter](https://cookiecutter.readthedocs.io/) (for example with [uv](https://docs.astral.sh/uv/)):

```bash
uv tool install cookiecutter
```

Generate a project from GitHub once this repository is published (replace `ORG` and `REPO`):

```bash
cookiecutter gh:ORG/REPO
```

The template lives at the **repository root**, so you do **not** need `--directory`.

From a local clone:

```bash
cookiecutter /path/to/hotglue-tap-cookiecutter
```

## Compatibility note

The generated tap follows the **same patterns as the Meltano SDK tap template** (e.g. `RESTStream`, `GraphQLStream` tap types, `hotglue_singer_sdk.testing`). Align `requires-python`, `hotglue-singer-sdk` version pins, and dependency extras with the **Hotglue Singer SDK build you actually install** (PyPI release vs. git). If your SDK version does not yet expose the same APIs as this template, adjust the generated project after scaffolding.
