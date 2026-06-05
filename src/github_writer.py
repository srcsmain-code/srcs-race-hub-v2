from __future__ import annotations

import base64
import json
from typing import Any

import requests
import streamlit as st


def github_configured() -> bool:
    required = ["GITHUB_TOKEN", "GITHUB_REPO_OWNER", "GITHUB_REPO_NAME", "GITHUB_BRANCH"]
    return all(st.secrets.get(key) for key in required)


def commit_json_to_github(path: str, payload: Any, message: str) -> dict:
    """Create or update a JSON file in GitHub using the Contents API.

    This is intentionally isolated from the registration page so we can keep
    local/testing behavior separate from production GitHub writes.
    """
    token = st.secrets["GITHUB_TOKEN"]
    owner = st.secrets["GITHUB_REPO_OWNER"]
    repo = st.secrets["GITHUB_REPO_NAME"]
    branch = st.secrets["GITHUB_BRANCH"]

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    existing = requests.get(url, headers=headers, params={"ref": branch}, timeout=20)
    sha = existing.json().get("sha") if existing.status_code == 200 else None

    encoded_content = base64.b64encode(
        json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
    ).decode("utf-8")

    body = {
        "message": message,
        "content": encoded_content,
        "branch": branch,
    }
    if sha:
        body["sha"] = sha

    response = requests.put(url, headers=headers, json=body, timeout=20)
    response.raise_for_status()
    return response.json()
