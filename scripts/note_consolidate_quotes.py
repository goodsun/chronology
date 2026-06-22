#!/usr/bin/env python3
"""本文中に残る複数行引用(>)を、note で崩れない形に整える。

連続する「>」行のまとまり（引用ブロック）ごとに:
  - 空の「>」行で区切られた各段落を、それぞれ1行の「>」に集約（全角スペース連結）
  - 段落間は実空行で区切り、note 上で別々の引用枠になるようにする
単一行の引用や、すでに1行に集約済みの「▼」コラムは出力が変わらない。
"""
from pathlib import Path

SEP = "　"  # 全角スペース


def strip_quote(line: str) -> str:
    if line.startswith("> "):
        return line[2:]
    if line.startswith(">"):
        return line[1:].lstrip(" ")
    return line


def process(text: str) -> tuple[str, int]:
    lines = text.split("\n")
    out = []
    changed = 0
    i = 0
    n = len(lines)
    while i < n:
        if not lines[i].startswith(">"):
            out.append(lines[i])
            i += 1
            continue
        # 連続する引用行のまとまりを取得
        run = []
        while i < n and lines[i].startswith(">"):
            run.append(lines[i])
            i += 1
        # 空引用行で段落分割
        segments = []
        cur = []
        for ln in run:
            c = strip_quote(ln)
            if c == "":
                if cur:
                    segments.append(cur)
                    cur = []
            else:
                cur.append(c)
        if cur:
            segments.append(cur)
        # 出力
        rebuilt = []
        for idx, seg in enumerate(segments):
            if idx > 0:
                rebuilt.append("")
            rebuilt.append("> " + SEP.join(seg))
        if rebuilt != run:
            changed += 1
        out.extend(rebuilt)
    return "\n".join(out), changed


def main():
    root = Path(__file__).resolve().parent.parent
    for md in sorted((root / "chapters").glob("*.md")):
        new, changed = process(md.read_text(encoding="utf-8"))
        if changed:
            md.write_text(new, encoding="utf-8")
            print(f"{md.name}: {changed} quote block(s) consolidated")


if __name__ == "__main__":
    main()
