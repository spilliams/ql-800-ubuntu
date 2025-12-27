#!/usr/bin/env python3
import subprocess
from PIL import Image, ImageDraw, ImageFont
import sys

# import code128
# import ean13

tape_width_mm = 62
tape_width_px = 696 # see https://github.com/matmair/brother_ql-inventree

# def is_numeric(barcode):
#     """Returns true if the barcode contains only digits"""
#     return barcode.isdigit()

# def format_barcode_display(barcode_code, is_ean13=False):
#     if is_ean13 and len(barcode_code) == 13:
#         return f"{barcode_code[0]} {barcode_code[1:7]} {barcode_code[7:13]}"
#     return barcode_code

def create_inventory_label(uuid):
    height_px = 165
    image = Image.new('RGB', (tape_width_px, height_px), color='white')
    draw = ImageDraw.Draw(image)
    
    font_size = 44
    # unicode_font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu/UbuntuSans.ttf", font_size)
    unicode_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    font_medium = ImageFont.truetype("/home/spencer/Downloads/fonts/01_Range_Mono_Complete/01 Range Mono Complete/OTF/RangeMono-Medium.otf", font_size)
    # font_medium = ImageFont.truetype("/home/spencer/Downloads/fonts/GortonPerfected-Medium.otf", 44)
    
    text_x_min = 170
    x = text_x_min
    y = 0
    
    lodestone = u"\uD83D"
    # lodestone = u"\uDF53"
    # lodestone = u"\U0001F753"
    # lodestone = "🝓"
    bbox = draw.textbbox((x, y), lodestone, font=unicode_font)
    text_width = bbox[2] - bbox[0]
    draw.text((x, y), lodestone, fill='black', font=unicode_font)
    x += text_width
    
    bbox = draw.textbbox((x, y), " leuco.net", font=font_medium)
    # text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.multiline_text((x, y), " leuco.net", fill='black', font=font_medium)
    x = text_x_min
    y += text_height + 12
    
    bbox = draw.textbbox((x, y), uuid, font=font_medium)
    draw.text((x, y), uuid, fill='black', font=font_medium)

    bw = image.convert('1')
    filename = f"inventory_{uuid}.png"
    bw.save(filename)
    
    return filename


# def create_price_label(product_name, price_euros, barcode_number, footer="", height=300):
#     try:
#         font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
#         
#         font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
#         font_price = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
#         font_website = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
#     except:
#         font_large = ImageFont.load_default()
#         font_medium = ImageFont.load_default()
#         font_small = ImageFont.load_default()
#         font_price = ImageFont.load_default()
#         font_website = ImageFont.load_default()
    
#     margin = 12
#     current_y = margin
    
#     # Traitement du nom du produit
#     max_chars_per_line = 32
#     lines = []
    
#     for line in lines:
#         bbox = draw.textbbox((0, 0), line, font=font_medium)
#         text_width = bbox[2] - bbox[0]
#         x_centered = (width - text_width) // 2
#         draw.text((x_centered, current_y), line, fill='black', font=font_medium)
#         current_y += 24
    
#     current_y += 15
    
#     # Barcode drawing
#     barcode_height = 100
#     module_width = 3 if not use_ean13 else 5
    
#     if use_ean13:
#         # Code-barres EAN-13
#         actual_barcode_width = 113 * module_width
#         base_center = (width - actual_barcode_width) // 2
#         barcode_x = base_center + 35
#         success = ean13.draw_barcode(draw, barcode_x, current_y, actual_barcode_width, barcode_height, barcode_code, module_width)
#     else:
#         # Code-barres Code 128
#         # Width estimation (11 bits per character + start + checksum + stop)
#         estimated_width = (len(barcode_code) + 3) * 11 * module_width
#         barcode_x = (width - estimated_width) // 2
#         success = code128.draw_barcode(draw, barcode_x, current_y, estimated_width, barcode_height, barcode_code, module_width)
    
#     if not success:
#         draw.text((barcode_x, current_y), f"Code: {barcode_code}", fill='black', font=font_small)
    
#     current_y += barcode_height + 5
    
#     # Barcode display
#     formatted_barcode = format_barcode_display(barcode_code, use_ean13)
#     bbox = draw.textbbox((0, 0), formatted_barcode, font=font_small)
#     text_width = bbox[2] - bbox[0]
#     x_centered = (width - text_width) // 2
#     draw.text((x_centered, current_y), formatted_barcode, fill='black', font=font_small)
#     current_y += 30
    
#     # Price
#     price_text = f"{price_euros:.2f} €"
#     bbox = draw.textbbox((0, 0), price_text, font=font_price)
#     text_width = bbox[2] - bbox[0]
#     x_centered = (width - text_width) // 2
#     draw.text((x_centered, current_y), price_text, fill='black', font=font_price)
#     current_y += 50
    
#     # Footer
#     if footer and footer.strip():
#         bbox = draw.textbbox((0, 0), footer, font=font_website)
#         text_width = bbox[2] - bbox[0]
#         x_centered = (width - text_width) // 2
#         draw.text((x_centered, current_y), footer, fill='black', font=font_website)
    
#     # Border
#     draw.rectangle([2, 2, width-2, height-2], outline='black', width=1)

# def print_label(filename):
#     cmd = [
#         'brother_ql', '--backend', 'pyusb',
#         '--model', 'QL-800',
#         '--printer', 'usb://0x04f9:0x209b',
#         'print', '-l', f'{tape_width_mm}', filename
#     ]
    
#     result = subprocess.run(cmd, capture_output=True, text=True)
    
#     if 'Total:' in result.stderr:
#         return True, "Print successful"
#     else:
#         return False, f"Print error: {result.stderr.strip()}"

def main():
    try:
        if len(sys.argv) < 2:
            print("Usage: python3 inventory.py UUID", file=sys.stderr)
            sys.exit(1)
        
        uuid = sys.argv[1]
        if uuid and not all(c.isalnum() for c in uuid):
            print("Error: UUID must contain only letters and digits", file=sys.stderr)
            sys.exit(1)
        
        filename = create_inventory_label(uuid)
        print(f"saved label as {filename}")
        
        # success, message = print_label(filename)
        # if success:
        #     print(f"✓ {message}")
        #     sys.exit(0)
        # else:
        #     print(f"✗ {message}", file=sys.stderr)
        #     sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
