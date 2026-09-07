# E-Portfolio Generator

A tool that turns an Owner's personal and project information into a hosted, shareable Portfolio, built to be shown to recruiters both as a working product and as a codebase.

## Language

### Portfolios & ownership

**Owner**:
The single account that creates and controls Portfolios. Public registration is closed, so exactly one Owner exists at a time; the account is seeded directly rather than self-registered.
_Avoid_: user, account

**Portfolio**:
A single generated e-portfolio instance belonging to the Owner, identified by a permanent Slug. The Owner may hold several Portfolios at once, each built to highlight a different set of skills or projects for a different kind of job search.
_Avoid_: profile, site, page

**Slug**:
The permanent, human-readable identifier of a Portfolio, fixed for life once generated. It is the address used to share a Public Portfolio.
_Avoid_: URL, id, handle

**Generator**:
The form-driven flow that turns Owner-submitted personal and project information into a rendered Portfolio.
_Avoid_: builder, wizard, form

### Visibility & sharing

**Public Portfolio**:
A Portfolio viewable by anyone who has its Slug, without authentication. There is no directory or search of Portfolios — "public" means unguarded, not listed or discoverable.
_Avoid_: listed, indexed

**Private Portfolio**:
A Portfolio viewable only by the Owner (authenticated) or by anyone holding a current Share Link. Never viewable by Slug alone.
_Avoid_: hidden, unlisted (an unlisted Portfolio would still be viewable by Slug alone; a Private one is not)

**Share Link**:
A Private Portfolio's Slug combined with its current Share Token — a secret, regenerable credential the Owner hands directly to a chosen viewer, such as one recruiter. Regenerating the Share Token immediately invalidates every Share Link built from the previous one.
_Avoid_: invite link, access token

### Content

**Project**:
An accomplishment described within a Portfolio — its scope, motivation, context, collaborators, and a reference link — optionally illustrated by one Visual.
_Avoid_: task, experience, entry

**Visual**:
The single uploaded image attached to a Project.
_Avoid_: image, media, attachment
