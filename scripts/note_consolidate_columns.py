#!/usr/bin/env python3
"""「▼ …」コラム（連続する複数行の引用ブロック）を、note で崩れない
単一引用ブロック（1行の > ）に集約する。

各コラムは「> **▼ …**」で始まり、直後に続く「> 」行（空行や非引用行が来るまで）
を1つの引用ブロックとみなす。見出し行と本文行を全角スペースで連結し、1行にする。
"""
import re
import sys
from pathlib import Path

SEP = "　"  # 全角スペース


def consolidate(text: str) -> tuple[str, int]:
    lines = text.split("\n")
    out = []
    i = 0
    count = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^> \*\*▼", line):
            # コラム開始。見出し行＋後続の「> 」行を、次のコラム/非引用行まで収集
            block = [line[1:].lstrip(" ")]
            i += 1
            while (
                i < len(lines)
                and lines[i].startswith(">")
                and not re.match(r"^> \*\*▼", lines[i])
            ):
                content = lines[i][1:].lstrip(" ")
                if content:  # 空の引用行はスキップ
                    block.append(content)
                i += 1
            # 直前も引用行なら、note で別ブロックになるよう空行を挟む
            if out and out[-1].startswith(">"):
                out.append("")
            out.append("> " + SEP.join(block))
            count += 1
        else:
            out.append(line)
            i += 1
    return "\n".join(out), count


def main():
    root = Path(__file__).resolve().parent.parent
    total = 0
    for md in sorted((root / "chapters").glob("*.md")):
        original = md.read_text(encoding="utf-8")
        new, n = consolidate(original)
        if n:
            md.write_text(new, encoding="utf-8")
            print(f"{md.name}: {n} columns consolidated")
            total += n
    print(f"--- total: {total}")


if __name__ == "__main__":
    main()
