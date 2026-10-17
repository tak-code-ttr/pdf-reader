#!/usr/bin/env python3
"""src/pdf-reader.src.html に PDF.js 一式を埋め込み、オフラインで動く単一ファイルを生成する。

  pdf-reader.html … ローカル用（ダブルクリックで開く・iCloud Drive などに置く）
  docs/           … Web公開用（GitHub Pages の公開フォルダ）。PWA 対応でホーム画面に追加してオフライン起動できる

使い方: python3 build.py
"""
import base64
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "pdf-reader.src.html"
OUT = ROOT / "pdf-reader.html"
SITE = ROOT / "docs"
PWA = ROOT / "pwa"
PDFJS = ROOT / "vendor" / "pdfjs-dist-3.11.174"
PWA_FILES = ("manifest.webmanifest", "icon-192.png", "icon-512.png", "apple-touch-icon.png")
PWA_HEAD = (
    '<link rel="manifest" href="manifest.webmanifest">\n'
    '<link rel="icon" href="icon-192.png">\n'
    '<link rel="apple-touch-icon" href="apple-touch-icon.png">'
)


def b64(path):
    return base64.b64encode(path.read_bytes()).decode("ascii")


def script_safe(text, label):
    if "</script" in text.lower():
        raise SystemExit(f"{label} に </script が含まれているため埋め込めません")
    return text


def add_script_hashes(html):
    """CSP の 'unsafe-inline' の代わりに、埋め込んだ各スクリプトのハッシュだけを実行許可する。
    ワーカー本体（type="text/plain"）も、Worker が使えない環境で <script> として実行するため含める。"""
    bodies = re.findall(r"<script(?: [^>]*)?>(.*?)</script>", html, re.S)
    hashes = sorted({"'sha256-" + base64.b64encode(hashlib.sha256(b.encode("utf-8")).digest()).decode() + "'"
                     for b in bodies if b.strip()})
    return html.replace("@@SCRIPT_HASHES@@", " ".join(hashes), 1)


def replace_marker(html, name, content):
    start = html.index(f"<!--@@{name}@@")
    end = html.index("-->", start) + len("-->")
    return html[:start] + content + html[end:]


def main():
    src = SRC.read_text(encoding="utf-8")

    lib = script_safe((PDFJS / "build" / "pdf.min.js").read_text(encoding="utf-8"), "pdf.min.js")
    worker = script_safe((PDFJS / "build" / "pdf.worker.min.js").read_text(encoding="utf-8"), "pdf.worker.min.js")
    assets = {
        "cmaps": {p.stem: b64(p) for p in sorted((PDFJS / "cmaps").glob("*.bcmap"))},
        "fonts": {p.name: b64(p) for p in sorted((PDFJS / "standard_fonts").iterdir())
                  if p.suffix in (".pfb", ".ttf")},
    }
    embed = (
        "<!-- PDF.js 3.11.174 (Apache-2.0, Mozilla Foundation) を埋め込み。build.py で生成 -->\n"
        f"<script>{lib}</script>\n"
        f'<script id="pdfjs-worker" type="text/plain">{worker}</script>\n'
        f'<script id="pdfjs-assets" type="application/json">{json.dumps(assets, separators=(",", ":"))}</script>'
    )
    html = add_script_hashes(replace_marker(src, "PDFJS_EMBED", embed))

    # ローカル用
    OUT.write_text(replace_marker(html, "PWA_HEAD", ""), encoding="utf-8")
    print(f"{OUT.name}: {OUT.stat().st_size / 1e6:.1f} MB "
          f"(cmaps {len(assets['cmaps'])}, fonts {len(assets['fonts'])})")

    # Web公開用
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    site_html = replace_marker(html, "PWA_HEAD", PWA_HEAD)
    (SITE / "index.html").write_text(site_html, encoding="utf-8")
    for name in PWA_FILES:
        shutil.copy2(PWA / name, SITE / name)
    version = hashlib.sha256(
        site_html.encode("utf-8") + b"".join((PWA / n).read_bytes() for n in (*PWA_FILES, "sw.js"))
    ).hexdigest()[:12]
    (SITE / "sw.js").write_text((PWA / "sw.js").read_text(encoding="utf-8").replace("@@VERSION@@", version),
                                encoding="utf-8")
    (SITE / ".nojekyll").write_text("")
    print(f"docs/: index.html ほか（キャッシュ版 {version}）")


if __name__ == "__main__":
    main()
