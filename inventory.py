#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
import sys

import aztec
import ql800

FORMAT_FULL = 'full'
FORMAT_SMALL = 'small'
FORMAT_TINY = 'tiny'
FORMAT_OPTIONS = [FORMAT_FULL, FORMAT_SMALL, FORMAT_TINY]

def valid_format(format):
    return format in FORMAT_OPTIONS

def create_aztec_label(format, uuid, size_px, label='inventory'):
    if format == FORMAT_FULL:
        return create_full_aztec_label(uuid, label, size_px)
    if format == FORMAT_SMALL:
        return create_small_aztec_label(uuid, label, size_px)
    if format == FORMAT_TINY:
        return create_tiny_aztec_label(uuid)

    print(f"Label format '{format}' not recognized", file=sys.stderr)
    sys.exit(1)


def create_full_aztec_label(uuid, label='inventory', size_px=300):
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
    font_face = ImageFont.truetype("/home/spencer/Documents/fonts/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
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
    aztec_margin = (height_px - aztec_h) // 2
    aztec_x = size_px - 2*aztec_margin - aztec_w
    image.paste(aztec_img, (aztec_x, aztec_margin))
    
    return image.convert('1')


def create_small_aztec_label(uuid, label="inventory", size_px=200):
    """Creates a square image with the Aztec UUID, with plaintext UUID and label bordering it on two sides."""
    aztec_size = (9 * size_px) // 10
    image = Image.new('1', (size_px, size_px), color='white')
    draw = ImageDraw.Draw(image)
    
    aztec.generate(uuid, "aztec.png")
    aztec_img = Image.open("aztec.png", 'r')
    aztec_img = aztec_img.resize((aztec_size, aztec_size))
    image.paste(aztec_img, (0, 0))
    
    font_size = size_px // 10
    font_face = ImageFont.truetype("/home/spencer/Documents/fonts/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
    
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


def ideal_tape_n(width_px, total_px):
    """Returns 4 values: ideal number of copies (based on given width), the edge padding to apply to first and last copy (static), the inner padding to apply to all copies (static), and the width of the cut-line to use between copies (static)."""
    # the printer adds margin. To make the image look square when cut out of the ribbon, we need padding.
    margin_top_px = 30
    margin_side_px = 15
    padding_edge_px = margin_top_px - margin_side_px
    padding_inner_px = margin_top_px
    cut_line_px = 1

    ideal_n = total_px // (width_px+2*padding_inner_px+cut_line_px)
    return (ideal_n, padding_edge_px, padding_inner_px, cut_line_px)


def ideal_width(tape_width_px, n=0):
    _, padding_edge_px, padding_inner_px, cut_line_px = ideal_tape_n(1, tape_width_px)

    total_padding = 2*padding_edge_px + 2*(n-1)*padding_inner_px + (n-1)*cut_line_px
    ideal_width_px = (tape_width_px - total_padding) // n
    print(f"total padding: {total_padding}; ideal width: {ideal_width_px}")
    return ideal_width_px

def composite_continuous(source_img, tape_width_px, n=0):
    """Fills the tape width with as many copies of the source image as will fit. If n is provided and >0, uses that many copies instead of fitting to width."""
    print(f"tape width: {tape_width_px}, n: {n}")

    ideal_n, padding_edge_px, padding_inner_px, cut_line_px = ideal_tape_n(source_img.size[0], tape_width_px)
    if n > ideal_n:
        print(f"Warning: requested n={n} causes image to scale down.", file=sys.stderr)
    if n <= 0:
        n = ideal_n
    print(f"n: {n}")

    # set up the source image and canvas
    image_w, image_h = source_img.size
    print(f"source image size: {image_w}x{image_h}")
    scaled_image_w = ideal_width(tape_width_px, n)
    scaled_image_h = int(scaled_image_w / image_w * image_h)
    print(f"scaled image size: {scaled_image_w}x{scaled_image_h}")
    if int(scaled_image_w) <= 0 or int(scaled_image_h) <= 0:
        print(f"Scaled image size is too small: {scaled_image_w}x{scaled_image_h}", file=sys.stderr)
        sys.exit(1)
    source_img = source_img.resize((scaled_image_w, scaled_image_h))
    source_w, source_h = source_img.size
    canvas = Image.new('1', (tape_width_px, source_h), color='white')
    draw = ImageDraw.Draw(canvas)

    x = padding_edge_px
    while n > 0:
        canvas.paste(source_img, (x, 0))
        x += source_w + padding_inner_px
        if x < tape_width_px:
            draw.line((x, 0, x, source_h), width=cut_line_px, fill='black')
        if x < tape_width_px-source_w:
            x += padding_inner_px
        n -= 1

    return canvas.convert('1')


def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 inventory.py [format] UUID", file=sys.stderr)
        sys.exit(1)

    format = sys.argv[1] if len(sys.argv) > 2 else FORMAT_FULL

    uuid = sys.argv[2] if len(sys.argv) > 2 else sys.argv[1]

    if uuid and not all(c.isalnum() for c in uuid):
        print("Error: UUID must contain only letters and digits", file=sys.stderr)
        sys.exit(1)

    tape_designation = '62'
    tape_width_px, _ = ql800.label_size_px(tape_designation)

    # for tape62, and for the way the composite gutters/divides images:
    n = {FORMAT_FULL: 1, FORMAT_SMALL: 3, FORMAT_TINY: 0}[format]
    size_px = ideal_width(tape_width_px, (n if n > 0 else 1))

    # TODO: use an arg to select the symbology (aztec vs microqr)
    image = create_aztec_label(format, uuid, size_px)

    # TODO: use an arg to select the tape type
    image_composite = composite_continuous(image, tape_width_px, n=n)
    
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
