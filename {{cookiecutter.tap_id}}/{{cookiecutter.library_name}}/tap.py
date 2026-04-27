"""{{ cookiecutter.source_name }} tap class."""

from __future__ import annotations
{%- if cookiecutter.auth_method == "OAuth2" %}

from typing import Any
{%- endif %}
{#- Build the list of stream class names once, sorted alphabetically (isort-friendly). -#}
{%- set classes = namespace(items=[]) -%}
{%- for raw in cookiecutter.stream_names.split(",") -%}
{%- set snake = raw | trim | lower | replace(" ", "_") | replace("-", "_") | replace("__", "_") | replace("__", "_") | replace("__", "_") -%}
{%- if snake -%}
{%- set ns = namespace(parts="") -%}
{%- for part in snake.split("_") -%}
{%- if part -%}
{%- set ns.parts = ns.parts ~ (part | capitalize) -%}
{%- endif -%}
{%- endfor -%}
{%- set _ = classes.items.append(ns.parts ~ "Stream") -%}
{%- endif -%}
{%- endfor %}

from hotglue_singer_sdk import Stream, Tap
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers
{%- if cookiecutter.auth_method == "OAuth2" %}
from hotglue_singer_sdk.authenticators import OAuthAuthenticator
{%- endif %}
from typing_extensions import override

{% if cookiecutter.auth_method == "OAuth2" -%}
from {{ cookiecutter.library_name }}.auth import {{ cookiecutter.source_name }}Authenticator
{% endif -%}
from {{ cookiecutter.library_name }}.streams import (
{%- for class_name in classes.items | sort %}
    {{ class_name }},
{%- endfor %}
)

STREAM_TYPES = [
{%- for class_name in classes.items | sort %}
    {{ class_name }},
{%- endfor %}
]


class Tap{{ cookiecutter.source_name }}(Tap):
    """Singer tap for {{ cookiecutter.source_name }}."""

    name = "{{ cookiecutter.tap_id }}"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
            default="2000-01-01T00:00:00Z",
        ),
        th.Property(
            "api_url",
            th.StringType,
            description="Base URL for the {{ cookiecutter.source_name }} API",
            default="{{ cookiecutter.api_base_url }}",
        ),
    {%- if cookiecutter.auth_method in ("OAuth2", "JWT") %}
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="OAuth client ID for the {{ cookiecutter.source_name }} OAuth app",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="OAuth client secret for the {{ cookiecutter.source_name }} OAuth app",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            description="OAuth refresh token for the {{ cookiecutter.source_name }} OAuth app",
        ),
    {%- elif cookiecutter.auth_method == "Basic Auth" %}
        th.Property(
            "username",
            th.StringType,
            required=True,
            description="The {{ cookiecutter.source_name }} username",
        ),
        th.Property(
            "password",
            th.StringType,
            required=True,
            description="The {{ cookiecutter.source_name }} password",
        ),
    {%- else %}
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The API key to authenticate against {{ cookiecutter.source_name }}",
        ),
    {%- endif %}
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
{% if cookiecutter.auth_method == "OAuth2" %}
    @classmethod
    def access_token_support(
        cls,
        connector: Any = None,
    ) -> tuple[type[OAuthAuthenticator], str]:
        """Return the authenticator class and OAuth token endpoint.

        Returns:
            A tuple with the authenticator class and the OAuth token endpoint URL.
        """
        # TODO: replace with the real OAuth token endpoint for your vendor.
        return {{ cookiecutter.source_name }}Authenticator, "{{ cookiecutter.api_base_url }}/oauth/token"
{% endif %}

if __name__ == "__main__":
    Tap{{ cookiecutter.source_name }}.cli()
