#!/usr/bin/env python3
import ql800
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 print.py FILENAME", file=sys.stderr)
        sys.exit(1)
    
    filename = sys.argv[1]
    
    tape_designation = '62'
    
    success, message = ql800.print_label(filename, tape_designation)
    if success:
        print(f"✓ {message}")
        sys.exit(0)
    else:
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
