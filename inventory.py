#!/usr/bin/env python3
import subprocess
from PIL import Image, ImageDraw, ImageFont
import sys

import aztec

tape_designation = '62'
tape_width_px = 696 # see https://github.com/matmair/brother_ql-inventree

def create_full_inventory_label(uuid, label='leuco.net'):
    """Creates an image with the lodestone symbol, some text, and an aztec code of the UUID."""
    height_px = 164
    image = Image.new('RGB', (tape_width_px, height_px), color='white')
    draw = ImageDraw.Draw(image)

    # lodestone image on the left
    lodestone_img = Image.open('lodestone_160.png', 'r')
    lodestone_w, lodestone_h = lodestone_img.size
    lodestone_margin = (height_px - lodestone_h) // 2
    image.paste(lodestone_img, (lodestone_margin, lodestone_margin))
    lodestone_img.close()

    # text in the middle
    font_size = 50
    font_face = ImageFont.truetype("/home/spencer/Downloads/fonts/01_Range_Mono_Complete/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
    text = f"{label}\n{uuid}"
    y_centered = height_px // 2 + 2
    x_centered = tape_width_px // 2
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
    aztec_x = tape_width_px - 2*aztec_margin - aztec_w
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
    lodestone_img = Image.open('lodestone_20.png', 'r')
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


def print_label(filename):
    """Requires a CLI provided by brother-ql-inventree."""
    cmd = [
        'brother_ql', '--backend', 'pyusb',
        '--model', 'QL-800',
        '--printer', 'usb://0x04f9:0x209b',
        'print', '-l', f'{tape_designation}', filename
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if 'Total:' in result.stderr:
        return True, "Print successful"
    else:
        return False, f"Print error: {result.stderr.strip()}"


def main():
    try:
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
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
