"""
HMAC_DRBG - HMAC-based Deterministic Random Bit Generator
Based on NIST SP 800-90A Rev. 1

This implementation provides a cryptographically secure pseudorandom number generator
with the following security properties:
- Prediction resistance: Cannot predict future outputs
- Backtracking resistance: Cannot determine previous outputs from current state
"""

import hmac
import hashlib
from typing import Optional


class HMAC_DRBG:
    """
    HMAC-based Deterministic Random Bit Generator (HMAC_DRBG)

    Implements NIST SP 800-90A HMAC_DRBG with SHA-256 as the hash function.
    Provides 256-bit security strength.

    Attributes:
        V: Internal state value (seed)
        Key: HMAC key
        reseed_counter: Counter tracking iterations since last reseed
        reseed_interval: Maximum number of requests between reseeds (default: 10000)
    """

    def __init__(self, entropy: bytes, nonce: Optional[bytes] = None,
                 personalization: Optional[bytes] = None):
        """
        Instantiate the DRBG with initial entropy.

        Args:
            entropy: Initial entropy input (should be >= 256 bits / 32 bytes for SHA-256)
            nonce: Optional nonce value (recommended: >= 128 bits / 16 bytes)
            personalization: Optional personalization string
        """
        self.hash_func = hashlib.sha256
        self.outlen = self.hash_func().digest_size  # 32 bytes for SHA-256
        self.reseed_interval = 10000

        # Initialize internal state
        self._instantiate(entropy, nonce, personalization)

    def _instantiate(self, entropy: bytes, nonce: Optional[bytes] = None,
                     personalization: Optional[bytes] = None):
        """
        HMAC_DRBG Instantiate Process (NIST SP 800-90A Section 10.1.2.3)
        """
        # Construct seed_material = entropy || nonce || personalization
        seed_material = entropy
        if nonce:
            seed_material += nonce
        if personalization:
            seed_material += personalization

        # Initial values: Key = 0x00...00, V = 0x01...01
        self.Key = b'\x00' * self.outlen
        self.V = b'\x01' * self.outlen

        # Update internal state with seed material
        self._update(seed_material)

        # Initialize reseed counter
        self.reseed_counter = 1

    def _update(self, provided_data: Optional[bytes] = None):
        """
        HMAC_DRBG Update Function (NIST SP 800-90A Section 10.1.2.2)

        Updates the internal state (V and Key) using the provided data.

        Args:
            provided_data: Optional data to incorporate into the state
        """
        # Step 1: K = HMAC(K, V || 0x00 || provided_data)
        h = hmac.new(self.Key, self.V + b'\x00', self.hash_func)
        if provided_data:
            h.update(provided_data)
        self.Key = h.digest()

        # Step 2: V = HMAC(K, V)
        self.V = hmac.new(self.Key, self.V, self.hash_func).digest()

        # Step 3: If provided_data is present
        if provided_data:
            # K = HMAC(K, V || 0x01 || provided_data)
            h = hmac.new(self.Key, self.V + b'\x01', self.hash_func)
            h.update(provided_data)
            self.Key = h.digest()

            # V = HMAC(K, V)
            self.V = hmac.new(self.Key, self.V, self.hash_func).digest()

    def reseed(self, entropy: bytes, additional_input: Optional[bytes] = None):
        """
        Reseed the DRBG with fresh entropy.

        Args:
            entropy: Fresh entropy input (should be >= 256 bits / 32 bytes)
            additional_input: Optional additional input
        """
        # Construct seed_material = entropy || additional_input
        seed_material = entropy
        if additional_input:
            seed_material += additional_input

        # Update internal state
        self._update(seed_material)

        # Reset reseed counter
        self.reseed_counter = 1

    def generate(self, num_bytes: int, additional_input: Optional[bytes] = None) -> Optional[bytes]:
        """
        Generate pseudorandom bytes.

        Args:
            num_bytes: Number of random bytes to generate
            additional_input: Optional additional input

        Returns:
            Random bytes of length num_bytes, or None if reseed is required
        """
        # Check if reseed is required
        if self.reseed_counter > self.reseed_interval:
            print("Warning: Reseed required (reseed_counter exceeded)")
            return None

        # If additional_input is provided, update state
        if additional_input:
            self._update(additional_input)

        # Generate random bytes
        temp = b''
        while len(temp) < num_bytes:
            self.V = hmac.new(self.Key, self.V, self.hash_func).digest()
            temp += self.V

        # Truncate to requested length
        random_bytes = temp[:num_bytes]

        # Update state
        self._update(additional_input)

        # Increment reseed counter
        self.reseed_counter += 1

        return random_bytes

    def generate_bits(self, num_bits: int, additional_input: Optional[bytes] = None) -> Optional[str]:
        """
        Generate pseudorandom bits as a string.

        Args:
            num_bits: Number of random bits to generate
            additional_input: Optional additional input

        Returns:
            String of '0' and '1' characters, or None if reseed is required
        """
        # Calculate number of bytes needed
        num_bytes = (num_bits + 7) // 8

        # Generate random bytes
        random_bytes = self.generate(num_bytes, additional_input)
        if random_bytes is None:
            return None

        # Convert bytes to bit string
        bit_string = ''.join(format(byte, '08b') for byte in random_bytes)

        # Truncate to requested length
        return bit_string[:num_bits]

    def randint(self, a: int, b: int, additional_input: Optional[bytes] = None) -> Optional[int]:
        """
        Generate a random integer in range [a, b].

        Args:
            a: Lower bound (inclusive)
            b: Upper bound (inclusive)
            additional_input: Optional additional input

        Returns:
            Random integer in [a, b], or None if reseed is required
        """
        if a > b:
            raise ValueError("Lower bound must be <= upper bound")

        range_size = b - a + 1
        num_bits = range_size.bit_length()

        # Generate random bits until we get a value in range
        max_attempts = 1000
        for _ in range(max_attempts):
            bit_string = self.generate_bits(num_bits, additional_input)
            if bit_string is None:
                return None

            value = int(bit_string, 2)
            if value < range_size:
                return a + value

        raise RuntimeError("Failed to generate random integer in range")


def demonstrate_hmac_drbg():
    """Demonstrate HMAC_DRBG usage with statistical tests."""
    print("=" * 70)
    print("HMAC_DRBG - NIST SP 800-90A Demonstration")
    print("=" * 70)
    print()

    # 1. Instantiate with entropy
    print("1. Instantiating HMAC_DRBG with entropy...")
    import os
    entropy = os.urandom(32)  # 256 bits of entropy
    nonce = os.urandom(16)     # 128 bits nonce
    personalization = b"HMAC_DRBG_Demo_2026"

    drbg = HMAC_DRBG(entropy, nonce, personalization)
    print(f"   Entropy: {entropy.hex()[:32]}...")
    print(f"   Nonce: {nonce.hex()}")
    print(f"   Personalization: {personalization.decode()}")
    print()

    # 2. Generate random bytes
    print("2. Generating 32 random bytes...")
    random_bytes = drbg.generate(32)
    print(f"   Random bytes: {random_bytes.hex()}")
    print()

    # 3. Generate random bits
    print("3. Generating 10000 random bits for statistical analysis...")
    bits = drbg.generate_bits(10000)

    # Statistical test 1: Count zeros and ones
    zero_count = bits.count('0')
    one_count = bits.count('1')
    print(f"   Total bits: {len(bits)}")
    print(f"   Zero count: {zero_count} ({zero_count/len(bits)*100:.2f}%)")
    print(f"   One count: {one_count} ({one_count/len(bits)*100:.2f}%)")
    print()

    # Statistical test 2: Average number of zeros in subsequences of length 1000
    print("4. Statistical Test: Average zeros per 1000-bit subsequence")
    summation = 0
    count = 0
    for i in range(len(bits) - 1000):
        summation += bits[i:i+1000].count("0")
        count += 1
    average = summation / count
    print(f"   Expected: ~500")
    print(f"   Actual: {average:.2f}")
    print(f"   Deviation: {abs(500 - average):.2f} ({abs(500-average)/500*100:.2f}%)")
    print()

    # Statistical test 3: Frequency of 4-bit patterns
    print("5. Statistical Test: 4-bit pattern distribution")
    from itertools import product
    subseq_four = [''.join(nums) for nums in product('01', repeat=4)]
    freq = {subseq: 0 for subseq in subseq_four}

    for i in range(len(bits) - 4):
        pattern = bits[i:i+4]
        if pattern in freq:
            freq[pattern] += 1

    expected = (len(bits) - 4) / 16
    print(f"   Expected frequency per pattern: ~{expected:.0f}")
    print(f"   {'Pattern':<10} {'Count':<10} {'Deviation':<10}")
    print(f"   {'-'*30}")

    max_deviation = 0
    for pattern in sorted(freq.keys()):
        deviation = abs(freq[pattern] - expected)
        max_deviation = max(max_deviation, deviation)
        print(f"   {pattern:<10} {freq[pattern]:<10} {deviation:>8.2f}")

    print(f"\n   Maximum deviation: {max_deviation:.2f} ({max_deviation/expected*100:.2f}%)")
    print()

    # 6. Generate random integers
    print("6. Generating random integers in range [1, 100]...")
    random_ints = [drbg.randint(1, 100) for _ in range(10)]
    print(f"   Random integers: {random_ints}")
    print()

    # 7. Reseed demonstration
    print("7. Reseeding with fresh entropy...")
    fresh_entropy = os.urandom(32)
    drbg.reseed(fresh_entropy)
    print(f"   Fresh entropy: {fresh_entropy.hex()[:32]}...")
    print(f"   Reseed counter reset to: {drbg.reseed_counter}")

    # Generate after reseed
    random_bytes_after = drbg.generate(16)
    print(f"   Random bytes after reseed: {random_bytes_after.hex()}")
    print()

    print("=" * 70)
    print("Demonstration complete!")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_hmac_drbg()
