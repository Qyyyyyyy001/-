#!/usr/bin/env python3
"""
fetch.py — 通过 Figma REST API 把 manifest.json 中列出的 5 个区块导出为 PNG。

用法:
    export FIGMA_TOKEN=figd_xxxxx   # 在 https://www.figma.com/developers/api#access-tokens 申请
    python3 fetch.py [--scale 2]

输出:
    design-specs/figma-exports/fonts.png
    design-specs/figma-exports/color.png
    design-specs/figma-exports/spacing.png
    design-specs/figma-exports/button.png
    design-specs/figma-exports/checkbox.png
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Pay B 端 Figma sections to PNG")
    parser.add_argument("--scale", type=int, default=2, choices=[1, 2, 3, 4],
                        help="export scale, default 2 (retina)")
    parser.add_argument("--format", default="png", choices=["png", "jpg", "svg", "pdf"],
                        help="export format, default png")
    args = parser.parse_args()

    token = os.environ.get("FIGMA_TOKEN")
    if not token:
        print("ERROR: set FIGMA_TOKEN env var (Figma personal access token)", file=sys.stderr)
        return 1

    here = Path(__file__).resolve().parent
    manifest = json.loads((here / "manifest.json").read_text(encoding="utf-8"))

    file_key = manifest["$source"]["figmaFile"]
    exports = manifest["exports"]
    ids = ",".join(e["nodeId"] for e in exports)

    api = (
        f"https://api.figma.com/v1/images/{file_key}"
        f"?ids={ids}&format={args.format}&scale={args.scale}"
    )
    print(f"→ requesting render URLs for {len(exports)} nodes...")
    req = urllib.request.Request(api, headers={"X-Figma-Token": token})
    with urllib.request.urlopen(req) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    if body.get("err"):
        print(f"Figma API error: {body['err']}", file=sys.stderr)
        return 2

    images = body.get("images", {})
    for entry in exports:
        node_id = entry["nodeId"]
        url = images.get(node_id)
        if not url:
            print(f"  ✗ {entry['name']} ({node_id}) — no URL")
            continue
        out = here / entry["filename"]
        print(f"  ↓ {entry['name']:10} → {out.name}")
        urllib.request.urlretrieve(url, out)

    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
