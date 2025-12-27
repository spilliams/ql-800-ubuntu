import random

def calculate_checksum(code_12_digits):
    total = 0
    for i, digit in enumerate(code_12_digits):
        if i % 2 == 0:
            total += int(digit)
        else:
            total += int(digit) * 3
    return str((10 - (total % 10)) % 10)

def generate_internal():
    prefix = "2"
    random_part = "".join([str(random.randint(0, 9)) for _ in range(11)])
    code_12 = prefix + random_part
    checksum = calculate_checksum(code_12)
    return code_12 + checksum

def draw_barcode(draw, x, y, width, height, ean13_code, module_width):
    """Dessine un code-barres EAN-13 (code original conservé)"""
    patterns = {
        'A': {
            '0': '0001101', '1': '0011001', '2': '0010011', '3': '0111101',
            '4': '0100011', '5': '0110001', '6': '0101111', '7': '0111011',
            '8': '0110111', '9': '0001011'
        },
        'B': {
            '0': '0100111', '1': '0110011', '2': '0011011', '3': '0100001',
            '4': '0011101', '5': '0111001', '6': '0000101', '7': '0010001',
            '8': '0001001', '9': '0010111'
        },
        'C': {
            '0': '1110010', '1': '1100110', '2': '1101100', '3': '1000010',
            '4': '1011100', '5': '1001110', '6': '1010000', '7': '1000100',
            '8': '1001000', '9': '1110100'
        }
    }
    
    first_digit_patterns = {
        '0': 'AAAAAA', '1': 'AABABB', '2': 'AABBAB', '3': 'AABBBA',
        '4': 'ABAABB', '5': 'ABBAAB', '6': 'ABBBAA', '7': 'ABABAB',
        '8': 'ABABBA', '9': 'ABBABA'
    }
    
    if len(ean13_code) != 13:
        return False
    
    first_digit = ean13_code[0]
    left_digits = ean13_code[1:7]
    right_digits = ean13_code[7:13]
    pattern_sequence = first_digit_patterns[first_digit]
    
    current_x = x
    
    for bit in '101':
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    for i, digit in enumerate(left_digits):
        pattern_type = pattern_sequence[i]
        bit_pattern = patterns[pattern_type][digit]
        
        for bit in bit_pattern:
            if bit == '1':
                draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
            current_x += module_width
    
    for bit in '01010':
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    for digit in right_digits:
        bit_pattern = patterns['C'][digit]
        
        for bit in bit_pattern:
            if bit == '1':
                draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
            current_x += module_width
    
    for bit in '101':
        if bit == '1':
            draw.rectangle([current_x, y, current_x + module_width, y + height], fill='black')
        current_x += module_width
    
    return True
