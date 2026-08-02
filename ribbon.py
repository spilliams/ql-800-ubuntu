#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import ql800
import sys


def create_label(text, tape_width_px):
    """Creates an image of a single line of text. The text will be as tall as the given tape width."""
    font_size = tape_width_px - 20
    font_face = ImageFont.truetype("/home/spencer/Documents/fonts/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
    fake_img = Image.new('1', (1, 1), color='white')
    draw = ImageDraw.Draw(fake_img)
    bbox = draw.textbbox((0, 0), text, font=font_face)
    text_w = bbox[2] - bbox[0]
    #text_h = bbox[3] - bbox[1] + font_size // 2
    
    print(f"font size {font_size}, text width {text_w}, tape width {tape_width_px}")
    image = Image.new('1', (text_w, tape_width_px), color='white')
    label_draw = ImageDraw.Draw(image)
    label_draw.text((0, 0), text, font=font_face, fill='black')
    image = image.rotate(90, expand=True)

    return image.convert('1')


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ribbon.py TEXT", file=sys.stderr)
        sys.exit(1)
    
    text = sys.argv[1]
    
    tape_designation = '62'
    tape_width_px, _ = ql800.label_size_px(tape_designation)
    image = create_label(text, tape_width_px)
    
    filename = ql800.escape_for_filename(f"ribbon_{text}")
    filename = f"output/{filename}.png"
    image.save(filename)
    
    # success, message = ql800.print_label(filename, tape_designation)
    # if success:
    #     print(f"✓ {message}")
    #     sys.exit(0)
    # else:
    #     print(f"Error: {message}", file=sys.stderr)
    #     sys.exit(1)


if __name__ == "__main__":
    main()
