#!/usr/bin/env python3
"""Write APP_TOKEN into the copy of index.html that gets published.

The page needs the token in it to open connected on a browser it has never
seen — that is what "no setup" means, and there is no way around it: Apps
Script gives a static page no other way to authenticate. What this script
buys is that the token lives in exactly one place, GitHub's secret store,
instead of in the repository and its history forever. The working tree stays
clean, `git log` never learns it, and rotating means changing the secret and
re-running the deploy rather than rewriting history.

What it does NOT buy: the published page still carries the token, so anyone
who can load the Pages URL can use the Sheet behind it and spend the Anthropic
key it proxies. That is inherent to a static page with no server of its own,
and it is the trade the whole feature is.

Reads APP_TOKEN from the environment and never prints it. Exits non-zero if
index.html does not look the way it expects, so a rename upstream fails the
deploy instead of quietly publishing a page that cannot connect.
"""

import json
import os
import re
import sys

ANCHOR = re.compile(r'^const SHEET_TOKEN = "";$', re.M)


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "index.html"

    # Trimmed on the way in, because getToken() in the page trims before it
    # sends. A secret pasted with a trailing newline — the classic way to fill
    # one of these in — would otherwise publish a constant the app can never
    # use as written, and the only symptom would be "Bad or missing token" on
    # a page that looks correctly configured.
    token = os.environ.get("APP_TOKEN", "").strip()

    if not token:
        print("APP_TOKEN is empty — publishing the page unchanged.")
        print("Every browser will ask for the token once, exactly as before.")
        return 0

    with open(path, encoding="utf-8") as fh:
        src = fh.read()

    found = ANCHOR.findall(src)
    if len(found) != 1:
        print(
            f"error: expected exactly one `const SHEET_TOKEN = \"\";` line in {path}, "
            f"found {len(found)}.",
            file=sys.stderr,
        )
        print(
            "The constant was renamed or already filled in. Refusing to guess — "
            "fix this script's anchor rather than shipping a page that cannot connect.",
            file=sys.stderr,
        )
        return 1

    # json.dumps gives a correctly escaped JS string literal, so a quote or a
    # backslash in the token cannot break out of it. That is not sufficient on
    # its own: this literal is going inside an inline <script>, and an HTML
    # parser ends that element at the first literal "</script>" no matter what
    # the JavaScript quoting says. json.dumps leaves "<" alone, so escape the
    # three HTML-significant characters as \uXXXX — valid inside a JS string,
    # and they decode back to the original characters at runtime.
    literal = json.dumps(token)
    for ch, esc in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026")):
        literal = literal.replace(ch, esc)

    # Prove the escaping is lossless before writing anything. JSON string
    # escapes are a subset of JavaScript's, so decoding the literal answers
    # "will the browser see exactly the token?" — a wrong answer here would
    # publish a page that fails to authenticate for a reason nobody could see.
    if json.loads(literal) != token:
        print("error: escaped token does not decode back to the original.", file=sys.stderr)
        return 1

    line = "const SHEET_TOKEN = " + literal + ";"
    out = ANCHOR.sub(lambda _: line, src, count=1)

    if out == src:
        print("error: substitution produced no change.", file=sys.stderr)
        return 1
    if line not in out:
        print("error: token did not survive substitution.", file=sys.stderr)
        return 1

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)

    # Length only. Never the value — workflow logs are readable by anyone who
    # can read the repository.
    print(f"Token injected ({len(token)} chars). Published pages open connected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
