"""
Hash_DRBG - Simple Deterministic Random Bit Generator based on SHA-256
Simplified version to understand the principle
"""

import hashlib
import os


class Simple_Hash_DRBG:
    """
    Random number generator based solely on SHA-256.

    Simple principle:
    1. We have an internal state (seed)
    2. To generate numbers: we hash the state multiple times
    3. After each generation: we update the state
    """

    def __init__(self, entropy: bytes):
        """
        Initialize the generator with entropy.

        Args:
            entropy: Initial random data (at least 32 bytes)
        """
        if len(entropy) < 32:
            raise ValueError("At least 32 bytes of entropy required")

        # Internal state: hash the initial entropy
        self.seed = hashlib.sha256(entropy).digest()

        # Counter to avoid repetition
        self.counter = 0

        print(f"✓ Generator initialized with seed: {self.seed.hex()[:16]}...")

    def generate(self, num_bytes: int) -> bytes:
        """
        Generate random bytes.

        Principle:
        - Hash (seed + counter) to get 32 bytes
        - Repeat until we have enough bytes
        - Update the seed afterwards

        Args:
            num_bytes: Number of bytes to generate

        Returns:
            Random bytes
        """
        output = b''
        temp_counter = 0

        # Generate enough bytes
        while len(output) < num_bytes:
            # Hash (seed + temporary counter)
            data = self.seed + temp_counter.to_bytes(4, 'big')
            chunk = hashlib.sha256(data).digest()
            output += chunk
            temp_counter += 1

        # Truncate to requested size
        result = output[:num_bytes]

        # IMPORTANT: Update internal state
        self._update_state()

        return result

    def _update_state(self):
        """
        Update the internal state so future outputs cannot be predicted.

        Principle: seed = SHA256(seed + counter)
        """
        self.counter += 1
        data = self.seed + self.counter.to_bytes(4, 'big')
        self.seed = hashlib.sha256(data).digest()

    def generate_bits(self, num_bits: int) -> str:
        """
        Generate a string of bits '0' and '1'.

        Args:
            num_bits: Number of bits to generate

        Returns:
            String of '0' and '1'
        """
        # Calculate how many bytes we need
        num_bytes = (num_bits + 7) // 8

        # Generate the bytes
        random_bytes = self.generate(num_bytes)

        # Convert to bits
        bit_string = ''.join(format(byte, '08b') for byte in random_bytes)

        # Truncate to requested length
        return bit_string[:num_bits]

    def randint(self, a: int, b: int) -> int:
        """
        Generate a random integer between a and b (inclusive).

        Args:
            a: Lower bound
            b: Upper bound

        Returns:
            Random integer in [a, b]
        """
        if a > b:
            raise ValueError("a must be <= b")

        range_size = b - a + 1
        num_bits = range_size.bit_length()

        # Generate until we get a number in range
        for _ in range(1000):
            bits = self.generate_bits(num_bits)
            value = int(bits, 2)

            if value < range_size:
                return a + value

        raise RuntimeError("Unable to generate a number in range")

    def reseed(self, new_entropy: bytes):
        """
        Reinitialize the generator with new entropy.

        Args:
            new_entropy: New random data
        """
        # Mix the old seed with new entropy
        combined = self.seed + new_entropy
        self.seed = hashlib.sha256(combined).digest()
        self.counter = 0

        print(f"✓ Generator reseeded with new seed: {self.seed.hex()[:16]}...")


def demonstration():
    """Simple demonstration of the generator."""
    print("=" * 60)
    print("Simple Hash_DRBG - Demonstration")
    print("=" * 60)
    print()

    # 1. Create the generator
    print("1. Creating generator with random entropy")
    entropy = os.urandom(32)  # 32 bytes = 256 bits of entropy
    print(f"   Entropy: {entropy.hex()[:32]}...")
    drbg = Simple_Hash_DRBG(entropy)
    print()

    # 2. Generate bytes
    print("2. Generating 16 random bytes")
    random_bytes = drbg.generate(16)
    print(f"   Result: {random_bytes.hex()}")
    print()

    # 3. Generate bits
    print("3. Generating 1000 bits")
    bits = drbg.generate_bits(1000)
    zero_count = bits.count('0')
    one_count = bits.count('1')
    print(f"   First 80 bits: {bits[:80]}")
    print(f"   Statistics: {zero_count} zeros, {one_count} ones")
    print(f"   Proportion: {zero_count/10:.1f}% zeros, {one_count/10:.1f}% ones")
    print()

    # 4. Generate integers
    print("4. Generating 10 integers between 1 and 100")
    random_ints = [drbg.randint(1, 100) for _ in range(10)]
    print(f"   Results: {random_ints}")
    print()

    # 5. Reseed
    print("5. Reseeding with new entropy")
    new_entropy = os.urandom(32)
    print(f"   New entropy: {new_entropy.hex()[:32]}...")
    drbg.reseed(new_entropy)
    print()

    # 6. Generate after reseed
    print("6. Generating after reseed")
    random_bytes_after = drbg.generate(16)
    print(f"   Result: {random_bytes_after.hex()}")
    print()

    print("=" * 60)
    print("✓ Demonstration complete!")
    print("=" * 60)
    print()

if __name__ == "__main__":
    demonstration()