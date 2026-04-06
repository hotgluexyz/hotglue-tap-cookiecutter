"""HTTP API client (REST or GraphQL), including {{ cookiecutter.source_name }}Stream base class."""

from __future__ import annotations

{% if cookiecutter.auth_method in ("OAuth2", "JWT") -%}
from functools import cached_property
{% endif -%}
from typing import Any, Optional

{% if cookiecutter.auth_method  == "API Key" -%}
from hotglue_singer_sdk.authenticators import APIKeyAuthenticator
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import {{ cookiecutter.stream_type }}Stream


{% elif cookiecutter.auth_method  == "Bearer Token" -%}
from hotglue_singer_sdk.authenticators import BearerTokenAuthenticator
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import {{ cookiecutter.stream_type }}Stream


{% elif cookiecutter.auth_method == "Basic Auth" -%}
from requests.auth import HTTPBasicAuth
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import {{ cookiecutter.stream_type }}Stream


{% elif cookiecutter.auth_method == "Custom or N/A" -%}
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import {{ cookiecutter.stream_type }}Stream


{% elif cookiecutter.auth_method == "OAuth2" and cookiecutter.oauth_access_token_via_hg == "yes" -%}
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import {{ cookiecutter.stream_type }}Stream


{% elif cookiecutter.auth_method in ("OAuth2", "JWT") -%}
from hotglue_singer_sdk.helpers.jsonpath import extract_jsonpath
from hotglue_singer_sdk.streams import {{ cookiecutter.stream_type }}Stream

from {{ cookiecutter.library_name }}.auth import {{ cookiecutter.source_name }}Authenticator

{% endif -%}


from typing_extensions import override
import requests
{%- if cookiecutter.auth_method in ("OAuth2", "JWT") %}
from hotglue_singer_sdk.helpers.types import Auth
{%- endif %}


class {{ cookiecutter.source_name }}Stream({{ cookiecutter.stream_type }}Stream):
    """{{ cookiecutter.source_name }} stream class."""

    # Update this value if necessary or override `parse_response`.
    records_jsonpath = "$[*]"

    # Update this value if necessary or override `get_new_paginator`.
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    @override
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        # TODO: hardcode a value here, or retrieve it from self.config
        return "https://api.mysample.com"

{%- if cookiecutter.auth_method == "OAuth2" %}

    @override
    @cached_property
    def authenticator(self) -> Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        {%- if cookiecutter.oauth_access_token_via_hg == "yes" %}
        authenticator_cls, auth_endpoint = self._tap.access_token_support(self._tap)
        return authenticator_cls(self, self.config, auth_endpoint=auth_endpoint)
        {%- else %}
        return {{ cookiecutter.source_name }}Authenticator(
            stream=self,
            config=self.config,
            auth_endpoint="TODO: OAuth Endpoint URL"
        )
        {%- endif %}

{%- elif cookiecutter.auth_method == "JWT" %}

    @override
    @cached_property
    def authenticator(self) -> Auth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return {{ cookiecutter.source_name }}Authenticator(stream=self)

{%- elif cookiecutter.auth_method == "API Key" %}

    @override
    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return APIKeyAuthenticator(
            key="x-api-key",
            value=self.config["api_key"],
            location="header",
        )

{%- elif cookiecutter.auth_method == "Bearer Token" %}

    @override
    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return BearerTokenAuthenticator(stream=self, token=self.config["api_key"])

{%- elif cookiecutter.auth_method == "Basic Auth" %}

    @override
    @property
    def authenticator(self) -> HTTPBasicAuth:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return HTTPBasicAuth(
            username=self.config["username"],
            password=self.config["password"],
        )

{%- endif %}

    @override
    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
{%- if cookiecutter.auth_method not in ("OAuth2", "JWT") %}
        # If not using an authenticator, you may also provide inline auth headers:
        # headers["Private-Token"] = self.config.get("api_key")
{%- endif %}
        return {}

    def get_next_page_token(
        self,
        response: requests.Response,
        previous_token: Any | None,
    ) -> Optional[Any]:
        """Return token identifying next page or None if all records have been read.

        Args:
            response: A raw `requests.Response`_ object.
            previous_token: Previous pagination reference.

        Returns:
            Reference value to retrieve next page.

        .. _requests.Response:
            https://requests.readthedocs.io/en/latest/api/#requests.Response
        """
        if self.next_page_token_jsonpath:
            all_matches = extract_jsonpath(
                self.next_page_token_jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)
            next_page_token = first_match
        else:
            next_page_token = response.headers.get("X-Next-Page", None)

        return next_page_token

    @override
    def get_url_params(
        self,
        context: Optional[dict],
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    @override
    def prepare_request_payload(
        self,
        context: Optional[dict],
        next_page_token: Any | None,
    ) -> dict | None:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary with the JSON body for a POST requests.
        """
        # TODO: Delete this method if no payload is required. (Most REST APIs.)
        return None

    @override
    def post_process(
        self,
        row: dict,
        context: Optional[dict] = None,
    ) -> dict | None:
        """As needed, append or transform raw data to match expected structure.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        # TODO: Delete this method if not needed.
        return row
