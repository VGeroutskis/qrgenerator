#!/usr/bin/env python3
"""
QR Code Generator - Γεννήτρια Κωδικών QR
=========================================
Κύριο πρόγραμμα για γρήγορη δημιουργία QR codes από γραμμή εντολών

Χρήση: python generate_qr.py <δεδομένα> [επίπεδο_EC] [αρχείο_εξόδου]

Παραδείγματα:
  python generate_qr.py 'Hello World'
  python generate_qr.py 'https://example.com' M output/url.svg
  python generate_qr.py 'Καλημέρα' L greeting.svg

Επίπεδα EC: L (~7%), M (~15%), Q (~25%), H (~30%)
"""

import sys
from qrgenerator import QRCodeGenerator, SVGRenderer, ASCIIRenderer


def main():
    """Κύρια συνάρτηση - επεξεργασία ορισμάτων και δημιουργία QR"""
    if len(sys.argv) < 2:
        print("Χρήση: python generate_qr.py <δεδομένα> [επίπεδο_EC] [αρχείο_εξόδου]")
        print()
        print("Παραδείγματα:")
        print("  python generate_qr.py 'Hello World'")
        print("  python generate_qr.py 'https://example.com' M output/url.svg")
        print("  python generate_qr.py '123456' H")
        print("  python generate_qr.py 'Καλημέρα' L greeting.svg")
        print()
        print("Επίπεδα EC: L (7%), M (15%), Q (25%), H (30%)")
        sys.exit(1)
    
    # Ανάλυση ορισμάτων
    data = sys.argv[1]
    ec_level = sys.argv[2] if len(sys.argv) > 2 else 'M'
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Δημιουργία QR code
    gen = QRCodeGenerator()
    qr = gen.generate(data, ec_level)
    
    print(f"Δημιουργήθηκε QR Code:")
    print(f"  Δεδομένα: {data[:50]}{'...' if len(data) > 50 else ''}")
    print(f"  Έκδοση: {qr.version}")
    print(f"  Μέγεθος: {qr.size}×{qr.size}")
    print(f"  Επίπεδο EC: {ec_level}")
    
    # Αποθήκευση αν καθορίστηκε αρχείο εξόδου
    if output_file:
        renderer = SVGRenderer()
        with open(output_file, 'w') as f:
            f.write(renderer.render(qr, module_size=10, border=4))
        print(f"  Αποθηκεύτηκε σε: {output_file}")
    else:
        # Εμφάνιση ASCII preview
        ascii_renderer = ASCIIRenderer()
        print()
        print(ascii_renderer.render(qr, border=2))


if __name__ == "__main__":
    main()
