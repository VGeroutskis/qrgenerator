"""
QR Code Generator core
"""

from typing import Optional, List, Tuple
from .qr_encoder import QREncoder
from .qr_structure import select_version, DATA_CAPACITY
from .reed_solomon import ReedSolomon, EC_CODEWORDS_TABLE
from .qr_matrix import QRMatrix


class QRCodeGenerator:
    MIN_VERSION = 1
    MAX_VERSION = 40
    BITS_PER_BYTE = 8
    NUM_MASK_PATTERNS = 8

    def __init__(self):
        self.encoder = QREncoder()
        self.rs = ReedSolomon()

    def generate(self, data: str, ec_level: str = 'M') -> QRMatrix:
        mode = self.encoder.detect_mode(data)
        version, encoded_bits = self._encode_and_select_version(data, ec_level, mode)

        print(f"Selected version: {version}, EC: {ec_level}")
        print(f"Data bits: {len(encoded_bits)}")

        data_codewords = self.encoder.bits_to_bytes(encoded_bits)

        final_codewords = self._generate_error_correction(
            data_codewords, version, ec_level
        )

        matrix = self._create_matrix_with_data(final_codewords, version)

        best_matrix = self._select_best_mask(matrix, version, ec_level)

        return best_matrix

    def _encode_and_select_version(
        self, data: str, ec_level: str, mode: int
    ) -> Tuple[int, List[int]]:
        for version in range(self.MIN_VERSION, self.MAX_VERSION + 1):
            encoded_bits = self.encoder.encode(data, version, mode)
            capacity_bytes = DATA_CAPACITY.get((version, ec_level), 0)
            capacity_bits = capacity_bytes * self.BITS_PER_BYTE
            if len(encoded_bits) <= capacity_bits:
                padded_bits = self.encoder.add_padding(encoded_bits, capacity_bits)
                return version, padded_bits
        raise ValueError("Data too large for supported versions")

    def _generate_error_correction(
        self, data_codewords: List[int], version: int, ec_level: str
    ) -> List[int]:
        ec_info = self._get_ec_info(version, ec_level)
        ec_per_block, blocks_g1, blocks_g2, _ = ec_info
        if self._is_single_block(blocks_g1, blocks_g2):
            return self._encode_single_block(data_codewords, ec_per_block)
        return self._encode_multi_blocks(data_codewords, ec_per_block, blocks_g1, blocks_g2)

    def _get_ec_info(self, version: int, ec_level: str) -> tuple:
        ec_info = EC_CODEWORDS_TABLE.get((version, ec_level))
        if not ec_info:
            raise ValueError(f"Invalid version {version} or EC level {ec_level}")
        return ec_info

    def _is_single_block(self, blocks_g1: int, blocks_g2: int) -> bool:
        return blocks_g1 == 1 and blocks_g2 == 0

    def _encode_single_block(self, data: List[int], ec_count: int) -> List[int]:
        ec_codewords = self.rs.encode(data, ec_count)
        return data + ec_codewords

    def _encode_multi_blocks(
        self, data_codewords: List[int], ec_per_block: int,
        blocks_g1: int, blocks_g2: int
    ) -> List[int]:
        total_blocks = blocks_g1 + blocks_g2
        block_size = len(data_codewords) // total_blocks
        data_blocks, ec_blocks = self._create_blocks(
            data_codewords, block_size, total_blocks, ec_per_block
        )
        final_codewords = self._interleave_blocks(data_blocks, ec_blocks)
        return final_codewords

    def _create_blocks(
        self, data: List[int], block_size: int, total_blocks: int, ec_count: int
    ) -> Tuple[List[List[int]], List[List[int]]]:
        data_blocks = []
        ec_blocks = []
        for i in range(total_blocks):
            start = i * block_size
            end = min(start + block_size, len(data))
            block_data = data[start:end]
            block_ec = self.rs.encode(block_data, ec_count)
            data_blocks.append(block_data)
            ec_blocks.append(block_ec)
        return data_blocks, ec_blocks

    def _interleave_blocks(self, data_blocks: List[List[int]], ec_blocks: List[List[int]]) -> List[int]:
        result = []
        max_data_len = max(len(block) for block in data_blocks)
        for i in range(max_data_len):
            for block in data_blocks:
                if i < len(block):
                    result.append(block[i])
        max_ec_len = max(len(block) for block in ec_blocks) if ec_blocks else 0
        for i in range(max_ec_len):
            for block in ec_blocks:
                if i < len(block):
                    result.append(block[i])
        return result

    def _create_matrix_with_data(self, codewords: List[int], version: int) -> QRMatrix:
        bits = self._codewords_to_bits(codewords)
        matrix = QRMatrix(version)
        matrix.build_function_patterns()
        matrix.place_data(bits)
        return matrix

    def _codewords_to_bits(self, codewords: List[int]) -> List[int]:
        bits = []
        for codeword in codewords:
            for bit_pos in range(self.BITS_PER_BYTE - 1, -1, -1):
                bits.append((codeword >> bit_pos) & 1)
        return bits

    def _select_best_mask(self, matrix: QRMatrix, version: int, ec_level: str) -> QRMatrix:
        masks_with_scores = [
            self._evaluate_mask(matrix, version, ec_level, mask)
            for mask in range(self.NUM_MASK_PATTERNS)
        ]
        best_matrix, best_mask, best_penalty = min(masks_with_scores, key=lambda x: x[2])
        print(f"Best mask: {best_mask}, Penalty: {best_penalty}")
        best_matrix.mask_pattern = best_mask
        return best_matrix

    def _evaluate_mask(self, base_matrix: QRMatrix, version: int, ec_level: str, mask: int) -> Tuple[QRMatrix, int, int]:
        test_matrix = self._clone_matrix(base_matrix, version)
        test_matrix.apply_mask(mask)
        test_matrix.add_format_information(ec_level, mask)
        penalty = test_matrix.evaluate_penalty()
        return test_matrix, mask, penalty

    def _clone_matrix(self, matrix: QRMatrix, version: int) -> QRMatrix:
        clone = QRMatrix(version)
        clone.matrix = [row[:] for row in matrix.matrix]
        clone.reserved = [row[:] for row in matrix.reserved]
        return clone
