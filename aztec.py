from PIL import Image
import subprocess
import sys

def generate(payload, filename="aztec.png"):
    """Relies on an installed CLI tool named `zint` to work."""
    cmd = [
        'zint',
        '-b', 'AZTEC',
        '-d', payload,
        '-o', filename
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)

    if len(result.stderr) > 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
