"""
QR Code Matrix Generation and Data Placement
"""

from .qr_structure import get_version_size, get_alignment_positions


class QRMatrix:
    UNSET = -1
    WHITE = 0
    BLACK = 1
    FINDER_SIZE = 7
    ALIGNMENT_SIZE = 5
    TIMING_ROW_COL = 6
    FORMAT_STRIP_ROW = 8

    def __init__(self, version):
        self.version = version
        self.size = get_version_size(version)
        self.matrix = [[self.UNSET] * self.size for _ in range(self.size)]
        self.reserved = [[False] * self.size for _ in range(self.size)]

    def add_finder_pattern(self, row, col):
        pattern = [
            [1,1,1,1,1,1,1],
            [1,0,0,0,0,0,1],
            [1,0,1,1,1,0,1],
            [1,0,1,1,1,0,1],
            [1,0,1,1,1,0,1],
            [1,0,0,0,0,0,1],
            [1,1,1,1,1,1,1],
        ]
        for i in range(7):
            for j in range(7):
                r, c = row + i, col + j
                if 0 <= r < self.size and 0 <= c < self.size:
                    self.matrix[r][c] = pattern[i][j]
                    self.reserved[r][c] = True

    def add_separator(self, row, col, width, height):
        for i in range(height):
            for j in range(width):
                r, c = row + i, col + j
                if 0 <= r < self.size and 0 <= c < self.size:
                    if not self.reserved[r][c]:
                        self.matrix[r][c] = 0
                        self.reserved[r][c] = True

    def add_timing_patterns(self):
        start, end = 8, self.size - 8
        for col in range(start, end):
            self.matrix[self.TIMING_ROW_COL][col] = col % 2
            self.reserved[self.TIMING_ROW_COL][col] = True
        for row in range(start, end):
            self.matrix[row][self.TIMING_ROW_COL] = row % 2
            self.reserved[row][self.TIMING_ROW_COL] = True

    def add_alignment_pattern(self, row, col):
        offset_range = range(-2, 3)
        for i in offset_range:
            for j in offset_range:
                r, c = row + i, col + j
                if not self._is_valid_position(r, c):
                    continue
                is_border = abs(i) == 2 or abs(j) == 2
                is_center = i == 0 and j == 0
                self.matrix[r][c] = self.BLACK if (is_border or is_center) else self.WHITE
                self.reserved[r][c] = True

    def _is_valid_position(self, row: int, col: int) -> bool:
        return 0 <= row < self.size and 0 <= col < self.size

    def add_dark_module(self):
        row = 4 * self.version + 9
        col = 8
        self.matrix[row][col] = 1
        self.reserved[row][col] = True

    def reserve_format_areas(self):
        for i in range(9):
            if i != 6:
                self.reserved[8][i] = True
                self.reserved[i][8] = True
        for i in range(8):
            self.reserved[8][self.size - 1 - i] = True
        for i in range(7):
            self.reserved[self.size - 1 - i][8] = True

    def build_function_patterns(self):
        self.add_finder_pattern(0, 0)
        self.add_finder_pattern(0, self.size - 7)
        self.add_finder_pattern(self.size - 7, 0)
        self.add_separator(7, 0, 8, 1)
        self.add_separator(0, 7, 1, 8)
        self.add_separator(7, self.size - 8, 8, 1)
        self.add_separator(0, self.size - 8, 1, 8)
        self.add_separator(self.size - 8, 0, 8, 1)
        self.add_separator(self.size - 8, 7, 1, 8)
        self.add_timing_patterns()
        if self.version >= 2:
            positions = get_alignment_positions(self.version)
            for row, col in positions:
                self.add_alignment_pattern(row, col)
        self.add_dark_module()
        self.reserve_format_areas()

    def place_data(self, data_bits):
        bit_index = 0
        col = self.size - 1
        direction = -1
        while col > 0:
            if col == 6:
                col -= 1
            for row_step in range(self.size):
                if direction == -1:
                    row = self.size - 1 - row_step
                else:
                    row = row_step
                for c_offset in [0, -1]:
                    c = col + c_offset
                    if not self.reserved[row][c]:
                        if bit_index < len(data_bits):
                            self.matrix[row][c] = data_bits[bit_index]
                            bit_index += 1
                        else:
                            self.matrix[row][c] = 0
            col -= 2
            direction *= -1
        return bit_index

    def apply_mask(self, mask_pattern):
        for row in range(self.size):
            for col in range(self.size):
                if not self.reserved[row][col]:
                    if self._mask_condition(row, col, mask_pattern):
                        self.matrix[row][col] ^= 1

    def _mask_condition(self, i, j, pattern):
        masks = [
            lambda i, j: (i + j) % 2 == 0,
            lambda i, j: i % 2 == 0,
            lambda i, j: j % 3 == 0,
            lambda i, j: (i + j) % 3 == 0,
            lambda i, j: ((i // 2) + (j // 3)) % 2 == 0,
            lambda i, j: ((i * j) % 2) + ((i * j) % 3) == 0,
            lambda i, j: (((i * j) % 2) + ((i * j) % 3)) % 2 == 0,
            lambda i, j: (((i + j) % 2) + ((i * j) % 3)) % 2 == 0
        ]
        return masks[pattern](i, j) if 0 <= pattern < len(masks) else False

    def add_format_information(self, ec_level, mask_pattern):
        format_bits = self._generate_format_bits(ec_level, mask_pattern)
        for i in range(6):
            self.matrix[8][i] = format_bits[i]
        self.matrix[8][7] = format_bits[6]
        self.matrix[8][8] = format_bits[7]
        self.matrix[7][8] = format_bits[8]
        self.matrix[5][8] = format_bits[9]
        self.matrix[4][8] = format_bits[10]
        self.matrix[3][8] = format_bits[11]
        self.matrix[2][8] = format_bits[12]
        self.matrix[1][8] = format_bits[13]
        self.matrix[0][8] = format_bits[14]
        for i in range(7):
            self.matrix[8][self.size - 1 - i] = format_bits[i]
        for i in range(8):
            row = self.size - 1 - i
            self.matrix[row][8] = format_bits[7 + i]
        dark_module_row = 4 * self.version + 9
        self.matrix[dark_module_row][8] = 1

    def _generate_format_bits(self, ec_level, mask_pattern):
        ec_bits = {'L': 0b01, 'M': 0b00, 'Q': 0b11, 'H': 0b10}
        format_data = (ec_bits[ec_level] << 3) | mask_pattern
        generator = 0b10100110111
        format_value = format_data << 10
        for _ in range(5):
            if format_value & (1 << (14 - _)):
                format_value ^= generator << (4 - _)
        format_info = (format_data << 10) | format_value
        format_info ^= 0b101010000010010
        bits = []
        for i in range(14, -1, -1):
            bits.append((format_info >> i) & 1)
        return bits

    def evaluate_penalty(self):
        score = 0
        score += self._penalty_rule_1()
        score += self._penalty_rule_2()
        score += self._penalty_rule_3()
        score += self._penalty_rule_4()
        return score

    def _penalty_rule_1(self):
        penalty = 0
        for row in range(self.size):
            count = 1
            prev = self.matrix[row][0]
            for col in range(1, self.size):
                if self.matrix[row][col] == prev:
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
                    prev = self.matrix[row][col]
            if count >= 5:
                penalty += 3 + (count - 5)
        for col in range(self.size):
            count = 1
            prev = self.matrix[0][col]
            for row in range(1, self.size):
                if self.matrix[row][col] == prev:
                    count += 1
                else:
                    if count >= 5:
                        penalty += 3 + (count - 5)
                    count = 1
                    prev = self.matrix[row][col]
            if count >= 5:
                penalty += 3 + (count - 5)
        return penalty

    def _penalty_rule_2(self):
        penalty = 0
        for row in range(self.size - 1):
            for col in range(self.size - 1):
                value = self.matrix[row][col]
                if (self.matrix[row][col + 1] == value and
                    self.matrix[row + 1][col] == value and
                    self.matrix[row + 1][col + 1] == value):
                    penalty += 3
        return penalty

    def _penalty_rule_3(self):
        penalty = 0
        patterns = [
            [1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 1]
        ]
        for row in range(self.size):
            for col in range(self.size - 10):
                for pattern in patterns:
                    match = all(self.matrix[row][col + i] == pattern[i] for i in range(11))
                    if match:
                        penalty += 40
        for col in range(self.size):
            for row in range(self.size - 10):
                for pattern in patterns:
                    match = all(self.matrix[row + i][col] == pattern[i] for i in range(11))
                    if match:
                        penalty += 40
        return penalty

    def _penalty_rule_4(self):
        total = self.size * self.size
        dark = sum(sum(1 for val in row if val == 1) for row in self.matrix)
        percent = (dark * 100) // total
        deviation = abs(percent - 50) // 5
        return deviation * 10
