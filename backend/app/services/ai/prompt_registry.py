"""Prompt Registry — version-controlled prompt management.

Prompts are stored as YAML files in backend/prompts/ and loaded
on first access with caching. Supports variables, overrides, and validation.
"""

from __future__ import annotations

import re
import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger("careerforge.ai.prompts")

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"

_cache: dict[str, dict] = {}


def load_prompt(category: str, name: str, version: str = "latest") -> dict:
    """Load a prompt from YAML files.

    Args:
        category: Prompt category (resume, ats, jd, reflection)
        name: Prompt name (writer, planner, etc.)
        version: Version string or "latest"

    Returns:
        Dict with keys: system, user, template, variables, params, metadata
    """
    cache_key = f"{category}/{name}:{version}"
    if cache_key in _cache:
        return _cache[cache_key]

    prompt_dir = PROMPTS_DIR / category
    if not prompt_dir.exists():
        raise FileNotFoundError(f"Prompt directory not found: {prompt_dir}")

    # Find the right version file
    if version == "latest":
        candidates = sorted(prompt_dir.glob(f"{name}*.yaml"), reverse=True)
        if not candidates:
            raise FileNotFoundError(f"No prompt found: {category}/{name}")
        prompt_file = candidates[0]
    else:
        prompt_file = prompt_dir / f"{name}_v{version}.yaml"
        if not prompt_file.exists():
            prompt_file = prompt_dir / f"{name}.yaml"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt not found: {category}/{name} v{version}")

    with open(prompt_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    _cache[cache_key] = data
    logger.debug("prompt.loaded", path=str(prompt_file))
    return data


def render_prompt(category: str, name: str, variables: dict[str, Any], version: str = "latest") -> dict[str, str]:
    """Load and render a prompt with variable substitution.

    Returns dict with 'system' and 'user' keys containing rendered text.
    """
    prompt = load_prompt(category, name, version)

    system = prompt.get("system", "")
    user = prompt.get("user", "")
    template = prompt.get("template", "")

    # If there's a template, use it as user prompt
    if template and not user:
        user = template

    # Render variables: {{variable_name}}
    for key, value in variables.items():
        placeholder = "{{" + key + "}}"
        replacement = str(value) if value is not None else ""
        system = system.replace(placeholder, replacement)
        user = user.replace(placeholder, replacement)

    # Validate required variables
    required = prompt.get("variables", [])
    for var in required:
        if var not in variables:
            logger.warning("prompt.missing_variable", prompt=f"{category}/{name}", variable=var)

    return {
        "system": system,
        "user": user,
        "prompt_version": prompt.get("metadata", {}).get("version", "1.0"),
    }


def list_prompts(category: str | None = None) -> list[dict]:
    """List all available prompts."""
    results = []
    search_dir = PROMPTS_DIR / category if category else PROMPTS_DIR
    if not search_dir.exists():
        return results

    for yaml_file in search_dir.rglob("*.yaml"):
        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            rel = yaml_file.relative_to(PROMPTS_DIR)
            results.append({
                "category": rel.parts[0],
                "name": yaml_file.stem,
                "path": str(rel),
                "metadata": data.get("metadata", {}),
                "variables": data.get("variables", []),
            })
        except Exception as e:
            logger.warning("prompt.load.error", path=str(yaml_file), error=str(e))

    return results


def validate_prompt(category: str, name: str) -> dict:
    """Validate a prompt file has required fields."""
    try:
        prompt = load_prompt(category, name)
        issues = []
        if not prompt.get("system") and not prompt.get("template") and not prompt.get("user"):
            issues.append("No prompt content (system, user, or template)")
        if not prompt.get("metadata", {}).get("version"):
            issues.append("Missing metadata.version")
        return {"valid": len(issues) == 0, "issues": issues}
    except FileNotFoundError as e:
        return {"valid": False, "issues": [str(e)]}


def clear_cache() -> None:
    """Clear the prompt cache."""
    _cache.clear()
