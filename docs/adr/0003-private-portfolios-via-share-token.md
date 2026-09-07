---
status: accepted
---

# Gate Private Portfolios with a share token, not visitor login

An Owner can hold several Portfolios and wants some visible only to selected recruiters, without forcing those recruiters to create an account just to view one page.

A Private Portfolio is guarded by a secret, regenerable Share Token appended to its Slug URL, rather than by requiring the visitor to authenticate. Anyone holding a current Share Link can view it; the Owner can invalidate every previously distributed link at any time by regenerating the token. A request with no token, or a stale one, returns 404 — identical to a nonexistent Slug, so a guess can't confirm a Portfolio exists.

## Considered options

- **Require visitor login**: rejected — contradicts the app's closed-registration model (the Owner is the only account that can exist) and adds friction for the recruiters this feature exists for.
- **Explicit allow-list by email**: rejected — would still require visitors to hold accounts, and the Owner to maintain a list per Portfolio; heavier than the actual need of "I decide who gets which link."
