"""
QR Code Renderers (ASCII, SVG)
"""


class ASCIIRenderer:
    def render(self, matrix, border=2):
        lines = []
        width = matrix.size + 2 * border
        lines.extend(['█' * width * 2] * border)
        for row in matrix.matrix:
            line = '█' * (border * 2)
            for module in row:
                if module == 1:
                    line += '██'
                else:
                    line += '  '
            line += '█' * (border * 2)
            lines.append(line)
        lines.extend(['█' * width * 2] * border)
        return '\n'.join(lines)


class SVGRenderer:
    def render(self, matrix, module_size=10, border=4):
        size = matrix.size + 2 * border
        svg_size = size * module_size
        svg = [
            f'<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'width="{svg_size}" height="{svg_size}" '
            f'viewBox="0 0 {svg_size} {svg_size}">',
            f'  <rect width="{svg_size}" height="{svg_size}" fill="white"/>',
            f'  <g fill="black">',
        ]
        for row in range(matrix.size):
            for col in range(matrix.size):
                if matrix.matrix[row][col] == 1:
                    x = (col + border) * module_size
                    y = (row + border) * module_size
                    svg.append(
                        f'    <rect x="{x}" y="{y}" '
                        f'width="{module_size}" height="{module_size}"/>'
                    )
        svg.extend(['  </g>', '</svg>'])
        return '\n'.join(svg)


class ImageRenderer:
    def render(self, matrix, module_char='█', empty_char=' ', border=2):
        lines = []
        width = matrix.size + 2 * border
        border_line = module_char * width
        lines.extend([border_line] * border)
        for row in matrix.matrix:
            line = module_char * border
            for module in row:
                line += module_char if module == 1 else empty_char
            line += module_char * border
            lines.append(line)
        lines.extend([border_line] * border)
        return '\n'.join(lines)
