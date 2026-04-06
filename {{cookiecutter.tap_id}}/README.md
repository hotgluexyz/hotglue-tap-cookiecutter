# {{ cookiecutter.tap_id }}

A [Singer](https://www.singer.io/) tap that extracts data from **{{ cookiecutter.source_name }}**. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features
{% if cookiecutter.stream_type == "REST" %}
- **REST**-style HTTP streams (see `client.py` / `streams.py`).
{%- elif cookiecutter.stream_type == "GraphQL" %}
- **GraphQL** streams (see `client.py` / `streams.py`).
{%- else %}
- **Custom** stream base (`Stream`); implement record extraction in `client.py` / `streams.py`.
{%- endif -%}
{% if cookiecutter.auth_method == "OAuth2" %}
{%- if cookiecutter.oauth_access_token_via_hg == "yes" %}
- **OAuth2** with access token support via Hotglue (`access_token_support` on the tap).
{%- else %}
- **OAuth2** via custom authenticator in `auth.py`.
{%- endif %}
{%- elif cookiecutter.auth_method == "JWT" %}
- **JWT** authentication (`auth.py`).
{%- elif cookiecutter.auth_method == "Basic Auth" %}
- **Basic** authentication (username / password).
{%- elif cookiecutter.auth_method == "Bearer Token" %}
- **Bearer** token authentication.
{%- elif cookiecutter.auth_method == "API Key" %}
- **API key** authentication.
{%- else %}
- **Custom / N/A** authentication — finish wiring in `client.py` as needed.
{%- endif %}
- Configurable **`api_url`**, **`project_ids`**, and optional **`start_date`**.
- Incremental sync is scaffolded with placeholder **`id`** (primary key) and **`modified_at`** (replication key); replace with real fields per stream in `streams.py`.

### Streams

| Stream | Endpoint / notes | Primary key | Replication key |
| ------ | ---------------- | ----------- | ----------------- |
{%- for raw in cookiecutter.stream_names.split(",") %}
{%- set snake = raw | trim | lower | replace(" ", "_") | replace("-", "_") | replace("__", "_") | replace("__", "_") | replace("__", "_") %}
{%- if snake %}
| `{{ snake }}` | {%- if cookiecutter.stream_type == "REST" %} `GET` + `/{{ snake }}` (default path; TODO: confirm with API) {%- elif cookiecutter.stream_type == "GraphQL" %} GraphQL root field / query in `streams.py` (TODO: align with API) {%- else %} TODO: document how this stream is read {%- endif %} | `id` (TODO) | `modified_at` (TODO) |
{%- endif %}
{%- endfor %}

TODO: Describe pagination, rate limits, and any stream-specific query parameters in this section.

## Requirements

- Python **3.10+** (see `requires-python` in `pyproject.toml`).

## Installation

1. **Clone** this repository and `cd` into the project directory.
2. **Create `config.json`** in the project root with your credentials and settings (see [Configuration](#configuration) for the fields and an example).
3. **Create a virtual environment** and activate it:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows, use `.venv\Scripts\activate` instead of `source .venv/bin/activate`.

4. **Install the package** in editable mode:

```bash
pip install -e .
```

5. **Run the tap** (with the venv still activated):

```bash
{{ cookiecutter.tap_id }} --help
```

## Configuration

| Setting | Type | Required | Default | Description |
| ------- | ---- | -------- | ------- | ----------- |
| `start_date` | string (datetime) | no | `2000-01-01T00:00:00Z` | Earliest record date to sync. |
{%- if cookiecutter.auth_method in ("OAuth2", "JWT") %}
| `client_id` | string | yes | — | OAuth client ID. |
| `client_secret` | string | yes | — | OAuth client secret. |
| `refresh_token` | string | no | — | OAuth refresh token (if applicable). |
{%- elif cookiecutter.auth_method == "Basic Auth" %}
| `username` | string | yes | — | Account username. |
| `password` | string | yes | — | Account password. |
{%- else %}
| `api_key` | string | yes | — | API credential (adjust name/location in code if your API differs). |
{%- endif %}
| `project_ids` | array of strings | yes | — | Project IDs to replicate (template placeholder; rename or remove if not used). |
| `api_url` | string | yes | `https://api.mysample.com` | Base URL for the API. |

Run `{{ cookiecutter.tap_id }} --about` (or `{{ cookiecutter.tap_id }} --about --format=markdown`) for the authoritative schema for your installed version.

### Example `config.json`

```json
{
  "start_date": "2000-01-01T00:00:00Z",
{%- if cookiecutter.auth_method in ("OAuth2", "JWT") %}
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": "",
{%- elif cookiecutter.auth_method == "Basic Auth" %}
  "username": "YOUR_USERNAME",
  "password": "YOUR_PASSWORD",
{%- else %}
  "api_key": "YOUR_API_KEY",
{%- endif %}
  "project_ids": ["project1", "project2"],
  "api_url": "https://api.mysample.com"
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the SDK merges env into config). Env names follow the tap’s setting keys (see `{{ cookiecutter.tap_id }} --about`).

## Usage

With your virtual environment **activated** and `config.json` in place:

Discover stream catalog:

```bash
{{ cookiecutter.tap_id }} --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
{{ cookiecutter.tap_id }} --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
{{ cookiecutter.tap_id }} --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
{{ cookiecutter.tap_id }} --about
```

## API / documentation

TODO: Add your vendor’s base URLs, auth docs, and links (compare to the “API hosts” section in a finished tap README).


## License

{%- if cookiecutter.license == "MIT" %}
MIT — see `LICENSE` and `pyproject.toml`.
{%- elif cookiecutter.license == "Apache-2.0" %}
Apache 2.0 — see `LICENSE` and `pyproject.toml`.
{%- else %}
See repository files; add a `LICENSE` if you distribute this package.
{%- endif %}
