# Δημιουργία Κωδικών QR

Ελαφρύ, ανεξάρτητο εργαλείο και βιβλιοθήκη για τη δημιουργία QR codes σε μορφές SVG ή ASCII.

## Περιγραφή
Αυτό το αποθετήριο περιέχει έναν απλό, αλλά πλήρη, QR generator γραμμένο σε Python. Παρέχει:
- Κεντρική CLI εφαρμογή: `generate_qr.py`
- Βιβλιοθήκη `qrgenerator` με βασικές κλάσεις: `QRCodeGenerator`, `QREncoder`, `QRMatrix`, `SVGRenderer`, `ASCIIRenderer`.

Το πακέτο υλοποιεί κωδικοποίηση δεδομένων, Reed–Solomon error correction, δημιουργία matrix, επιλογή μάσκας και rendering.

## Απαιτήσεις
- Python 3.8+
- Δεν χρειάζονται εξωτερικές βιβλιοθήκες (pure-Python).

## Γρήγορη εκτέλεση (CLI)
Δημιουργεί και εμφανίζει ένα preview ή αποθηκεύει σε SVG:

```bash
python generate_qr.py 'Γεια σου κόσμε'          # ASCII preview
python generate_qr.py 'https://example.com' M out.svg  # Αποθήκευση σε SVG
```

Παράμετροι CLI: `<δεδομένα> [επίπεδο_EC] [αρχείο_εξόδου]`
Επίπεδα EC: `L` (~7%), `M` (~15%), `Q` (~25%), `H` (~30%).

### Παραδείγματα ανά mode
Το πακέτο ανιχνεύει και υποστηρίζει τα κύρια modes: numeric, alphanumeric και byte (UTF-8). Παρακάτω μερικά παραδείγματα CLI για κάθε περίπτωση:

```bash
# Numeric (μόνο αριθμοί) — πιο συμπαγής κωδικοποίηση
python generate_qr.py 012345678901234

# Alphanumeric (A–Z, 0–9 και επιτρεπτοί χαρακτήρες) — π.χ. διακριτικά, URL-safe
python generate_qr.py 'HELLO-123' M out_alnum.svg

# Byte mode (UTF-8) — χρησιμοποιείται για ελληνικά, σύμβολα, emoji κτλ.
python generate_qr.py 'Καλημέρα κόσμε' Q greeting.svg
python generate_qr.py 'Hello ✨' H emoji.svg

# Σημείωση για Kanji: η συγκεκριμένη υλοποίηση δεν διαθέτει ξεχωριστό Kanji encoder.
# Οι χαρακτήρες Kanji (αν χρειαστεί) θα κωδικοποιηθούν μέσω byte (UTF-8) mode.
```



### Πρόσθετα κοινά ειδικά φορμά
Παρακάτω υπάρχουν έτοιμα παραδείγματα για όλες τις συνήθεις ειδικές μορφές που χρησιμοποιούνται σε QR codes.

1) vCard (VCARD / επαφές)

```bash
# CLI (escaped νέες γραμμές)
python generate_qr.py "BEGIN:VCARD\nVERSION:3.0\nN:Παπαδόπουλος;Γιάννης;;;\nFN:Γιάννης Παπαδόπουλος\nORG:Example\nTEL;TYPE=WORK,VOICE:+302101234567\nEMAIL:giannis@example.com\nEND:VCARD" M vcard.svg
```

Παράδειγμα βιβλιοθήκης (προτιμώμενο για πολλαπλές γραμμές):

```python
from qrgenerator import QRCodeGenerator, SVGRenderer

vcard = '''BEGIN:VCARD
VERSION:3.0
N:Παπαδόπουλος;Γιάννης;;;
FN:Γιάννης Παπαδόπουλος
ORG:Example
TEL;TYPE=WORK,VOICE:+302101234567
EMAIL:giannis@example.com
END:VCARD
'''

gen = QRCodeGenerator()
qr = gen.generate(vcard, ec_level='M')
renderer = SVGRenderer()
svg = renderer.render(qr, module_size=8, border=4)
with open('vcard.svg', 'w') as f:
  f.write(svg)
```

2) Wi‑Fi (WPA/WEP/open)

```bash
# WPA/WPA2
python generate_qr.py "WIFI:T:WPA;S:MyNetwork;P:mysecretpassword;;" M wifi_wpa.svg

# WEP
python generate_qr.py "WIFI:T:WEP;S:MyNet;P:legacykey;;" M wifi_wep.svg

# Open
python generate_qr.py "WIFI:T:nopass;S:GuestNetwork;;" L wifi_open.svg
```

3) SMS

```bash
python generate_qr.py "SMS:+302101234567:Γεια σου" M sms.svg
```

4) TEL (κλήση)

```bash
python generate_qr.py "TEL:+302101234567" L tel.svg
```

5) MAILTO / Email

```bash
python generate_qr.py "mailto:giannis@example.com?subject=Χαιρετισμός&body=Καλημέρα" M mailto.svg
```

6) GEO (γεωγραφικές συντεταγμένες)

```bash
python generate_qr.py "geo:37.9760,23.7366" L geo.svg
```

7) Bitcoin URI

```bash
python generate_qr.py "bitcoin:1BoatSLRHtKNngkdXEeobR76b53LETtpyT?amount=0.001&label=Donation" M btc.svg
```

8) iCalendar / Meeting (VEVENT)

```bash
python generate_qr.py "BEGIN:VCALENDAR\nBEGIN:VEVENT\nSUMMARY:Συνάντηση\nDTSTART:20260120T100000Z\nDTEND:20260120T110000Z\nEND:VEVENT\nEND:VCALENDAR" M ical.svg
```

9) MECARD (σύντομη μορφή επαφής)

```bash
python generate_qr.py "MECARD:N:Παπαδόπουλος,Γιάννης;TEL:+302101234567;EMAIL:giannis@example.com;;" M mecard.svg
```

Σημειώσεις:
- Σε σύνθετα, πολλαπλών γραμμών περιεχόμενα (vCard, iCalendar) προτείνεται η χρήση της βιβλιοθηκής API αντί CLI για απλούστερη διαχείριση των newline.
- Όλα τα παραδείγματα μπορούν να χρησιμοποιηθούν και μέσω του Python API αντικαθιστώντας το string στο `gen.generate(...)`.

## Χρήση ως βιβλιοθήκη
Σύντομο παράδειγμα χρήσης από Python:

```python
from qrgenerator import QRCodeGenerator, SVGRenderer

gen = QRCodeGenerator()
qr = gen.generate('Καλημέρα', ec_level='M')
renderer = SVGRenderer()
svg = renderer.render(qr, module_size=8, border=4)
with open('greeting.svg', 'w') as f:
    f.write(svg)
```

## Δομή αποθετηρίου
- `generate_qr.py` — μικρό CLI wrapper για γρήγορη χρήση.
- `qrgenerator/` — κύρια βιβλιοθήκη:
  - `qr_generator.py` — επιλογή version, interleaving, επιλογή μάσκας.
  - `qr_encoder.py` — ανίχνευση mode (numeric/alphanumeric/byte) και κωδικοποίηση.
  - `qr_matrix.py` — κατασκευή matrix, placement και penalty rules.
  - `qr_renderer.py` — `SVGRenderer`, `ASCIIRenderer` (απλά renderers).
  - `reed_solomon.py`, `galois_field.py` — Reed–Solomon EC implementation.
  - `qr_structure.py` — πίνακες χωρητικότητας και alignment patterns.

## Συνεισφορά
Για μικρές αλλαγές ή bug fixes, ανοίξτε pull request. Παρακαλείστε να διατηρείτε καθαρό και τεκμηριωμένο κώδικα.

## Άδεια
Δείτε το αρχείο `LICENSE` για λεπτομέρειες.


