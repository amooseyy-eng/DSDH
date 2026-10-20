"""扫描或清理 data/ 中的纯白图片；默认只报告，传 --apply 才删除。"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops
from tqdm import tqdm


def is_blank(path: Path) -> bool:
    with Image.open(path) as image:
        diff = ImageChops.difference(image.convert("RGB"), Image.new("RGB", image.size, "white"))
        return diff.getbbox() is None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--apply", action="store_true", help="实际删除纯白图片")
    args = parser.parse_args()
    images = [p for p in args.data.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}]
    blanks = []
    for path in tqdm(images, desc="检查图片"):
        try:
            if is_blank(path):
                blanks.append(path)
        except Exception as exc:
            print(f"无法读取 {path}: {exc}")
    print(f"扫描 {len(images)} 张图片，发现 {len(blanks)} 张纯白图片。")
    if args.apply:
        for path in blanks:
            path.unlink()
        print("已删除纯白图片。")
    elif blanks:
        print("当前为预览模式；确认后用 --apply 删除。")


if __name__ == "__main__":
    main()
