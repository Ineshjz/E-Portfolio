#!/usr/bin/env python3
"""PreToolUse hook: blocks `git commit` unless the user's own most recent
chat message in this conversation explicitly approved it.

Reads the hook JSON on stdin (see Claude Code hook docs). If tool_input.command
is a `git commit` invocation, walks the conversation transcript (transcript_path)
backwards to find the most recent genuinely human-authored message (skipping
tool-result-carrying turns), and requires that message to contain one of the
approval phrases below. No approval phrase -> hard deny (exit 2). Anything that
can't be verified (missing/unreadable transcript, parse errors) also denies:
the default is "no" unless approval was found.
"""
import json
import re
import sys
import unicodedata

COMMIT_COMMAND_RE = re.compile(r"(^|[;&|(])\s*git\s+commit(\s|$)")

APPROVAL_PHRASES = [
    "valide le commit",
    "valide ce commit",
    "je valide le commit",
    "je valide ce commit",
    "commit valide",
    "validate commit",
    "approve commit",
    "confirm commit",
    "go for commit",
]


def normalize(text: str) -> str:
    """Lowercase and strip accents so 'validé' / 'valide' both match."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.lower()


def block(reason: str) -> None:
    sys.stderr.write(
        "BLOCKED: git commit requires your explicit go-ahead first.\n"
        f"{reason}\n"
        "Do not retry this command. Ask the user, in plain chat, to explicitly "
        "approve the commit (e.g. a reply containing \"je valide le commit\" or "
        "\"validate commit\"), then retry the same command.\n"
    )
    sys.exit(2)


def most_recent_human_text(transcript_path: str) -> str | None:
    """Return the text of the most recent genuinely human-authored message in
    the transcript, or None if the transcript can't be read/parsed.

    A "genuinely human" turn is a JSONL entry with type == "user" that isn't a
    tool-result echo (those are also type == "user" in the Anthropic API sense,
    since tool results are sent back as user-role messages) and isn't a
    subagent sidechain message.
    """
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return None

    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue

        if entry.get("type") != "user" or entry.get("isSidechain"):
            continue

        message = entry.get("message") or {}
        content = message.get("content")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            if any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
                # This "user" turn is just a tool result being echoed back,
                # not the human typing. Keep looking further back.
                continue
            text = "\n".join(
                b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
            )
            return text

        # Unrecognized content shape - nothing to check, but this is still
        # the most recent human turn, so stop here rather than reading an
        # older message as if it were current.
        return ""

    return None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("Could not read the hook input, so approval could not be verified.")
        return

    command = (data.get("tool_input") or {}).get("command", "") or ""
    if not COMMIT_COMMAND_RE.search(command):
        sys.exit(0)  # not a git commit invocation - nothing to check

    transcript_path = data.get("transcript_path")
    if not transcript_path:
        block("No transcript available to verify your approval.")
        return

    text = most_recent_human_text(transcript_path)
    if text is None:
        block("Could not read the conversation transcript to verify your approval.")
        return

    normalized = normalize(text)
    if any(phrase in normalized for phrase in APPROVAL_PHRASES):
        sys.exit(0)

    block("Your most recent chat message did not contain an explicit approval phrase.")


if __name__ == "__main__":
    main()
