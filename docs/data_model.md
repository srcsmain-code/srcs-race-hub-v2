# Race Hub v2 Data Model

## Principle

Race Hub v2 should separate raw submissions from official operational data.

## Main data areas

```text
data/
  championships/
  events/
  drivers/
  teams/
  registrations/
  results/
  classification/
```

## Registrations

Pending registrations are raw form submissions. They are not official until reviewed.

```text
data/registrations/pending/spa_3h_endurance/
```

Approved registrations should be copied into event-specific confirmed entry files.

```text
data/events/spa_3h_endurance/confirmed_entries.json
```

## Driver classification

Rookie is an intake gateway, not a final placement tier.

Placement pathways:

- Premier Pathway
- League Pathway
- Reserve Pathway

## Future database migration

The JSON structure should be kept simple so it can later migrate to:

- GitHub JSON files
- Google Sheets
- Supabase
- Airtable
- Notion
- PostgreSQL
