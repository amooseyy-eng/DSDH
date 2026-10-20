"""简繁转换、文本清洗、单字/多字频率统计。"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path

from zhconv import convert


def clean_text(text: str, han_only: bool = False) -> str:
    """按实验讲义清理文本；默认保留中英文、数字和常见标点。"""
    if han_only:
        return "".join(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", text))
    text = re.sub(r"[^\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaffA-Za-z0-9，。！？；：、“”‘’（）《》【】,.!?;:'\"()\[\]{}<>—…\- ]", "", text)
    return " ".join(text.split())


def frequency(text: str, ngram: int = 1, han_only: bool = True) -> list[tuple[str, int]]:
    if ngram < 1:
        raise ValueError("ngram 必须大于等于 1")
    text = clean_text(text, han_only=han_only)
    units = [text[i : i + ngram] for i in range(max(0, len(text) - ngram + 1))]
    return Counter(units).most_common()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    conv = sub.add_parser("convert", help="繁简互转")
    conv.add_argument("--direction", choices=("to-simplified", "to-traditional"), required=True)
    conv.add_argument("--text", required=True)

    clean = sub.add_parser("clean", help="清理一段文本")
    clean.add_argument("--text", required=True)
    clean.add_argument("--han-only", action="store_true", help="只保留汉字")

    freq = sub.add_parser("freq", help="统计 data_ch2.txt 的单字或 N 元字频")
    freq.add_argument("--input", type=Path, default=Path("data_ch2.txt"))
    freq.add_argument("--ngram", type=int, default=1)
    freq.add_argument("--top", type=int, default=20)
    freq.add_argument("--all-characters", action="store_true", help="不限制为汉字")
    freq.add_argument("--output", type=Path, help="可选 CSV 输出路径")

    args = parser.parse_args()
    if args.command == "convert":
        target = "zh-hans" if args.direction == "to-simplified" else "zh-hant"
        print(convert(args.text, target))
    elif args.command == "clean":
        print(clean_text(args.text, han_only=args.han_only))
    else:
        text = args.input.read_text(encoding="utf-8-sig")
        rows = frequency(text, args.ngram, han_only=not args.all_characters)
        for rank, (unit, count) in enumerate(rows[: args.top], 1):
            print(f"{rank}\t{unit}\t{count}")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with args.output.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(("rank", "unit", "frequency"))
                writer.writerows((rank, unit, count) for rank, (unit, count) in enumerate(rows, 1))
            print(f"已保存：{args.output}")


if __name__ == "__main__":
    main()
