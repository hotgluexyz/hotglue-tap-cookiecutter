#!/usr/bin/env python
from pathlib import Path
import shutil


PACKAGE_PATH = Path("{{cookiecutter.library_name}}")


if __name__ == "__main__":
    # Two client templates: http-client.py (REST/GraphQL) → client.py
    target = PACKAGE_PATH / "client.py"
    raw_client_py = PACKAGE_PATH / "http-client.py"
    raw_client_py.rename(target)

    for client_py in PACKAGE_PATH.rglob("*-client.py"):
        client_py.unlink()

    # Select appropriate tap.py based on stream type
    tap_target = PACKAGE_PATH / "tap.py"
    PACKAGE_PATH.joinpath("base-tap.py").rename(tap_target)

    # Clean up remaining tap template files
    for tap_py in PACKAGE_PATH.rglob("*-tap.py"):
        tap_py.unlink()

    if "{{ cookiecutter.stream_type }}" != "REST":
        shutil.rmtree(PACKAGE_PATH.joinpath("schemas"), ignore_errors=True)

    if "{{ cookiecutter.auth_method }}" not in ("OAuth2", "JWT"):
        PACKAGE_PATH.joinpath("auth.py").unlink()

    # Handle license selection
    license_choice = "{{ cookiecutter.license }}"
    if license_choice == "Apache-2.0":
        Path("LICENSE-Apache-2.0").rename("LICENSE")
        Path("LICENSE-MIT").unlink()
    elif license_choice == "MIT":
        Path("LICENSE-MIT").rename("LICENSE")
        Path("LICENSE-Apache-2.0").unlink()
    elif license_choice == "None":
        Path("LICENSE-Apache-2.0").unlink()
        Path("LICENSE-MIT").unlink()

    agent_instructions = "{{ cookiecutter.include_agent_instructions }}"
    if agent_instructions == "CLAUDE.md":
        Path("AGENTS.md").rename("CLAUDE.md")
    elif agent_instructions == "None":
        Path("AGENTS.md").unlink(missing_ok=True)
