#!/usr/bin/env python3
import subprocess
from PIL import Image, ImageDraw, ImageFont
import sys

import code128
import ean13

def is_numeric(barcode):
    """Vérifie si le code-barres ne contient que des chiffres"""
    return barcode.isdigit()

def format_barcode_display(barcode_code, is_ean13=False):
    """Formate l'affichage du code-barres"""
    if is_ean13 and len(barcode_code) == 13:
        return f"{barcode_code[0]} {barcode_code[1:7]} {barcode_code[7:13]}"
    return barcode_code

def create_price_label(product_name, price_euros, barcode_number, footer="", height=300):
    width = 696
    
    # Détermine le type de code-barres à générer
    use_ean13 = False
    
    if barcode_number is None or barcode_number == "":
        # Génère un code aléatoire basé sur le type demandé
        barcode_code = code128.generate_internal()
        use_ean13 = False
    else:
        if is_numeric(barcode_number):
            # Code numérique - utilise EAN-13 si possible
            if len(barcode_number) == 12:
                barcode_code = barcode_number + ean13.calculate_checksum(barcode_number)
                use_ean13 = True
            elif len(barcode_number) == 13:
                barcode_code = barcode_number
                use_ean13 = True
            else:
                # Code numérique mais pas de la bonne longueur pour EAN-13
                barcode_code = barcode_number
                use_ean13 = False
        else:
            # Code alphanumérique - utilise Code 128
            barcode_code = barcode_number.upper()  # Convertit en majuscules
            use_ean13 = False
    
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_price = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_website = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_price = ImageFont.load_default()
        font_website = ImageFont.load_default()
    
    margin = 12
    current_y = margin
    
    # Traitement du nom du produit
    max_chars_per_line = 32
    lines = []
    
    truncated_name = product_name
    if len(product_name) > max_chars_per_line * 2:
        truncated_name = product_name[:max_chars_per_line * 2 - 3] + "..."
    
    if len(truncated_name) > max_chars_per_line:
        words = truncated_name.split()
        current_line = ""
        for word in words:
            if len(current_line + word + " ") <= max_chars_per_line:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                    if len(lines) >= 2:
                        break
                current_line = word + " "
        if current_line and len(lines) < 2:
            lines.append(current_line.strip())
    else:
        lines = [truncated_name]
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_medium)
        text_width = bbox[2] - bbox[0]
        x_centered = (width - text_width) // 2
        draw.text((x_centered, current_y), line, fill='black', font=font_medium)
        current_y += 24
    
    current_y += 15
    
    # Dessin du code-barres
    barcode_height = 100
    module_width = 3 if not use_ean13 else 5
    
    if use_ean13:
        # Code-barres EAN-13
        actual_barcode_width = 113 * module_width
        base_center = (width - actual_barcode_width) // 2
        barcode_x = base_center + 35
        success = ean13.draw_barcode(draw, barcode_x, current_y, actual_barcode_width, barcode_height, barcode_code, module_width)
    else:
        # Code-barres Code 128
        # Estimation de la largeur (11 bits par caractère + start + checksum + stop)
        estimated_width = (len(barcode_code) + 3) * 11 * module_width
        barcode_x = (width - estimated_width) // 2
        success = code128.draw_barcode(draw, barcode_x, current_y, estimated_width, barcode_height, barcode_code, module_width)
    
    if not success:
        draw.text((barcode_x, current_y), f"Code: {barcode_code}", fill='black', font=font_small)
    
    current_y += barcode_height + 5
    
    # Affichage du code-barres
    formatted_barcode = format_barcode_display(barcode_code, use_ean13)
    bbox = draw.textbbox((0, 0), formatted_barcode, font=font_small)
    text_width = bbox[2] - bbox[0]
    x_centered = (width - text_width) // 2
    draw.text((x_centered, current_y), formatted_barcode, fill='black', font=font_small)
    current_y += 30
    
    # Prix
    price_text = f"{price_euros:.2f} €"
    bbox = draw.textbbox((0, 0), price_text, font=font_price)
    text_width = bbox[2] - bbox[0]
    x_centered = (width - text_width) // 2
    draw.text((x_centered, current_y), price_text, fill='black', font=font_price)
    current_y += 50
    
    # Pied de page
    if footer and footer.strip():
        bbox = draw.textbbox((0, 0), footer, font=font_website)
        text_width = bbox[2] - bbox[0]
        x_centered = (width - text_width) // 2
        draw.text((x_centered, current_y), footer, fill='black', font=font_website)
    
    # Bordure
    draw.rectangle([2, 2, width-2, height-2], outline='black', width=1)
    
    # Sauvegarde
    bw = image.convert('1')
    safe_barcode = "".join(c for c in barcode_code if c.isalnum())
    filename = f"etiquette_{safe_barcode}.png"
    bw.save(filename)
    
    return filename, barcode_code

def print_label(filename):
    cmd = [
        'brother_ql', '--backend', 'pyusb',
        '--model', 'QL-800',
        '--printer', 'usb://0x04f9:0x209b',
        'print', '-l', '62', filename
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if 'Total:' in result.stderr:
        return True, "Print successful"
    else:
        return False, f"Print error: {result.stderr.strip()}"

def main():
    try:
        if len(sys.argv) < 4:
            print("Usage: python3 etiquettes.py <title> <price> <barcode> [footer]", file=sys.stderr)
            print("Exemples:", file=sys.stderr)
            print("  python3 etiquettes.py 'Python Book' 29.90 210012345 'www.site.com'  # EAN-13", file=sys.stderr)
            print("  python3 etiquettes.py 'Special Item' 15.50 'ABC123DEF' 'www.site.com'  # Code 128", file=sys.stderr)
            sys.exit(1)
        
        title = sys.argv[1]
        
        try:
            price = float(sys.argv[2])
        except ValueError:
            print("Error: Price must be a number", file=sys.stderr)
            sys.exit(1)
        
        barcode = sys.argv[3]
        footer = sys.argv[4] if len(sys.argv) > 4 else ""
        
        # Validation moins restrictive - accepte maintenant les caractères alphanumériques
        if barcode and not all(c.isalnum() for c in barcode):
            print("Error: Barcode must contain only letters and digits", file=sys.stderr)
            sys.exit(1)
        
        filename, barcode_code = create_price_label(title, price, barcode, footer)
        
        barcode_type = "EAN-13" if is_numeric(barcode_code) and len(barcode_code) == 13 else "Code 128"
        print(f"Generated {barcode_type} barcode: {barcode_code}")
        
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
