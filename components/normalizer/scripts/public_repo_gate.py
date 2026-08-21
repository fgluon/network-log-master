#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
LOCAL_TERMS_FILE = ROOT / ".public-gate-local.txt"

SECRET_PATTERNS = (
    (
        "GitHub fine-grained token",
        re.compile(rb"github_pat_[A-Za-z0-9_]{20,}"),
    ),
    (
        "GitHub classic token",
        re.compile(rb"\bghp_[A-Za-z0-9]{20,}\b"),
    ),
    (
        "private key",
        re.compile(
            rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
        ),
    ),
)

SENSITIVE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
}

SENSITIVE_DIRECTORIES = {
    "secrets",
    "credentials",
}


def git(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def tracked_files() -> list[str]:
    raw = git("ls-files", "-z")
    return [
        item.decode("utf-8")
        for item in raw.split(b"\0")
        if item
    ]


def index_content(path: str) -> bytes:
    prefix = (
        git("rev-parse", "--show-prefix")
        .decode("utf-8")
        .strip()
    )
    return git("show", f":{prefix}{path}")


def local_terms() -> list[str]:
    if not LOCAL_TERMS_FILE.exists():
        return []

    terms = []
    for line in LOCAL_TERMS_FILE.read_text(
        encoding="utf-8"
    ).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def sensitive_path(path: str) -> str | None:
    p = PurePosixPath(path)
    lower_name = p.name.lower()

    if lower_name == ".env" or lower_name.startswith(".env."):
        return "environment credential file"

    if p.suffix.lower() in SENSITIVE_SUFFIXES:
        return f"sensitive file type {p.suffix}"

    for part in p.parts:
        if part.lower() in SENSITIVE_DIRECTORIES:
            return f"sensitive directory {part}"

    return None


def main() -> int:
    problems: list[str] = []
    terms = local_terms()

    files = tracked_files()

    for path in files:
        path_problem = sensitive_path(path)
        if path_problem:
            problems.append(
                f"{path}: {path_problem}"
            )

        content = index_content(path)

        for label, pattern in SECRET_PATTERNS:
            if pattern.search(content):
                problems.append(
                    f"{path}: possible {label}"
                )

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            continue

        folded = text.casefold()

        for term in terms:
            if term.casefold() in folded:
                problems.append(
                    f"{path}: contains local forbidden term "
                    f"{term!r}"
                )

    # The local policy file itself must never become tracked.
    if ".public-gate-local.txt" in files:
        problems.append(
            ".public-gate-local.txt is tracked by Git"
        )

    if problems:
        print("PUBLIC REPO GATE: FAIL")
        print()
        for problem in sorted(set(problems)):
            print(f" - {problem}")
        return 1

    print("PUBLIC REPO GATE: PASS")
    print(f"Scanned {len(files)} tracked files.")
    print(
        f"Loaded {len(terms)} local forbidden terms."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
