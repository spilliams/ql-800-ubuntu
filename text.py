#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import ql800
import sys


def create_label(text, tape_width_px):
    """Creates an image of the given text."""
    print(f"tape_width_px {tape_width_px}")
    height_px = tape_width_px // 4
    print(f"height_px {height_px}")
    image = Image.new('1', (tape_width_px, height_px), "white")
    draw = ImageDraw.Draw(image)
    font_size = (0.3 * height_px) // 1
    font_face = ImageFont.truetype("/home/spencer/Documents/fonts/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)

    y_centered = height_px // 2
    x_centered = tape_width_px // 2
    bbox = draw.multiline_textbbox((x_centered, y_centered), text, align='center', anchor='mm', font=font_face, spacing=6)
    text_h = bbox[3] - bbox[1]
    text_w = bbox[2] - bbox[0]
    print(f"font size {font_size}, text width {text_w}, text height {text_h}")
    if text_w > tape_width_px:
        print(f"Error: Text width {text_w} exceeds tape width {tape_width_px}")
        sys.exit(1)
    if text_h > height_px:
        image = Image.new('1', (tape_width_px, text_h), "white")
        draw = ImageDraw.Draw(image)

    draw.multiline_text(
        (x_centered, y_centered),
        text,
        align='center',
        anchor='mm',
        fill='black',
        font=font_face,
        spacing=6
    )
    return image


def main():
    if len(sys.argv) != 1:
        print("Usage: python3 text.py", file=sys.stderr)
        sys.exit(1)

    print("Enter text (blank line to end):")
    sentinel = '' # ends when this string is seen
    text = '\n'.join(iter(input, sentinel))
    
    tape_designation = '62'
    tape_width_px, _ = ql800.label_size_px(tape_designation)
    image = create_label(text, tape_width_px)
    
    filename = ql800.escape_for_filename(f"text_{text}")
    filename = f"output/{filename}.png"
    image.save(filename)
    
    success, message = ql800.print_label(filename, tape_designation)
    if success:
        print(f"✓ {message}")
        sys.exit(0)
    else:
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
