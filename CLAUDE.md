## Agent skills

### Issue tracker

Issues and specs live as GitHub issues in `Ineshjz/E-Portfolio`, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical roles (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Document language

Applies whenever you are about to write or edit any project document: 
CONTEXT.md, ADRs, specs, PR, tickets, DIAGNOSIS.md, docs/agent-control.md, 
or any file under docs/.

- Write these documents in English, regardless of the language used in the conversation around them.
- This does NOT apply to conversational replies to the user, or to the grilling/interview questions asked during /grill-with-docs — those follow the language the user is using.

Done when: the document file itself, read on its own with no 
surrounding chat context, is entirely in English.