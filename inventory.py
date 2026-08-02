#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import sys

import aztec
import ql800

def create_aztec_label(format, uuid, label='leuco.net', size_px=200):
    match format:
        case 'full':
            return create_full_aztec_label(uuid, label, size_px)
        case 'small':
            return create_small_aztec_label(uuid, label, size_px)
        case 'tiny':
            return create_tiny_aztec_label(uuid)
        case _:
            print(f"Label format '{format}' not recognized", file=sys.stderr)
            sys.exit(1)


def create_full_aztec_label(uuid, label='leuco.net', size_px=300):
    """Returns an image with the lodestone symbol, some text, and an aztec code of the UUID."""
    height_px = size_px // 4
    image = Image.new('1', (size_px, height_px), color='white')
    draw = ImageDraw.Draw(image)

    # lodestone image on the left
    lodestone_img = Image.open('lodestone_160.png', 'r')
    lodestone_img = lodestone_img.convert('1')
    lodestone_img = lodestone_img.resize((height_px, height_px))
    lodestone_w, lodestone_h = lodestone_img.size
    image.paste(lodestone_img, (0, 0))

    # text in the middle
    font_size = (0.3 * height_px) // 1
    font_face = ImageFont.truetype("/home/spencer/Downloads/fonts/01_Range_Mono_Complete/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
    text = f"{label}\n{uuid}"
    y_centered = height_px // 2
    x_centered = size_px // 2
    draw.multiline_text(
        (x_centered, y_centered),
        text,
        align='center',
        anchor='mm',
        fill='black',
        font=font_face,
        spacing=6
    )
    
    # aztec on the right
    aztec_size = (lodestone_w + lodestone_h) // 2
    aztec.generate(uuid, "aztec.png")
    aztec_img = Image.open("aztec.png", 'r')
    aztec_img = aztec_img.resize((aztec_size, aztec_size))
    aztec_w, aztec_h = aztec_img.size
    print(f"aztec w {aztec_w}, h {aztec_h}, size {aztec_size}")
    aztec_margin = (height_px - aztec_h) // 2
    aztec_x = size_px - 2*aztec_margin - aztec_w
    image.paste(aztec_img, (aztec_x, aztec_margin))
    
    return image.convert('1')


def create_small_aztec_label(uuid, label="leuco.net", size_px=200):
    """Creates a square image with the Aztec UUID, with plaintext UUID and label bordering it on two sides."""
    aztec_size = (9 * size_px) // 10
    image = Image.new('1', (size_px, size_px), color='white')
    draw = ImageDraw.Draw(image)
    
    aztec.generate(uuid, "aztec.png")
    aztec_img = Image.open("aztec.png", 'r')
    aztec_img = aztec_img.resize((aztec_size, aztec_size))
    image.paste(aztec_img, (0, 0))
    
    font_size = size_px // 10
    font_face = ImageFont.truetype("/home/spencer/Downloads/fonts/01_Range_Mono_Complete/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
    
    # uuid below the aztec
    draw.text((aztec_size//2, aztec_size), uuid, fill='black', font=font_face, anchor='ma')
    
    # label to the right, rotated
    bbox = draw.textbbox((0, 0), label, font=font_face)
    label_w = bbox[2] - bbox[0]
    label_h = bbox[3] - bbox[1] + font_size // 2 # not sure why the bbox needs this extra room
    label_img = Image.new('1', (label_w, label_h), color='white')
    label_draw = ImageDraw.Draw(label_img)
    label_draw.text((0, 0), label, fill='black', font=font_face)
    label_img = label_img.rotate(90, expand=1)
    image.paste(label_img, (aztec_size, (aztec_size - label_w) // 2))
    
    # tiny lodestone in the corner
    lodestone_img = Image.open('lodestone_160.png', 'r')
    lodestone_img = lodestone_img.convert('1')
    lodestone_size = size_px - aztec_size
    lodestone_img = lodestone_img.resize((lodestone_size, lodestone_size))
    image.paste(lodestone_img, (aztec_size, aztec_size))

    return image.convert('1')


def create_tiny_aztec_label(uuid):
    """Creates an image of an aztec label, as small as possible"""
    aztec.generate(uuid, "aztec.png")
    aztec_img = Image.open("aztec.png", 'r')
    aztec_w, aztec_h = aztec_img.size
    image = Image.new('1', (aztec_w, aztec_h), color='white')
    image.paste(aztec_img, (0, 0))

    return image.convert('1')


def composite_continuous(source_img, tape_width_px, n=0):
    """Fills the tape width with as many copies of the source image as will fit. If n is provided and >0, uses that many copies instead of fitting to width."""
    # we want at least 30px for the gap between each.
    if n > 0:
        total_gutter = (n-1) * 30
        scaled_image_w = (tape_width_px - total_gutter) / n
        image_w, image_h = source_img.size
        scaled_image_h = scaled_image_w / image_w * image_h
        source_img = source_img.resize((int(scaled_image_w), int(scaled_image_h)))
    else:
        # tape >= source*n + 30*(n-1)
        n = 1
        source_w, _ = source_img.size
        while source_w*(n+1) + 30*(n) <= tape_width_px:
            n += 1

    source_w, source_h = source_img.size
    image = Image.new('1', (tape_width_px, source_h), color='white')
    draw = ImageDraw.Draw(image)

    divisor = n-1 if n>1 else 1
    gutter = (tape_width_px - (source_w*n)) // divisor
    gutter_l = gutter // 2
    gutter_r = gutter - gutter_l

    x = 0
    while n > 0:
        image.paste(source_img, (x, 0))
        x += source_w + gutter_l
        if x < tape_width_px-source_w:
            draw.line((x, 0, x, source_h))
            x += gutter_r
        n -= 1

    return image.convert('1')


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 inventory.py UUID", file=sys.stderr)
        sys.exit(1)
    
    uuid = sys.argv[1]
    if uuid and not all(c.isalnum() for c in uuid):
        print("Error: UUID must contain only letters and digits", file=sys.stderr)
        sys.exit(1)

    tape_designation = '62'
    tape_width_px, _ = ql800.label_size_px(tape_designation)

    # TODO: use an arg to select the format (full, small, tiny)
    # TODO: use an arg to select the symbology (aztec vs microqr)
    format = 'tiny'
    image = create_aztec_label('tiny', f"https://leuco.net/inv/{uuid}")
    
    # TODO: use an arg to select the tape type
    image_composite = composite_continuous(image, tape_width_px)
    
    filename = ql800.escape_for_filename(f"inventory_{format}_{uuid}")
    filename = f"output/{filename}.png"
    image_composite.save(filename)
    print(f"saved label as {filename}")
    
    # TODO: use an arg to determine if we will print
    success, message = ql800.print_label(filename, tape_designation)
    if success:
        print(f"✓ {message}")
        sys.exit(0)
    else:
        print(f"✗ {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
