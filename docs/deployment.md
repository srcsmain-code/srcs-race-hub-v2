# Deployment Notes

## Streamlit Cloud

1. Push repo to GitHub.
2. Create a Streamlit Cloud app from the repo.
3. Set app entry point to `app.py`.
4. Add secrets in Streamlit Cloud settings.

## Required secrets for GitHub write mode

```toml
GITHUB_TOKEN = "..."
GITHUB_REPO_OWNER = "..."
GITHUB_REPO_NAME = "srcs-race-hub-v2"
GITHUB_BRANCH = "main"
```

## Security rule

Do not commit real secrets to GitHub.
