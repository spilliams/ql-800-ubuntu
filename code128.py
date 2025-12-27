import string
import random

def generate_internal():
    """Génère un code-barres Code 128 aléatoire avec des lettres et chiffres"""
    chars = string.ascii_uppercase + string.digits
    return "INT" + "".join(random.choices(chars, k=8))

def get_patterns():
    """Retourne les patterns Code 128"""
    patterns = {
        # Code Set A (caractères de contrôle, chiffres, lettres majuscules)
        'A': {
            ' ': '11011001100', '!': '11001101100', '"': '11001100110', '#': '10010011000',
            '$': '10010001100', '%': '10001001100', '&': '10011001000', "'": '10011000100',
            '(': '10001100100', ')': '11001001000', '*': '11001000100', '+': '11000100100',
            ',': '10110011100', '-': '10011011100', '.': '10011001110', '/': '10111001100',
            '0': '10011101100', '1': '10011100110', '2': '11001110010', '3': '11001011100',
            '4': '11001001110', '5': '11011100100', '6': '11001110100', '7': '11101101110',
            '8': '11101001100', '9': '11100101100', ':': '11100100110', ';': '11101100100',
            '<': '11100110100', '=': '11100110010', '>': '11011011000', '?': '11011000110',
            '@': '11000110110', 'A': '10100011000', 'B': '10001011000', 'C': '10001000110',
            'D': '10110001000', 'E': '10001101000', 'F': '10001100010', 'G': '11010001000',
            'H': '11000101000', 'I': '11000100010', 'J': '10110111000', 'K': '10110001110',
            'L': '10001101110', 'M': '10111011000', 'N': '10111000110', 'O': '10001110110',
            'P': '11101110110', 'Q': '11010001110', 'R': '11000101110', 'S': '11011101000',
            'T': '11011100010', 'U': '11011101110', 'V': '11101011000', 'W': '11101000110',
            'X': '11100010110', 'Y': '11101101000', 'Z': '11101100010'
        }
    }
    
    # Codes spéciaux
    start_a = '11010000100'
    start_b = '11010010000'
    start_c = '11010011100'
    stop = '1100011101011'
    
    return patterns, start_a, start_b, start_c, stop

def calculate_checksum(data, start_code):
    """Calcule le checksum pour Code 128"""
    # Valeurs des caractères pour le checksum
    char_values = {}
    
    # Valeurs pour les caractères ASCII imprimables
    for i in range(32, 127):
        char_values[chr(i)] = i - 32
    
    # Start codes
    start_values = {'A': 103, 'B': 104, 'C': 105}
    
    checksum = start_values[start_code]
    
    for i, char in enumerate(data):
        if char in char_values:
            checksum += char_values[char] * (i + 1)
    
    return checksum % 103

def draw_barcode(draw, x, y, width, height, data, module_width):
    """Dessine un code-barres Code 128"""
    patterns, start_a, start_b, start_c, stop = get_patterns()
    
    # Utilise le Code Set A pour supporter les lettres majuscules et chiffres
    current_x = x
    
    # Start code A
    for bit in start_a:
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    # Données
    for char in data:
        if char in patterns['A']:
            pattern = patterns['A'][char]
            for bit in pattern:
                if bit == '1':
                    draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
                current_x += module_width
        else:
            # Si le caractère n'est pas supporté, le remplacer par un espace
            pattern = patterns['A'][' ']
            for bit in pattern:
                if bit == '1':
                    draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
                current_x += module_width
    
    # Checksum
    checksum_value = calculate_checksum(data, 'A')
    checksum_pattern = get_checksum_pattern(checksum_value)
    for bit in checksum_pattern:
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    # Stop code
    for bit in stop:
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    return True

def get_checksum_pattern(checksum_value):
    """Retourne le pattern pour la valeur de checksum"""
    patterns = [
        '11011001100', '11001101100', '11001100110', '10010011000', '10010001100',
        '10001001100', '10011001000', '10011000100', '10001100100', '11001001000',
        '11001000100', '11000100100', '10110011100', '10011011100', '10011001110',
        '10111001100', '10011101100', '10011100110', '11001110010', '11001011100',
        '11001001110', '11011100100', '11001110100', '11101101110', '11101001100',
        '11100101100', '11100100110', '11101100100', '11100110100', '11100110010',
        '11011011000', '11011000110', '11000110110', '10100011000', '10001011000',
        '10001000110', '10110001000', '10001101000', '10001100010', '11010001000',
        '11000101000', '11000100010', '10110111000', '10110001110', '10001101110',
        '10111011000', '10111000110', '10001110110', '11101110110', '11010001110',
        '11000101110', '11011101000', '11011100010', '11011101110', '11101011000',
        '11101000110', '11100010110', '11101101000', '11101100010', '11100011010',
        '11101111010', '11001000010', '11110001010', '10100110000', '10100001100',
        '10010110000', '10010000110', '10000101100', '10000100110', '10110010000',
        '10110000100', '10011010000', '10011000010', '10000110100', '10000110010',
        '11000010010', '11001010000', '11110111010', '11000010100', '10001111010',
        '10100111100', '10010111100', '10010011110', '10111100100', '10011110100',
        '10011110010', '11110100100', '11110010100', '11110010010', '11011011110',
        '11011110110', '11110110110', '10101111000', '10100011110', '10001011110',
        '10111101000', '10111100010', '11110101000', '11110100010', '10111011110',
        '10111101110', '11101011110', '11110101110', '11010000100', '11010010000',
        '11010011100', '1100011101011'
    ]
    
    if 0 <= checksum_value < len(patterns):
        return patterns[checksum_value]
    return patterns[0]
