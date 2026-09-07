---
status: accepted
---

# Store Project visuals in Cloudflare R2, not on the app's local disk

Project visuals are real uploaded files (not pasted URLs). Render's free web service has an ephemeral filesystem: anything written to local disk is lost on every redeploy, restart, or 15-minute idle spin-down. Saving uploads locally would mean Portfolio images silently disappearing over time.

We store uploaded Visuals in Cloudflare R2 (S3-compatible object storage) and keep only the resulting URL on the Project's Visual record. Storage lifetime is then decoupled entirely from the web service's process lifecycle.

## Considered options

- **Local disk on Render**: rejected — ephemeral, would silently lose images.
- **A paid Render instance with a persistent disk**: rejected — this is a $0 personal project.
- **Supabase Storage**: considered — but the app's Postgres already lives on Neon ([ADR-0001](./0001-neon-for-database-hosting.md)), so R2 keeps storage on its own free account rather than coupling the storage choice to a database vendor it doesn't otherwise use.
