> **Temporary location.** Per `docs/agents/issue-tracker.md`, specs for this repo belong as GitHub issues, not files under `docs/`. This one is parked here only because `gh`/`api.github.com` was unreachable from this session when it was written. Once connectivity is back, publish it and delete this file — see "Next step" at the bottom.

## Note

Written retroactively. The interview (`/grill-with-docs`, `CONTEXT.md` + `docs/adr/`) and the ticket breakdown (`/to-tickets`, #9–#19) both happened before this spec did. This document reconstructs the intermediate step for the sake of a consistent paper trail — it is not the source the tickets were cut from.

## What's being built

Once a Portfolio exists, the Owner currently has no way to touch it again — no view of its own content, no edit, no delete, no control over who can see it. This body of work adds that: a Portfolio detail page as the one place the Owner manages an existing Portfolio (view, delete, toggle Public/Private with a regenerable Share Link, edit Personal Info, add/edit/remove Projects, replace a Project's Visual), on top of closing the remaining gaps that block actually running this for a real job search — public registration still open, session cookies not hardened, Project Visuals not actually persisting, no deploy target wired up.

## Decisions

- **The detail page is the one foundation surface, not one page per action.** #13 ships it first specifically so visibility, personal-info edit, and project CRUD (#14, #15, #16) can each add a control to it rather than becoming their own standalone pages.
- **Private Portfolios are gated by a regenerable Share Token on the Slug, not visitor login** — [ADR-0003](https://github.com/Ineshjz/E-Portfolio/blob/main/docs/adr/0003-private-portfolios-via-share-token.md). #14 operationalizes this: a stale or missing token 404s identically to a nonexistent Slug, and regenerating the token invalidates every link built from the old one.
- **Registration stays closed; exactly one Owner, seeded directly.** Per `CONTEXT.md`'s definition of Owner ("public registration is closed... the account is seeded directly rather than self-registered"), #10 removes the still-present `POST /register` route and UI rather than leaving it as dead code.
- **Deleting a Portfolio cascades in one transaction.** #13's acceptance criteria (and the shipped implementation) remove `ProjectVisual` → `Project` → `PersonalInfo` → `Portfolio` together, so no orphaned rows survive a delete — consistent with `CONTEXT.md` modeling a Project's Visual and a Portfolio's Projects as owned by, not merely linked to, their parent.
- **A Project carries at most one Visual, and it's an uploaded image — not a pasted URL or a video.** #12 drops the unused `video_url` field while fixing Visual persistence; #17 replaces the pasted-URL input with a real upload. This matches `CONTEXT.md`'s definition of Visual ("the single uploaded image attached to a Project") and its own "avoid: media, attachment" note.
- **Visuals live in Cloudflare R2, not the app's local disk** — [ADR-0002](https://github.com/Ineshjz/E-Portfolio/blob/main/docs/adr/0002-cloudflare-r2-for-project-visuals.md), because Render's free web service has an ephemeral filesystem. #17 and #19 wire this up; #18 builds the replace/remove flow on top of it.
- **The database stays on Neon's free Postgres tier, independent of the app's host** — [ADR-0001](https://github.com/Ineshjz/E-Portfolio/blob/main/docs/adr/0001-neon-for-database-hosting.md), because Render's own free Postgres auto-deletes after 30 days. #19 deploys against this; #9 removes the stale SQLite artifacts left over from before the migration.
- **Sessions get a hard expiry before the app is safe to run publicly.** #11 gives the session cookie `secure`/`samesite`/`max_age` and gives `UserSession` rows a TTL, ahead of #19 putting the app on the open internet.

## Explicitly out of scope

Deduced from what the ticket set (#9–#19) does not touch:

- **No second Owner or public sign-up path.** #10 closes the one that existed; nothing reopens or replaces it. The app's ownership model stays single-Owner.
- **No directory or search of Portfolios.** `CONTEXT.md` is explicit that "public" means unguarded, not listed — no ticket adds a listing or search surface.
- **No visitor authentication for Private Portfolios.** ADR-0003 already rejected both visitor login and an email allow-list; #14 doesn't reopen that question, it only implements the share-token approach the ADR settled on.
- **No edit history or undo.** #15 and #16 overwrite `PersonalInfo` and `Project` rows in place; nothing adds versioning, drafts, or the ability to revert a change.
- **No bulk actions.** No ticket adds duplicating, exporting, or bulk-deleting Portfolios — delete (#13) and edit (#15, #16, #18) all operate on one Portfolio/Project/Visual at a time.
- **No usage analytics.** Nothing tracks views of a Portfolio or of a Share Link — regenerating a token (#14) invalidates prior links, but nothing reports how they were used before that.
- **No change to how a brand-new Portfolio gets created.** The Generator flow itself is untouched except for the persistence bug fix in #12; all of #13–#18 act on a Portfolio that already exists.

## Tickets

Foundational / no dependency:
- #9 — Repo hygiene: fix docs and local dev setup
- #10 — Close public registration and seed the Owner account
- #11 — Harden the session cookie
- #12 — Fix Project-visual persistence and render it
- #13 — Portfolio detail page with delete ✅ *(closed — this spec is written after the fact, following this ticket's implementation)*
- #17 — Switch Project-visual input to real file upload via Cloudflare R2

Built on the detail page (#13):
- #14 — Toggle portfolio visibility and share links
- #15 — Edit personal info
- #16 — Add, edit, and remove Projects

Built on Project CRUD + real uploads (#16, #17):
- #18 — Edit or replace a Project's visual from the detail page

Ships it:
- #19 — Deploy to Render with Neon and Cloudflare R2

## Disposition

Once #9–#19 are all closed, this document is retired — either closed as a GitHub issue, or (if it never made it off disk) deleted from `docs/`. It does not stay around as living documentation either way: any decision here worth remembering past that point belongs in `CONTEXT.md` or a `docs/adr/` record, not in this spec.

## Next step

This should live as a GitHub issue per `docs/agents/issue-tracker.md`, not as a file. Once `gh`/`api.github.com` is reachable again, run:

```
gh issue create --repo Ineshjz/E-Portfolio \
  --title "Spec: Portfolio management, hardening & deployment (tickets #9-#19)" \
  --body-file docs/specs/portfolio-management-hardening-deployment.md
```

Then, on each of #9, #10, #11, #12, #13, #14, #15, #16, #17, #18, #19, add a comment pointing back at the new spec issue number (`<N>`):

```
for n in 9 10 11 12 13 14 15 16 17 18 19; do
  gh issue comment "$n" --repo Ineshjz/E-Portfolio \
    --body "Retroactively linked to spec #<N> (written after tickets, to keep the paper trail consistent — see docs/agents/issue-tracker.md). No change to scope or acceptance criteria."
done
```

Then delete this file (`git rm docs/specs/portfolio-management-hardening-deployment.md`), since the issue is now the source of truth.
