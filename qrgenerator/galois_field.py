"""
Galois Field GF(2^8) arithmetic for Reed-Solomon error correction
"""

class GaloisField:
    """Implementation of GF(2^8) for QR Code error correction"""
    
    def __init__(self):
        # Generator polynomial: x^8 + x^4 + x^3 + x^2 + 1 (0x11d)
        self.primitive = 0x11d
        
        # Precompute log and antilog tables for faster computation
        self.exp_table = [0] * 512  # Extended to 512 for easier modulo
        self.log_table = [0] * 256
        
        self._generate_tables()
    
    def _generate_tables(self):
        """Generate exponential and logarithm tables"""
        x = 1
        for i in range(255):
            self.exp_table[i] = x
            self.log_table[x] = i
            
            # Multiply by 2 (alpha) in GF(2^8)
            x <<= 1
            if x & 0x100:  # If overflow
                x ^= self.primitive
        
        # Extend exp table for modulo operations
        for i in range(255, 512):
            self.exp_table[i] = self.exp_table[i - 255]
    
    def multiply(self, a, b):
        """Multiply two numbers in GF(2^8)"""
        if a == 0 or b == 0:
            return 0
        return self.exp_table[self.log_table[a] + self.log_table[b]]
    
    def divide(self, a, b):
        """Divide two numbers in GF(2^8)"""
        if a == 0:
            return 0
        if b == 0:
            raise ZeroDivisionError("Division by zero in GF(2^8)")
        return self.exp_table[(self.log_table[a] - self.log_table[b]) % 255]
    
    def power(self, a, n):
        """Raise a to the power of n in GF(2^8)"""
        if a == 0:
            return 0
        return self.exp_table[(self.log_table[a] * n) % 255]
    
    def inverse(self, a):
        """Find multiplicative inverse of a in GF(2^8)"""
        if a == 0:
            raise ZeroDivisionError("Zero has no inverse")
        return self.exp_table[255 - self.log_table[a]]


class Polynomial:
    """Polynomial in GF(2^8)"""
    
    def __init__(self, coefficients, gf):
        """
        Initialize polynomial with coefficients (highest degree first)
        coefficients: list of integers in GF(2^8)
        """
        self.gf = gf
        # Remove leading zeros
        while len(coefficients) > 1 and coefficients[0] == 0:
            coefficients = coefficients[1:]
        self.coeffs = coefficients
    
    def degree(self):
        """Return degree of polynomial"""
        return len(self.coeffs) - 1
    
    def __getitem__(self, i):
        """Get coefficient at degree i (0 is constant term)"""
        idx = len(self.coeffs) - 1 - i
        if idx < 0 or idx >= len(self.coeffs):
            return 0
        return self.coeffs[idx]
    
    def multiply_scalar(self, scalar):
        """Multiply polynomial by scalar"""
        return Polynomial([self.gf.multiply(c, scalar) for c in self.coeffs], self.gf)
    
    def multiply(self, other):
        """Multiply two polynomials"""
        result = [0] * (len(self.coeffs) + len(other.coeffs) - 1)
        
        for i, c1 in enumerate(self.coeffs):
            for j, c2 in enumerate(other.coeffs):
                result[i + j] ^= self.gf.multiply(c1, c2)
        
        return Polynomial(result, self.gf)
    
    def divide(self, divisor):
        """
        Divide polynomial by divisor
        Returns (quotient, remainder)
        """
        # Make a copy of coefficients
        remainder = list(self.coeffs)
        
        # Calculate quotient coefficients
        divisor_lead_inv = self.gf.inverse(divisor.coeffs[0])
        
        for i in range(len(self.coeffs) - len(divisor.coeffs) + 1):
            if remainder[i] != 0:
                # Calculate quotient coefficient
                coeff = self.gf.multiply(remainder[i], divisor_lead_inv)
                
                # Subtract divisor * coeff from remainder
                for j, div_coeff in enumerate(divisor.coeffs):
                    remainder[i + j] ^= self.gf.multiply(div_coeff, coeff)
        
        # The remainder starts after the quotient part
        separator = len(self.coeffs) - len(divisor.coeffs) + 1
        return Polynomial(remainder[separator:], self.gf)
    
    def __repr__(self):
        return f"Polynomial({self.coeffs})"
