from __future__ import annotations

from typing import Any


SUPPORTED_V01_SCOPES = {"user", "repo", "project"}
ALLOWED_VISIBILITY_BY_SCOPE = {
    "user": {"private"},
    "repo": {"private", "team"},
    "project": {"team"},
}


def enforce_write_policy(payload: dict[str, Any]) -> None:
    scope = payload["scope"]
    visibility = payload["visibility"]

    if scope not in SUPPORTED_V01_SCOPES:
        raise ValueError(f"Unsupported scope for v0.1 write policy: {scope}")

    allowed_visibilities = ALLOWED_VISIBILITY_BY_SCOPE[scope]
    if visibility not in allowed_visibilities:
        raise ValueError(
            f"Visibility '{visibility}' is not allowed for scope '{scope}' in v0.1"
        )


def enforce_search_policy(payload: dict[str, Any]) -> None:
    scopes = payload.get("scope") or []
    if not scopes:
        raise ValueError("Search requests must include at least one explicit scope")

    unsupported = sorted(set(scopes) - SUPPORTED_V01_SCOPES)
    if unsupported:
        joined = ", ".join(unsupported)
        raise ValueError(f"Unsupported scopes for v0.1 retrieval: {joined}")


def allowed_visibility_for_scopes(scopes: list[str]) -> list[str]:
    visibilities: set[str] = set()
    for scope in scopes:
        visibilities.update(ALLOWED_VISIBILITY_BY_SCOPE[scope])
    return sorted(visibilities)
