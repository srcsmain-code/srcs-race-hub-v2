# SRCS Race Hub v2

Clean rebuild starter for the Sim Racing Championship Series Race Hub.

Race Hub v2 is intended to become the operational backbone for SRCS:

- Public hub: calendar, standings, drivers, teams, event pages.
- Registration hub: endurance entries, rookie intake, attendance confirmations.
- Admin hub: pending submissions, approvals, classifications, event management.
- Data hub: JSON-first structure that can later move to GitHub API, Google Sheets, Supabase, Notion, or another database.

## Current starter features

- Streamlit app shell.
- SRCS-branded theme.
- 2026 season calendar placeholder.
- Standings calculation module.
- Spa 3-hour Endurance event page.
- Spa 3-hour Endurance registration form.
- Pending registration JSON output.
- Admin review page for pending Spa entries.
- GitHub writer helper module prepared but not yet wired into the public form.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
streamlit run app.py
```

## GitHub setup

1. Create a new GitHub repo, for example: `srcs-race-hub-v2`.
2. Upload or push this project.
3. Add Streamlit secrets locally or in Streamlit Cloud.
4. Never commit `.streamlit/secrets.toml`.
5. Use `.streamlit/secrets.example.toml` as the template.

## Data principle

Public forms should only create **pending submissions**.
Official data should only be updated after admin review.

Recommended flow:

```text
Public form submission
  -> data/registrations/pending/...
  -> admin review
  -> approved entry / official event data
  -> public Race Hub display
```

## Next build steps

1. Connect Spa registration form to GitHub file creation.
2. Add admin approve/reject workflow.
3. Import existing Race Hub v1 driver/team/result data.
4. Add August Rookie Intake form.
5. Add classification model page.
6. Add public/private page separation.
