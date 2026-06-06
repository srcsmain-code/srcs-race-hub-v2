# SRCS Race Hub v2 Architecture

Last updated: 2026-06-05

## Purpose

Race Hub v2 is the operational backbone for SRCS.

It supports public event information, event registration forms, registration-only links, admin review, GitHub-backed JSON storage, future F1 and GT3 events, championship rounds, one-off events, Rookie intake, and lead generation.

The key design principle:

> Race Hub should be event-driven, not hardcoded around one event.

Spa 3H is currently the first working event using this generic model.

## Operating Modes

### Public mode

Default app URL.

Shows the normal public Race Hub menu:

- Home
- Events
- Season 2026
- Standings
- Register Event
- Rookie Intake

### Registration-only mode

URL pattern:

```text
?mode=register&event_id=<event_id>

Example:

?mode=register&event_id=2026_spa_3h_endurance

Used for QR codes, WhatsApp links, Race Square narrowcasting, and direct event campaigns.

### Admin mode

URL pattern:

?mode=admin

Admin mode is password-protected using Streamlit Secrets.

It allows SRCS admin to select an event, view pending registrations, approve or reject registrations, view approved/rejected registrations, and download CSVs.

Main Router

The main entry point is:

app.py

Race Hub uses a custom router rather than Streamlit's automatic pages menu.

This allows different menus for public users, registration-only users, and admin users.

View Files

Views live in:

src/views/

Current views:

home.py
events.py
event_detail.py
register_event.py
admin.py
season_2026.py
standings.py
rookie_intake.py
Event Configs

Event configs live in:

data/events/

Each event has one JSON config file.

Current working event:

data/events/2026_spa_3h_endurance.json

Example event fields:

{
  "event_id": "2026_spa_3h_endurance",
  "event_name": "The SRCS Spa 3-hour Endurance",
  "event_short_name": "Spa 3H",
  "category": "GT3",
  "event_type": "endurance",
  "series_id": null,
  "venue": "Race Square",
  "track": "Spa-Francorchamps",
  "event_date": "2026-08-02",
  "registration_open": true,
  "registration_type": "team_2_driver",
  "cars": ["Porsche", "Mercedes", "Lamborghini", "Ferrari"],
  "public_visible": true,
  "description": "A 3-hour SRCS GT3 endurance event with two drivers per team."
}
Registration Storage

Registrations are stored as JSON files in GitHub.

Principle:

one registration = one JSON file

Folder structure:

data/registrations/
  pending/
    <event_id>/
  approved/
    <event_id>/
  rejected/
    <event_id>/

Example:

data/registrations/pending/2026_spa_3h_endurance/
data/registrations/approved/2026_spa_3h_endurance/
data/registrations/rejected/2026_spa_3h_endurance/
Registration Flow

Current flow:

Driver opens registration link
→ Race Hub loads event config
→ Driver submits form
→ Race Hub writes pending JSON to GitHub
→ Admin reviews registration
→ Admin approves or rejects
→ Approved entries appear on public event page
GitHub Storage

GitHub read/write logic lives in:

src/github_writer.py

It handles reading Streamlit secrets, writing JSON files, reading JSON files, listing registration folders, updating registration status, and approving/rejecting entries.

Streamlit Secrets

Required secrets:

GITHUB_TOKEN = "..."
GITHUB_REPO_OWNER = "srcsmain-code"
GITHUB_REPO_NAME = "srcs-race-hub-v2"
GITHUB_BRANCH = "main"

ADMIN_PASSWORD = "..."

Secrets must never be committed to GitHub.

Current URL Patterns

Public app:

/

Event detail:

?mode=event&event_id=<event_id>

Registration:

?mode=register&event_id=<event_id>

Admin:

?mode=admin
Current Architecture Checkpoint

Race Hub v2 currently has:

Public mode
Registration-only mode
Admin mode
Password-protected admin access
Generic event config model
Generic Events list page
Generic event detail page
Generic event registration page
GitHub-backed registration storage
Admin approval/rejection workflow
Public confirmed entries display
Spa 3H as the first working event
Next Recommended Upgrade

Add registration type handling.

Future registration types:

team_2_driver
single_driver
attendance_confirm
lead_form
team_entry

This will allow Race Hub to support Spa 3H team entries, Rookie intake leads, championship attendance confirmations, one-off single-driver events, and future team-based events.
MD