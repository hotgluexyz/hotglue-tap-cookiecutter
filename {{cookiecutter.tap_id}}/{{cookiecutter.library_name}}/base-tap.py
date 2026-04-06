"""{{ cookiecutter.source_name }} tap class."""

from __future__ import annotations

from hotglue_singer_sdk import Tap, Stream
from hotglue_singer_sdk import typing as th  # JSON schema typing helpers

{%- if cookiecutter.auth_method == "OAuth2" %}
from hotglue_singer_sdk.authenticators import OAuthAuthenticator
from {{ cookiecutter.library_name }}.auth import {{ cookiecutter.source_name }}Authenticator
{%- endif %}

from typing_extensions import override

from {{ cookiecutter.library_name }}.streams import (
{%- for raw in cookiecutter.stream_names.split(",") %}
{%- set snake = raw | trim | lower | replace(" ", "_") | replace("-", "_") | replace("__", "_") | replace("__", "_") | replace("__", "_") %}
{%- if snake %}
{%- set ns = namespace(parts="") %}
{%- for part in snake.split("_") %}
{%- if part %}
{%- set ns.parts = ns.parts ~ (part | capitalize) %}
{%- endif %}
{%- endfor %}
{%- set class_name = ns.parts ~ "Stream" %}
    {{ class_name }},
{%- endif %}
{%- endfor %}
)

STREAM_TYPES = [
{%- for raw in cookiecutter.stream_names.split(",") %}
{%- set snake = raw | trim | lower | replace(" ", "_") | replace("-", "_") | replace("__", "_") | replace("__", "_") | replace("__", "_") %}
{%- if snake %}
{%- set ns = namespace(parts="") %}
{%- for part in snake.split("_") %}
{%- if part %}
{%- set ns.parts = ns.parts ~ (part | capitalize) %}
{%- endif %}
{%- endfor %}
{%- set class_name = ns.parts ~ "Stream" %}
    {{ class_name }},
{%- endif %}
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
            default="2000-01-01T00:00:00Z"
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
            title="Refresh Token",
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
    def access_token_support(self) -> tuple[type[OAuthAuthenticator], str]:
        """Return the access token support for the {{ cookiecutter.source_name }} API.

        Returns:
            A tuple with the access token support class and the auth endpoint.
        """
        return {{ cookiecutter.source_name }}Authenticator, "https://api.mysample.com/oauth/token"
{% endif %}

if __name__ == "__main__":
    Tap{{ cookiecutter.source_name }}.cli()
