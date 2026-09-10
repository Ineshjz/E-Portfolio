---
status: accepted
---

# Persist a Project Visual as a pasted image URL, not an uploaded file, as an interim step

[ADR-0002](./0002-cloudflare-r2-for-project-visuals.md) commits to storing Project Visuals as real
uploaded files in Cloudflare R2, since Render's ephemeral filesystem cannot hold them. That upload
pipeline (file input, R2 client, signed URLs) does not exist yet. Meanwhile the Generator form
already collects one pasted image URL per Project, and `create_portfolio()` was silently dropping
it — a Portfolio's Projects rendered with no image at all.

We persist the Generator's existing pasted `image_url` as the Project's Visual, with no file upload
and no object storage involved: the Owner supplies a link to an image hosted elsewhere, and the
Visual record stores that string. `show_portfolio()` loads each Project's Visual and the template
renders it when present. At the same time, `video_url` is dropped from `ProjectVisual`,
`ProjectVisualInput`, and the Generator payload: a Project has at most one Visual, and it is an
image (see [CONTEXT.md](../../CONTEXT.md)), so the unused video field only added noise.

This is a deliberate interim step, not a reversal of ADR-0002. Real file upload to R2 stays the
target direction — this decision only makes the already-collected pasted URL durable in the
meantime, instead of continuing to discard it while the R2 pipeline is unbuilt. When upload lands,
`image_url` moves from an Owner-typed link to an R2-hosted one; the Visual's shape (one image URL
per Project, no video) does not need to change.

## Considered options

- **Wait and build the R2 upload pipeline first**: rejected for now — leaves Portfolios shipping
  with no Project images in the meantime, for a gap of unknown length, when the field the form
  already sends only needed to be read and persisted.
- **Keep `video_url` for future use**: rejected — nothing in the Generator, the schema's consumers,
  or [CONTEXT.md](../../CONTEXT.md)'s definition of Visual ("the single uploaded image") anticipates
  a second media type; keeping it would just be persisted dead code.
