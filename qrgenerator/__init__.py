"""
QR Generator Package

Lightweight, standalone QR code generator package exposing main classes.
"""

from .qr_generator import QRCodeGenerator
from .qr_renderer import SVGRenderer, ASCIIRenderer
from .qr_encoder import QREncoder
from .qr_matrix import QRMatrix

__version__ = "1.0.0"

__all__ = [
    "QRCodeGenerator",
    "SVGRenderer",
    "ASCIIRenderer",
    "QREncoder",
    "QRMatrix",
]
