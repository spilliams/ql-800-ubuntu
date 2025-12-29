#!/usr/bin/env python3
import subprocess
from PIL import Image, ImageDraw, ImageFont
import sys
import unicodedata
import re

import aztec

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
    
    bw = image.convert('1')
    filename = f"output/inventory_full_{uuid}.png"
    bw.save(filename)
    
    return filename


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

    bw = image.convert('1')
    filename = f"output/inventory_small_{uuid}.png"
    bw.save(filename)
    
    return filename


def create_tiny_aztec_label(uuid):
    """Creates an image of an aztec label, as small as possible"""
    aztec.generate(uuid, "aztec.png")
    aztec_img = Image.open("aztec.png", 'r')
    aztec_w, aztec_h = aztec_img.size
    image = Image.new('1', (aztec_w, aztec_h), color='white')
    image.paste(aztec_img, (0, 0))

    bw = image.convert('1')
    filename = f"output/inventory_tiny_{uuid}.png"
    bw.save(filename)
    
    return filename


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

    bw = image.convert('1')
    source_file_base = source_file.split('/')[-1]
    filename = f"output/continuous_{source_file_base}"
    bw.save(filename)
    
    return filename

def print_label(filename, tape_designation):
    """Requires a CLI provided by brother-ql-inventree."""
    cmd = [
        'brother_ql',
        '--backend', 'pyusb',
        '--printer', 'usb://0x04f9:0x209b',
        '--model', 'QL-800',
        'print',
        '--label', f'{tape_designation}',
        filename
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if 'Total:' in result.stderr:
        return True, "Print successful"
    else:
        return False, f"Print error: {result.stderr.strip()}"


tape_designations = ["12", "12+17", "18", "29", "38", "50", "54", "62", "62red", "102", "103", "104", "17x54", "17x87", "23x23", "29x42", "29x90", "39x90", "39x48", "52x29", "54x29", "60x86", "62x29", "62x100", "102x51", "102x152", "103x164", "d12", "d24", "d58"]
def label_size_px(designation):
    # see https://github.com/matmair/brother_ql-inventree
    tape_sizes = {
        "12":      ( 106,    0),
        "12+17":   ( 306,    0),
        "18":      ( 234,    0),
        "29":      ( 306,    0),
        "38":      ( 413,    0),
        "50":      ( 554,    0),
        "54":      ( 590,    0),
        "62":      ( 696,    0),
        "62red":   ( 696,    0),
        "102":     (1164,    0),
        "103":     (1200,    0),
        "104":     (1200,    0),
        "17x54":   ( 165,  566),
        "17x87":   ( 165,  956),
        "23x23":   ( 202,  202),
        "29x42":   ( 306,  425),
        "29x90":   ( 306,  991),
        "39x90":   ( 413,  991),
        "39x48":   ( 425,  495),
        "52x29":   ( 578,  271),
        "54x29":   ( 598,  271),
        "60x86":   ( 672,  954),
        "62x29":   ( 696,  271),
        "62x100":  ( 696, 1109),
        "102x51":  (1164,  526),
        "102x152": (1164, 1660),
        "103x164": (1200, 1822),
        "d12":     (  94,   94),
        "d24":     ( 236,  236),
        "d58":     ( 618,  618),
    }
    try:
        return tape_sizes[designation]
    except KeyError:
        print(f"Error: tape designation '{designation}' not recognized.")
        sys.exit(1)


def escape_for_filename(value):
    text = str(value)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-_')


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 inventory.py UUID", file=sys.stderr)
        sys.exit(1)
    
    uuid = sys.argv[1]
    if uuid and not all(c.isalnum() for c in uuid):
        print("Error: UUID must contain only letters and digits", file=sys.stderr)
        sys.exit(1)
    
    filename = create_tiny_inventory_label(uuid)
    print(f"saved label as {filename}")
    
    success, message = print_label(filename)
    if success:
        print(f"✓ {message}")
        sys.exit(0)
    else:
        print(f"✗ {message}", file=sys.stderr)
        sys.exit(1)
    


if __name__ == "__main__":
    main()
