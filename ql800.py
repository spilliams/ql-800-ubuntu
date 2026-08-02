#!/usr/bin/env python3
import re
import subprocess
import sys
import unicodedata

tape_designations = ["12", "12+17", "18", "29", "38", "50", "54", "62", "62red", "102", "103", "104", "17x54", "17x87", "23x23", "29x42", "29x90", "39x90", "39x48", "52x29", "54x29", "60x86", "62x29", "62x100", "102x51", "102x152", "103x164", "d12", "d24", "d58"]



def escape_for_filename(value):
    text = str(value)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-_')



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
