#!/usr/bin/env python
from pathlib import Path


PACKAGE_PATH = Path("{{cookiecutter.library_name}}")


if __name__ == "__main__":
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
