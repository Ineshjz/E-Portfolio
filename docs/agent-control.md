# Agent control

## Instruction: document language

Triggers whenever the agent is about to write or edit a project document
(CONTEXT.md, ADRs, specs, tickets, DIAGNOSIS.md, docs/agent-control.md,
or any file under docs/) — regardless of the language used in the
surrounding conversation, these are written in English. It should NOT
trigger on ordinary conversational replies or on the /grill-with-docs
interview, which follow the language the user is using — tested by
running a French-language conversation with no document requested, and
confirming the agent kept replying in French.

## Enforcement: commit approval

A PreToolUse hook (.claude/hooks/require-commit-approval.py) blocks any
`git commit` command unless the user's most recent message in the
transcript contains an explicit approval phrase (e.g. "je valide le
commit", "commit validé"). Instruction alone was insufficient: despite
being told explicitly to wait for validation before committing, the
agent committed unprompted on multiple occasions during Lab 1 — proof
that this needed a floor, not a request the model could choose to
honor or not.
