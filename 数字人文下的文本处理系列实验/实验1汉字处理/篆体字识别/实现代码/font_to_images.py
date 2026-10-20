"""把 TTF/OTF 字体中的汉字渲染为按汉字分类的图片目录。"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm


DEFAULT_START = 19968
DEFAULT_END = 26000


def characters_from_args(args: argparse.Namespace) -> list[str]:
    if args.characters_file:
        chars = args.characters_file.read_text(encoding="utf-8-sig")
        chars = list(dict.fromkeys(ch for ch in chars if not ch.isspace()))
    else:
        chars = [chr(cp) for cp in range(args.start, args.end)]
    return chars[: args.limit] if args.limit else chars


def font_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.suffix.lower() in {".ttf", ".otf", ".ttc"})


def render_one(char: str, font: ImageFont.FreeTypeFont, canvas_size: int) -> Image.Image:
    image = Image.new("RGB", (canvas_size, canvas_size), "white")
    draw = ImageDraw.Draw(image)
    box = draw.textbbox((0, 0), char, font=font)
    width, height = box[2] - box[0], box[3] - box[1]
    if width <= 0 or height <= 0:
        return image
    draw.text(((canvas_size - width) // 2 - box[0], (canvas_size - height) // 2 - box[1]), char, fill="black", font=font)
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts", type=Path, default=Path("ALL-Font"))
    parser.add_argument("--output", type=Path, default=Path("data"))
    parser.add_argument("--characters-file", type=Path)
    parser.add_argument("--start", type=int, default=DEFAULT_START)
    parser.add_argument("--end", type=int, default=DEFAULT_END)
    parser.add_argument("--limit", type=int, default=100, help="默认先生成 100 字；设为 0 生成完整范围")
    parser.add_argument("--image-size", type=int, default=96)
    parser.add_argument("--font-size", type=int, default=76)
    args = parser.parse_args()

    fonts = font_files(args.fonts)
    if not fonts:
        raise SystemExit(f"没有在 {args.fonts} 中找到 TTF/OTF/TTC 字体文件。")
    chars = characters_from_args(args)
    if not chars:
        raise SystemExit("字符集为空。")
    args.output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    total = 0

    for font_path in tqdm(fonts, desc="字体"):
        try:
            cmap_font = TTFont(str(font_path), fontNumber=0, lazy=True)
            cmap = cmap_font.getBestCmap() or {}
            cmap_font.close()
            image_font = ImageFont.truetype(str(font_path), args.font_size)
        except Exception as exc:
            print(f"跳过无法读取的字体 {font_path.name}: {exc}")
            continue

        for char in chars:
            if ord(char) not in cmap:
                continue
            image = render_one(char, image_font, args.image_size)
            class_dir = args.output / char
            class_dir.mkdir(parents=True, exist_ok=True)
            image.save(class_dir / f"{font_path.stem}.png")
            total += 1

    print(f"完成：{len(fonts)} 个字体，{len(chars)} 个目标字，生成 {total} 张图片；耗时 {time.perf_counter() - started:.1f} 秒。")


if __name__ == "__main__":
    main()
