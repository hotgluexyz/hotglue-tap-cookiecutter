# AGENTS.md - AI Agent Development Guide for {{ cookiecutter.tap_id }}

{# In the cookiecutter source tree this file is a Jinja template; generating a tap renders it to plain Markdown. #}

This document provides guidance for AI coding agents and developers working on this Singer tap. The **Project Overview** reflects the options used when this project was generated.

## Project Overview

- **Project Type**: Singer Tap
- **Source**: {{ cookiecutter.source_name }}
- **Stream Type**: {{ cookiecutter.stream_type }}
- **Authentication**: {{ cookiecutter.auth_method }}
- **Framework**: Hotglue Singer SDK (hotglue_singer_sdk)

## Architecture

This tap follows the Singer specification and uses the Hotglue Singer SDK (hotglue_singer_sdk) to extract data from {{ cookiecutter.source_name }}.

### Key Components

1. **Tap Class** (`{{ cookiecutter.library_name }}/tap.py`): Main entry point, defines streams and configuration
1. **Client** (`{{ cookiecutter.library_name }}/client.py`): HTTP client, stream base class, and (where applicable) how auth is attached to requests
1. **Streams** (`{{ cookiecutter.library_name }}/streams.py`): Stream classes, schemas (`th.PropertiesList`), and—depending on stream type—`path`, `query`, or custom extraction hooks
   {%- if cookiecutter.auth_method == "OAuth2" %}
1. **Authentication** (`{{ cookiecutter.library_name }}/auth.py`): `{{ cookiecutter.source_name }}Authenticator` subclasses the SDK’s `OAuthAuthenticator` (e.g. `oauth_request_body` for the token endpoint). `tap.py` exposes **`access_token_support()`** so Hotglue can coordinate tokens; `client.py` builds the authenticator via that hook.
   {%- elif cookiecutter.auth_method == "JWT" %}
1. **Authentication** (`{{ cookiecutter.library_name }}/auth.py`): JWT via `{{ cookiecutter.source_name }}Authenticator` (SDK `OAuthJWTAuthenticator`); used from **`client.py`**.
   {%- elif cookiecutter.auth_method == "Custom or N/A" %}
1. **Authentication** (`{{ cookiecutter.library_name }}/auth.py`): Stub or custom logic—finish wiring in **`client.py`** / config as needed.
   {%- endif %}

## Development Guidelines for AI Agents

### Understanding Singer Concepts

Before making changes, ensure you understand these Singer concepts:

- **Streams**: Individual data endpoints (e.g., users, orders, transactions)
- **State**: Tracks incremental sync progress using bookmarks
- **Catalog**: Metadata about available streams and their schemas
- **Records**: Individual data items emitted by the tap
- **Schemas**: JSON Schema definitions for stream data

### Stream type notes (this template)

{% if cookiecutter.stream_type == "REST" %}
- **REST**: Each stream typically sets **`path`** (under `url_base`), **`records_jsonpath`**, and pagination via **`get_next_page_token()`** / URL params in **`client.py`** or overrides on the stream class—match your vendor’s API.
{% elif cookiecutter.stream_type == "GraphQL" %}
- **GraphQL**: Streams define a **`query`** string (selection set / operation) in `streams.py`. Pagination and record shaping depend on the API (e.g. `pageInfo` cursors in the JSON body). Adjust **`records_jsonpath`** and **`get_next_page_token()`** (or GraphQL-specific overrides) on the base stream in **`client.py`** as needed; REST-oriented snippets are still useful when the transport is HTTP JSON.
{% else %}
- **Other / custom**: The scaffold uses a generic **`{{ cookiecutter.stream_type }}Stream`** base. You may need to override sync/request/parsing methods per the Hotglue Singer SDK—do not assume URL `path` + query-param pagination without checking the vendor.
{% endif %}

### Common Tasks

#### Adding a New Stream

1. Add a stream class in `{{ cookiecutter.library_name }}/streams.py` (follow naming: PascalCase + `Stream`, Singer **`name`** in snake_case—consistent with existing streams).
1. Set **`primary_keys`** and **`replication_key`** (use `None` if not incremental).
   {%- if cookiecutter.stream_type == "GraphQL" %}
1. Set **`name`** and a **`query`** that matches your schema and API; confirm how the client sends the GraphQL payload.
   {%- elif cookiecutter.stream_type == "REST" %}
1. Set **`name`** and **`path`** (relative to `url_base` in `client.py`).
   {%- else %}
1. Set **`name`** and wire how data is read (path, payload, or overrides) to match your **`{{ cookiecutter.stream_type }}`** integration.
   {%- endif %}
1. Define **`schema`** with `th.PropertiesList` / `th.Property` (same style as the generated streams).
1. Add the class to **`STREAM_TYPES`** in `tap.py` and to the **`from {{ cookiecutter.library_name }}.streams import (...)`** block (Cookiecutter pre-fills both from **`stream_names`**).

Example (aligned with `streams.py`):

```python
from hotglue_singer_sdk import typing as th

from {{ cookiecutter.library_name }}.client import {{ cookiecutter.source_name }}Stream


class MyNewStream({{ cookiecutter.source_name }}Stream):
    name = "my_new_stream"
    {%- if cookiecutter.stream_type == "GraphQL" %}
    query = """
        myNewResource {
            id
            updatedAt
        }
        """
    {%- elif cookiecutter.stream_type == "REST" %}
    path = "/api/v1/my_resource"
    {%- else %}
    # TODO: Set path, payload, or overrides for your stream type.
    {%- endif %}
    primary_keys = ["id"]
    replication_key = "updated_at"

    schema = th.PropertiesList(
        th.Property("id", th.StringType, description="Primary key"),
        th.Property("name", th.StringType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()
```

#### Briefing an AI agent with `curl` and a sample response

To get a useful update to **`streams.py`**, **`client.py`** (pagination / JSON paths), and—if it is a **new** stream—**`tap.py`** (`STREAM_TYPES` + import), send a message shaped roughly like this:

1. **Goal**: e.g. “Add stream `payouts`” or “Fix schema + pagination on `FinancialTransactionsStream`.”
1. **Request**: Paste the **`curl`** (or HTTP method + path + query) you use. **Redact** tokens, keys, and cookies; placeholders like `REDACTED` are fine.
1. **Response**: Paste a **realistic JSON** body (trim huge arrays to a few items). If the list is nested (e.g. `data.items`), say where records live.
1. **Pagination**: State how the next page is indicated (cursor in JSON, `Link` header, `page` / `offset`, or none).
1. **Incremental sync**: Which field should be the **replication key** (if any), and which field(s) are **primary keys**—or say “full table” if not incremental.
1. **Optional**: Auth quirks (special headers, required query params) if they affect this endpoint.

The agent should align **`name`**, **`path`** (or **`query`** for GraphQL), **`schema`**, **`records_jsonpath`** / **`get_next_page_token()`** in **`{{ cookiecutter.library_name }}/client.py`** when needed, and **`STREAM_TYPES`** + imports in **`tap.py`** for new streams. See **Handling Pagination** and **Adding a New Stream** above.

#### Modifying Authentication

{% if cookiecutter.auth_method == 'API Key' -%}

- Update `authenticator` in client class
- API key should be passed via headers or query parameters
- Configuration defined in `tap.py` config schema
  {% elif cookiecutter.auth_method == 'Bearer Token' -%}
- Token read from the **`api_key`** config property (see `tap.py` / `README.md`; rename in schema and client if your API uses a different setting name)
- Passed via **`BearerTokenAuthenticator`** in **`client.py`** (`Authorization: Bearer …`)
  {% elif cookiecutter.auth_method == 'Basic Auth' -%}
- Username/password in config
- Automatically encoded to base64
  {% elif cookiecutter.auth_method == 'OAuth2' -%}
- **`tap.py`**: Implement **`access_token_support()`** with your authenticator class and vendor token URL (template includes a placeholder URL—replace with the real endpoint).
- **`auth.py`**: `{{ cookiecutter.source_name }}Authenticator` extends `OAuthAuthenticator`; implement **`oauth_request_body`** for the vendor’s token request (grant type, scope, etc.).
- **`client.py`**: OAuth authenticator is created via **`self._tap.access_token_support(self._tap)`**—keep that pattern when adjusting the client.
- **Config** (see `tap.py` / `README.md`): typically `client_id`, `client_secret`, `refresh_token` as applicable; align with Hotglue connector fields when deployed there.
  {% elif cookiecutter.auth_method == 'JWT' -%}
- JWT via `{{ cookiecutter.source_name }}Authenticator` in **`auth.py`** (`OAuthJWTAuthenticator` subclass)
- Wired from **`client.py`** `authenticator`; extend config in **`tap.py`** if the vendor needs extra claims or secrets
  {% elif cookiecutter.auth_method == 'Custom or N/A' -%}
- Finish authentication in **`client.py`** (and **`tap.py`** `config_jsonschema`); use **`auth.py`** only if you add a dedicated authenticator class
  {% endif -%}

#### Handling Pagination

{% if cookiecutter.stream_type == "Other" -%}
This project was generated with stream type **Other**: pagination is not assumed to be REST query-param style. Inspect **`{{ cookiecutter.library_name }}/client.py`** and the SDK’s `{{ cookiecutter.stream_type }}Stream` behavior, then implement paging (or full fetch) in the appropriate hooks. If you end up with HTTP JSON pages, the **`get_next_page_token()`** patterns below still apply once your base stream uses them.
{% else -%}
The scaffold pages over HTTP using **`get_next_page_token()`** on the stream class (see **`{{ cookiecutter.library_name }}/client.py`** for the default implementation using JSONPath / headers). Return the value the SDK should pass on the next request (page number, cursor, URL, etc.); return **`None`** when there is no next page. **GraphQL** APIs often expose cursors inside the JSON body—parse those here and thread the token into the request builder your client uses.

The method signature matches the base stream (roughly: `response`, `previous_token`). Adapt the body to your API.
{% endif -%}

**Next token in the JSON body** (cursor, page number, etc.):

```python
from typing import Any

import requests
from typing_extensions import override

class MyStream({{ cookiecutter.source_name }}Stream):
    @override
    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Any | None:
        body = response.json()
        # TODO: Adjust keys to match your API.
        if not body.get("has_more", False):
            return None
        return body.get("pagination", {}).get("next_cursor")
```

_The snippets below assume the same imports: `from typing import Any`, `import requests`, and `from typing_extensions import override`._

**Next page via `Link` header** (or similar):

```python
@override
def get_next_page_token(
    self,
    response: requests.Response,
    previous_token: Any | None,
) -> Any | None:
    links = getattr(response, "links", None) or {}
    nxt = links.get("next", {}).get("url")
    return nxt  # or parse out ?page=… / cursor if your client expects a token, not a full URL
```

**Numeric page index** (increment each call):

```python
@override
def get_next_page_token(
    self,
    response: requests.Response,
    previous_token: Any | None,
) -> Any | None:
    page = 1 if previous_token is None else int(previous_token) + 1
    data = response.json()
    if page > data.get("total_pages", 1):
        return None
    return page
```

**Single-page / no pagination:**

```python
@override
def get_next_page_token(
    self,
    response: requests.Response,
    previous_token: Any | None,
) -> Any | None:
    return None
```

Wire the token into query params or headers in **`get_url_params()`** (or equivalent) using `next_page_token` so each request uses the value you return here.

#### State and Incremental Sync

- Set `replication_key` to enable incremental sync (e.g., "updated_at")
- Override `get_starting_timestamp()` to set initial sync point
- State automatically managed by SDK
- Access current state via `get_context_state()`

#### Schema Evolution

- Use flexible schemas during development
- Add new properties without breaking changes
- Consider making fields optional when unsure
- Use `th.Property("field", th.StringType)` for basic types
- Nest objects with `th.ObjectType(...)`

### Testing

Run tests to verify your changes (same virtualenv workflow as `README.md`: `python3 -m venv .venv`, activate it, then `pip install -e .`):

```bash
pip install pytest
pytest

# Run a specific test
pytest tests/test_core.py -k test_name
```

### Configuration

Configuration properties are defined in the tap class:

- Required vs optional properties
- Secret properties (passwords, tokens)
- Mark sensitive data with `secret=True` parameter
- Defaults specified in config schema

Example configuration schema:

```python
from hotglue_singer_sdk import typing as th

config_jsonschema = th.PropertiesList(
    th.Property("api_url", th.StringType, required=True),
    th.Property("api_key", th.StringType, required=True, secret=True),
    th.Property("start_date", th.DateTimeType),
).to_dict()
```

Example test with config:

```bash
{{ cookiecutter.tap_id }} --config config.json --discover
{{ cookiecutter.tap_id }} --config config.json --catalog catalog.json
```

### Keeping tap config, docs, and env in sync

Authoritative settings live in **`config_jsonschema`** on the tap class in `{{ cookiecutter.library_name }}/tap.py` (Hotglue Singer SDK). Everything operators and Hotglue jobs read should match that schema.

**When to sync:**

- Adding new configuration properties to the tap
- Removing or renaming existing properties
- Changing property types, defaults, or descriptions
- Marking properties as required or secret

**How to sync (typical flow for this template):**

1. Update `config_jsonschema` in `{{ cookiecutter.library_name }}/tap.py`.
1. Update **`README.md`**: the configuration table, the example `config.json`, and any prose that names settings.
1. Update **`.env.example`** so variable names stay aligned with `{{ cookiecutter.tap_id }} --about` / `--config=ENV` (keys are derived from config property names).
1. If the tap runs on **Hotglue**, align connector or job configuration in the Hotglue product with the same keys and types ([Hotglue documentation](https://docs.hotglue.com)).

Example — adding a new `batch_size` setting:

```python
# {{ cookiecutter.library_name }}/tap.py
config_jsonschema = th.PropertiesList(
    th.Property("api_url", th.StringType, required=True),
    th.Property("api_key", th.StringType, required=True, secret=True),
    th.Property("batch_size", th.IntegerType, default=100),  # New setting
).to_dict()
```

Example snippet for `README.md`’s **Example `config.json`** section:

```json
{
  "api_url": "https://api.example.com",
  "api_key": "YOUR_API_KEY",
  "batch_size": 100
}
```

```bash
# .env.example (prefix matches this tap’s env mapping; see --about)
{{ cookiecutter.tap_id.upper().replace('-', '_') }}_API_URL=https://api.example.com
{{ cookiecutter.tap_id.upper().replace('-', '_') }}_API_KEY=your_api_key_here
{{ cookiecutter.tap_id.upper().replace('-', '_') }}_BATCH_SIZE=100
```

**JSON shape vs SDK types:**

| `th.*` in `config_jsonschema` | Typical JSON in `config.json` |
|-------------------------------|-------------------------------|
| `StringType` | string |
| `IntegerType` | integer |
| `BooleanType` | boolean |
| `NumberType` | number |
| `DateTimeType` | string (ISO-8601 datetime) |
| `ArrayType` | array |
| `ObjectType` | object |

Use `secret=True` in the schema for credentials; document them as sensitive in `README.md` and never commit real values.

**Best practices:**

- Update `tap.py`, `README.md`, and `.env.example` together so CLI, docs, and env-based runs stay consistent.
- Prefer `{{ cookiecutter.tap_id }} --about` (or `--format=markdown`) as the generated reference for your tree.

> **Note:** Target and mapper patterns in the [Hotglue Singer SDK](https://github.com/hotgluexyz/HotglueSingerSDK) follow the same idea: one source of truth for settings in code, reflected everywhere operators look.

### Common Pitfalls

1. **Rate Limiting**: Implement backoff using `RESTStream` built-in retry logic
1. **Large Responses**: Use pagination, don't load entire dataset into memory
1. **Schema Mismatches**: Validate data matches schema, handle null values
1. **State Management**: Don't modify state directly, use SDK methods
1. **Timezone Handling**: Use UTC, parse ISO 8601 datetime strings
1. **Error Handling**: Let SDK handle retries, log warnings for data issues

### SDK Resources

- [Hotglue Singer SDK (GitHub)](https://github.com/hotgluexyz/HotglueSingerSDK)
- [Singer specification](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md) (community reference)
- Stream maps and SDK APIs: installed `hotglue_singer_sdk` package and the HotglueSingerSDK repository

### Best Practices

1. **Logging**: Use `self.logger` for structured logging
1. **Validation**: Validate API responses before emitting records
1. **Documentation**: Update README with new streams and config options
1. **Type Hints**: Add type hints to improve code clarity
1. **Testing**: Write tests for new streams and edge cases
1. **Performance**: Profile slow streams, optimize API calls
1. **Error Messages**: Provide clear, actionable error messages

## File Structure

```
{{ cookiecutter.tap_id }}/
├── {{ cookiecutter.library_name }}/
│   ├── __init__.py
│   ├── tap.py          # Main tap class
│   ├── client.py       # API client
│   └── streams.py      # Stream definitions
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── config.json         # Example configuration
├── pyproject.toml      # Dependencies and metadata
└── README.md          # User documentation
```

## Additional Resources

- Project README: `README.md` (venv, `pip install -e .`, `config.json`, CLI examples)
- Hotglue Singer SDK: https://github.com/hotgluexyz/HotglueSingerSDK
- Hotglue docs: https://docs.hotglue.com
- Singer specification: https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md

## Making Changes

When implementing changes:

1. Understand the existing code structure
1. Follow Singer and SDK patterns
1. Test thoroughly with real API credentials
1. Update documentation and docstrings
1. Ensure backward compatibility when possible
1. Run linting and type checking

## Questions?

If you're uncertain about an implementation:

- Check SDK documentation for similar examples
- Review other Singer taps for patterns
- Test incrementally with small changes
- Validate against the Singer specification

## Bumping the Singer SDK Version

When upgrading the `hotglue-singer-sdk` dependency in `pyproject.toml`, follow these steps to avoid breaking changes:

1. **Check the deprecation guide** before upgrading:
   https://github.com/hotgluexyz/HotglueSingerSDK (check release notes for your version)

   The deprecation page lists APIs scheduled for removal in each release, along with migration instructions. Review the entries for every version between your current version and the target version.

1. **Update the dependency** in `pyproject.toml`:

   ```toml
   [project]
   dependencies = [
       "hotglue-singer-sdk~=X.Y",  # Bump to the new version
   ]
   ```

1. **Reinstall in your virtualenv** and run the full test suite:

   ```bash
   pip install -e .
   pip install pytest
   pytest
   ```

1. **Address deprecation warnings**: Run with warnings enabled to catch anything that will become an error in a future release:

   ```bash
   pytest -W error::DeprecationWarning
   ```

1. **Check the changelog** for any behavioral changes that affect your tap, even if not surfaced by warnings (e.g. pagination, authentication, state handling).

## Reporting SDK Issues

If you encounter a bug or missing feature in the **Hotglue Singer SDK (`hotglue_singer_sdk`)** itself (not in this tap), report it to the [HotglueSingerSDK](https://github.com/hotgluexyz/HotglueSingerSDK) maintainers using their issue tracker.

Before filing, search existing issues to avoid duplicates. Include the SDK version (`{{ cookiecutter.tap_id }} --version` with your venv activated), Python version, and a minimal reproduction case when reporting bugs.
