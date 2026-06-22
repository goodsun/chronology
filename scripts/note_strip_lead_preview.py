#!/usr/bin/env python3
"""リード（冒頭の年代・導入）と次章予告の引用(>)を外して通常テキスト化する。

note では複数行引用がレイアウト崩れの原因になるため、
  - 冒頭リード: 最初の「---」より前にある「>」ブロック
  - 次章予告 : 「## 次章予告」または「## 序章への接続」直後の「>」ブロック
の 2 種類だけを対象に「>」を除去する。
段落構造（空行）は保持する。本文中の引用や「▼」コラムには手を触れない。
"""
import re
from pathlib import Path


def strip_quote(line: str) -> str:
    if line == ">":
        return ""
    if line.startswith("> "):
        return line[2:]
    if line.startswith(">"):
        return line[1:]
    return line


def process(text: str) -> tuple[str, int, int]:
    lines = text.split("\n")
    out = []
    passed_first_hr = False
    in_preview = False
    n_lead = n_prev = 0
    for line in lines:
        if not passed_first_hr:
            if line.strip() == "---":
                passed_first_hr = True
                out.append(line)
            elif line.startswith(">"):
                out.append(strip_quote(line))
                n_lead += 1
            else:
                out.append(line)
            continue

        if re.match(r"^## (次章予告|終章予告|序章への接続)", line):
            in_preview = True
            out.append(line)
            continue

        if in_preview:
            if line.startswith(">"):
                out.append(strip_quote(line))
                n_prev += 1
                continue
            if line.strip() == "":
                out.append(line)
                continue
            # 引用でも空行でもない本文（**…へ続く。** など）で予告ブロック終了
            in_preview = False
            out.append(line)
            continue

        out.append(line)
    return "\n".join(out), n_lead, n_prev


def main():
    root = Path(__file__).resolve().parent.parent
    for md in sorted((root / "chapters").glob("*.md")):
        new, n_lead, n_prev = process(md.read_text(encoding="utf-8"))
        if n_lead or n_prev:
            md.write_text(new, encoding="utf-8")
            print(f"{md.name}: lead={n_lead} preview={n_prev}")


if __name__ == "__main__":
    main()
