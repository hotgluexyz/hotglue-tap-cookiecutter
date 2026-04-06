"""Stream type classes for {{ cookiecutter.tap_id }}."""

from __future__ import annotations

from hotglue_singer_sdk import typing as th  # JSON Schema typing helpers

from {{ cookiecutter.library_name }}.client import {{ cookiecutter.source_name }}Stream

{#- stream_names: comma-separated labels; stream `name` is normalized to snake_case. #}
{%- if cookiecutter.stream_type == "GraphQL" %}
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


class {{ class_name }}({{ cookiecutter.source_name }}Stream):
    """Stream for ``{{ snake }}``."""

    name = "{{ snake }}"
    # TODO: Replace `id` ` with your actual primary keys.
    primary_keys = ["id"]
    # TODO: Replace with your actual replication key, or set to None if not incremental.
    replication_key = "modified_at"
    schema = th.PropertiesList(
        # TODO: Add the rest of the properties / fields from the API response (types, nested objects, etc.).
        th.Property(
            "id",
            th.StringType,
            description="TODO: Replace with your actual primary key field and type.",
        ),
        th.Property(
            "modified_at",
            th.DateTimeType,
            description="TODO: Replace with your actual replication key field and type (or remove if full-table).",
        ),
    ).to_dict()

    query = """
        # TODO: Use your API's GraphQL root field name (often camelCase) and add the rest of the selection set.
        {{ snake }} {
            id
            modified_at
        }
        """


{%- endif %}
{%- endfor %}
{%- elif cookiecutter.stream_type in ("REST", "Other") %}
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


class {{ class_name }}({{ cookiecutter.source_name }}Stream):
    """Stream for ``{{ snake }}``."""

    name = "{{ snake }}"
    path = "/{{ snake }}"
    # TODO: Replace with your actual primary key column name(s).
    primary_keys = ["id"]
    # TODO: Replace with your actual replication key, or set to None if not incremental.
    replication_key = "modified_at"
    # TODO: Replace with your actual schema.
    schema = th.PropertiesList(
        # TODO: Add the rest of the properties / fields from the API response (types, nested objects, etc.).
        th.Property(
            "id",
            th.StringType,
            description="TODO: Replace with your actual primary key field and type.",
        ),
        th.Property(
            "modified_at",
            th.DateTimeType,
            description="TODO: Replace with your actual replication key field and type (or remove if full-table).",
        ),
    ).to_dict()


{%- endif %}
{%- endfor %}
{%- endif %}
