"""
QR Code Data Encoding - Κωδικοποίηση Δεδομένων QR
"""

from typing import List, Optional, Union

# Mode constants
MODE_NUMERIC = 0b0001
MODE_ALPHANUMERIC = 0b0010
MODE_BYTE = 0b0100
MODE_KANJI = 0b1000

MODE_INDICATOR_BITS = 4
BITS_PER_BYTE = 8
NUMERIC_CHUNK_SIZE = 3
ALPHANUMERIC_CHUNK_SIZE = 2
ALPHANUMERIC_MULTIPLIER = 45
TERMINATOR_MAX_BITS = 4
PADDING_BYTE_1 = 0b11101100
PADDING_BYTE_2 = 0b00010001

ALPHANUMERIC_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"


class QREncoder:
    def __init__(self):
        self.alphanumeric_map = {c: i for i, c in enumerate(ALPHANUMERIC_CHARSET)}

    def detect_mode(self, data: str) -> int:
        if all(c.isdigit() for c in data):
            return MODE_NUMERIC
        elif all(c in ALPHANUMERIC_CHARSET for c in data.upper()):
            return MODE_ALPHANUMERIC
        else:
            return MODE_BYTE

    def get_character_count_bits(self, mode: int, version: int) -> int:
        if version <= 9:
            if mode == MODE_NUMERIC:
                return 10
            elif mode == MODE_ALPHANUMERIC:
                return 9
            elif mode == MODE_BYTE:
                return 8
        elif version <= 26:
            if mode == MODE_NUMERIC:
                return 12
            elif mode == MODE_ALPHANUMERIC:
                return 11
            elif mode == MODE_BYTE:
                return 16
        else:
            if mode == MODE_NUMERIC:
                return 14
            elif mode == MODE_ALPHANUMERIC:
                return 13
            elif mode == MODE_BYTE:
                return 16
        return 8

    def encode_numeric(self, data: str) -> List[int]:
        bits = []
        bit_lengths = {3: 10, 2: 7, 1: 4}
        for i in range(0, len(data), NUMERIC_CHUNK_SIZE):
            chunk = data[i:i+NUMERIC_CHUNK_SIZE]
            value = int(chunk)
            bit_length = bit_lengths[len(chunk)]
            bits.extend(self._to_bits(value, bit_length))
        return bits

    def encode_alphanumeric(self, data: str) -> List[int]:
        bits = []
        data = data.upper()
        for i in range(0, len(data), ALPHANUMERIC_CHUNK_SIZE):
            has_pair = (i + 1) < len(data)
            if has_pair:
                val1, val2 = self.alphanumeric_map[data[i]], self.alphanumeric_map[data[i+1]]
                value = val1 * ALPHANUMERIC_MULTIPLIER + val2
                bits.extend(self._to_bits(value, 11))
            else:
                value = self.alphanumeric_map[data[i]]
                bits.extend(self._to_bits(value, 6))
        return bits

    def encode_byte(self, data: Union[str, bytes]) -> List[int]:
        bits = []
        if isinstance(data, str):
            data = data.encode('utf-8')
        for byte in data:
            bits.extend(self._to_bits(byte, 8))
        return bits

    def _to_bits(self, value: int, length: int) -> List[int]:
        bits = []
        for i in range(length - 1, -1, -1):
            bits.append((value >> i) & 1)
        return bits

    def encode(self, data: str, version: int, mode: Optional[int] = None) -> List[int]:
        mode = mode if mode is not None else self.detect_mode(data)
        bits = self._build_header(mode, data, version)
        bits.extend(self._encode_data_by_mode(mode, data))
        return bits

    def _build_header(self, mode: int, data: str, version: int) -> List[int]:
        bits = self._to_bits(mode, MODE_INDICATOR_BITS)
        count_bits = self.get_character_count_bits(mode, version)
        data_length = self._get_data_length(mode, data)
        bits.extend(self._to_bits(data_length, count_bits))
        return bits

    def _get_data_length(self, mode: int, data: str) -> int:
        if mode == MODE_BYTE and isinstance(data, str):
            return len(data.encode('utf-8'))
        return len(data)

    def _encode_data_by_mode(self, mode: int, data: str) -> List[int]:
        encoders = {
            MODE_NUMERIC: self.encode_numeric,
            MODE_ALPHANUMERIC: self.encode_alphanumeric,
            MODE_BYTE: self.encode_byte
        }
        encoder = encoders.get(mode)
        if not encoder:
            raise ValueError(f"Unsupported mode: {mode}")
        return encoder(data)

    def add_padding(self, bits: List[int], total_data_bits: int) -> List[int]:
        bits = self._add_terminator(bits, total_data_bits)
        bits = self._align_to_byte_boundary(bits)
        bits = self._add_padding_bytes(bits, total_data_bits)
        return bits[:total_data_bits]

    def _add_terminator(self, bits: List[int], max_bits: int) -> List[int]:
        terminator_len = min(TERMINATOR_MAX_BITS, max_bits - len(bits))
        return bits + [0] * terminator_len

    def _align_to_byte_boundary(self, bits: List[int]) -> List[int]:
        while len(bits) % BITS_PER_BYTE != 0:
            bits.append(0)
        return bits

    def _add_padding_bytes(self, bits: List[int], target_bits: int) -> List[int]:
        padding_bytes = [PADDING_BYTE_1, PADDING_BYTE_2]
        index = 0
        while len(bits) < target_bits:
            byte_val = padding_bytes[index % 2]
            bits.extend(self._to_bits(byte_val, BITS_PER_BYTE))
            index += 1
        return bits

    def bits_to_bytes(self, bits: List[int]) -> List[int]:
        bytes_list = []
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i+8]
            byte_val = 0
            for bit in byte_bits:
                byte_val = (byte_val << 1) | bit
            bytes_list.append(byte_val)
        return bytes_list
