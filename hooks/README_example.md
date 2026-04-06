# tap-airwallex

A [Singer](https://www.singer.io/) tap that extracts data from the [Airwallex](https://www.airwallex.com/) API. It is built with [hotglue-singer-sdk](https://github.com/hotgluexyz/HotglueSingerSDK) and speaks the standard Singer message protocol on stdout, so you can pair it with any compatible target.

## Features

- Authenticates with Airwallex using API key and client ID (token obtained via the login endpoint).
- Supports **production** and **sandbox** base URLs.
- Incremental sync on `financial_transactions` using `created_at` and the `from_created_at` query parameter.

### Streams

| Stream                 | Endpoint                 | Primary key | Replication key |
| ---------------------- | ------------------------ | ----------- | --------------- |
| `financial_transactions` | `GET` + `/financial_transactions` on the configured API base | `id`        | `created_at`    |

Pagination uses `page_size` / `page_num` when the API returns `has_more`.

## Requirements

- Python **3.7.1**–**3.10** (see `pyproject.toml`).

## Installation

From a clone of this repository:

```bash
pip install poetry
poetry install
```

The `tap-airwallex` console script is available via:

```bash
poetry run tap-airwallex --help
```

## Configuration

| Setting        | Type    | Required | Default | Description |
| -------------- | ------- | -------- | ------- | ----------- |
| `api_key`      | string  | yes      | —       | Airwallex API key (`x-api-key` for login). |
| `client_id`    | string  | yes      | —       | Airwallex client ID (`x-client-id` for login). |
| `is_sandbox`   | boolean | no       | `false` | If `true`, uses the demo API host (`api-demo.airwallex.com`). |

When you pass `--config` with a **file path**, a successful login may update that file with `access_token` and related fields for reuse on the next run.

### Example `config.json`

```json
{
  "api_key": "YOUR_API_KEY",
  "client_id": "YOUR_CLIENT_ID",
  "is_sandbox": false
}
```

Do not commit real credentials. Prefer environment variables or a secrets manager in production.

### Environment-based config

You can load settings from the process environment using `--config=ENV` (the Singer SDK merges env into config). Run `tap-airwallex --about` for the authoritative setting names and types for your installed version.

## Usage

Discover stream catalog:

```bash
tap-airwallex --config config.json --discover > catalog.json
```

Run a sync (with optional state):

```bash
tap-airwallex --config config.json --catalog catalog.json --state state.json
```

Pipe to any Singer target:

```bash
tap-airwallex --config config.json --catalog catalog.json | target-jsonl
```

Inspect built-in settings and stream metadata:

```bash
tap-airwallex --about
```

## API hosts

| Mode        | Base URL |
| ----------- | -------- |
| Production  | `https://api.airwallex.com/api/v1` |
| Sandbox     | `https://api-demo.airwallex.com/api/v1` |

Official API documentation: [Airwallex Docs](https://www.airwallex.com/docs/).

## Development

```bash
poetry install
poetry run pytest
poetry run tap-airwallex --help
```

## License

Apache 2.0 — see `pyproject.toml`.
