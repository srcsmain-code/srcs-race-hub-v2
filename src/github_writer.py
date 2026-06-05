from __future__ import annotations

import base64
import json
from typing import Any

import requests
import streamlit as st


def get_github_config() -> dict[str, str]:
    return {
        "token": st.secrets.get("GITHUB_TOKEN", ""),
        "owner": st.secrets.get("GITHUB_REPO_OWNER", ""),
        "repo": st.secrets.get("GITHUB_REPO_NAME", ""),
        "branch": st.secrets.get("GITHUB_BRANCH", "main"),
    }


def github_configured() -> bool:
    config = get_github_config()
    return all(
        [
            config["token"],
            config["owner"],
            config["repo"],
            config["branch"],
        ]
    )


def _headers() -> dict[str, str]:
    config = get_github_config()
    return {
        "Authorization": f"Bearer {config['token']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _contents_url(path: str) -> str:
    config = get_github_config()
    clean_path = path.strip("/")
    return (
        f"https://api.github.com/repos/"
        f"{config['owner']}/{config['repo']}/contents/{clean_path}"
    )


def commit_json_to_github(path: str, payload: dict[str, Any], message: str) -> dict[str, Any]:
    if not github_configured():
        raise RuntimeError("GitHub is not configured. Check Streamlit secrets.")

    config = get_github_config()
    url = _contents_url(path)

    json_text = json.dumps(payload, indent=2, ensure_ascii=False)
    encoded_content = base64.b64encode(json_text.encode("utf-8")).decode("utf-8")

    data = {
        "message": message,
        "content": encoded_content,
        "branch": config["branch"],
    }

    response = requests.put(url, headers=_headers(), json=data, timeout=30)

    if response.status_code not in [200, 201]:
        raise RuntimeError(
            f"GitHub write failed: {response.status_code} — {response.text}"
        )

    return response.json()


def list_github_directory(path: str) -> list[dict[str, Any]]:
    if not github_configured():
        raise RuntimeError("GitHub is not configured. Check Streamlit secrets.")

    config = get_github_config()
    url = _contents_url(path)

    response = requests.get(
        url,
        headers=_headers(),
        params={"ref": config["branch"]},
        timeout=30,
    )

    if response.status_code == 404:
        return []

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub directory read failed: {response.status_code} — {response.text}"
        )

    data = response.json()

    if isinstance(data, dict):
        return [data]

    return data


def read_json_from_github(path: str) -> dict[str, Any]:
    if not github_configured():
        raise RuntimeError("GitHub is not configured. Check Streamlit secrets.")

    config = get_github_config()
    url = _contents_url(path)

    response = requests.get(
        url,
        headers=_headers(),
        params={"ref": config["branch"]},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"GitHub file read failed: {response.status_code} — {response.text}"
        )

    data = response.json()
    encoded_content = data.get("content", "")
    decoded = base64.b64decode(encoded_content).decode("utf-8")

    return json.loads(decoded)


def list_pending_spa_3h_registrations() -> list[dict[str, Any]]:
    directory_path = "data/registrations/pending/spa_3h_endurance"
    files = list_github_directory(directory_path)

    registrations: list[dict[str, Any]] = []

    for file_info in files:
        if file_info.get("type") != "file":
            continue

        name = file_info.get("name", "")
        if not name.endswith(".json"):
            continue

        path = file_info.get("path", "")
        if not path:
            continue

        payload = read_json_from_github(path)
        payload["_github_path"] = path
        registrations.append(payload)

    registrations.sort(key=lambda item: item.get("submitted_at_utc", ""), reverse=True)
    return registrations