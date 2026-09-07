---
status: accepted
---

# Use Neon's free tier for Postgres, decoupled from the app's host

The app deploys on Render's free web service tier, which is stateless and fine to spin down when idle. Render's own free Postgres, however, auto-deletes 30 days after creation (14-day grace period to upgrade before the data is gone for good) — unacceptable for a portfolio meant to stay live through an open-ended job search, and this project has no budget to pay for hosting.

We host the database on Neon's free Postgres tier instead, entirely independent of where the app itself runs. Neon's free compute autosuspends after 5 minutes idle but resumes automatically on the next connection, with no published policy of deleting data for inactivity.

## Considered options

- **Render Postgres (free)**: rejected — hard 30+14-day deletion.
- **Render Postgres (paid)**: rejected — this is a $0 personal project.
- **Supabase (free)**: rejected — free projects pause after 7 days and need a manual dashboard restore, with eventual deletion risk (~90 days, unpublished) if left paused.
