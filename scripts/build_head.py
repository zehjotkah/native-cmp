"""Assemble the Project Settings → Custom Code snippet into dist/cmp-head.html."""

import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

# This site's own cookieless analytics. It runs outside the CMP and is pushed only to this
# project's Custom Code, never into dist/cmp-head.html (which the generator hands out).
SITE_ONLY_HEAD = """<script
    src="https://insight.nativecmp.com/api/script.js"
    data-site-id="91dc1cbbaee5"
    defer
></script>
"""


def minify_js(path):
    result = subprocess.run(
        ["npx", "--yes", "esbuild@0.25.0", str(path), "--minify", "--target=es2017", "--legal-comments=none"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def minify_css(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([{};,>])\s*", r"\1", text)
    return text.replace(";}", "}").strip()


def build():
    DIST.mkdir(exist_ok=True)
    config = (SRC / "cmp-config.js").read_text().strip()
    css = minify_css((SRC / "cmp-critical.css").read_text())
    engine = minify_js(SRC / "cmp-engine.js")
    version = re.search(r'var VERSION = "([^"]+)"', (SRC / "cmp-engine.js").read_text()).group(1)
    head = "\n".join(
        [
            "<!-- Native CMP: configuration -->",
            "<script>",
            config,
            "</script>",
            f"<style data-cmp-critical>{css}</style>",
            f"<script data-cmp-engine=\"{version}\">{engine}</script>",
            "<!-- Consent-managed head scripts go below this line. Example:",
            '<script type="text/plain" data-cmp-service="google-analytics" data-type="text/javascript" data-src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXX"></script>',
            "-->",
        ]
    )
    (DIST / "cmp-head.html").write_text(head + "\n")
    (ROOT / ".temp").mkdir(exist_ok=True)
    (ROOT / ".temp" / "project-settings.json").write_text(json.dumps({"meta": {"code": SITE_ONLY_HEAD + "\n" + head}}))
    print(f"dist/cmp-head.html {len(head)} bytes")


if __name__ == "__main__":
    build()
