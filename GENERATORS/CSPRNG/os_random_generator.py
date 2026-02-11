"""
os.urandom - OS Random Number Generator
Uses the operating system's entropy source to generate
cryptographically secure random bytes.

Source:
    - Linux: /dev/urandom (kernel CSPRNG entropy pool)
    - Windows: CryptGenRandom
    - macOS: /dev/urandom (Yarrow)
"""

import os


def os_urandom_bytes(n_bytes):
    """
    Generate random bytes via os.urandom.

    Args:
        n_bytes: number of bytes to generate

    Returns:
        Cryptographically secure bytes
    """
    return os.urandom(n_bytes)


def os_urandom_integers(n, bits=32):
    """
    Generate random integers via os.urandom.

    Args:
        n: number of integers
        bits: number of bits per integer (8, 16, 32, 64...)

    Returns:
        List of n random integers
    """
    bytes_per_int = (bits + 7) // 8
    random_bytes = os.urandom(n * bytes_per_int)

    results = []
    for i in range(n):
        start = i * bytes_per_int
        end = start + bytes_per_int
        value = int.from_bytes(random_bytes[start:end], 'big')
        results.append(value)

    return results


def demonstration():
    """Simple demonstration of os.urandom."""
    print("=" * 60)
    print("os.urandom - Demonstration")
    print("=" * 60)
    print()

    # 1. Generate random bytes
    print("1. Generating 16 random bytes")
    random_bytes = os_urandom_bytes(16)
    print(f"   Hex:   {random_bytes.hex()}")
    print(f"   Bytes: {list(random_bytes)}")
    print()

    # 2. Generate random integers
    print("2. Generating 5 random 32-bit integers")
    random_ints = os_urandom_integers(5, bits=32)
    print(f"   Results: {random_ints}")
    print()

    # 3. Generate random integers with different bit sizes
    print("3. Different bit sizes")
    print(f"   8-bit  (0-255):          {os_urandom_integers(5, bits=8)}")
    print(f"   16-bit (0-65535):         {os_urandom_integers(5, bits=16)}")
    print(f"   32-bit (0-4294967295):    {os_urandom_integers(5, bits=32)}")
    print()

    # 4. Statistical test on 1000 bytes
    print("4. Statistical test on 1000 bytes")
    data = os_urandom_bytes(1000)
    bits = ''.join(format(byte, '08b') for byte in data)
    zero_count = bits.count('0')
    one_count = bits.count('1')
    print(f"   Total bits: {len(bits)}")
    print(f"   Zeros: {zero_count} ({zero_count/len(bits)*100:.1f}%)")
    print(f"   Ones:  {one_count} ({one_count/len(bits)*100:.1f}%)")
    print()

    print("=" * 60)
    print("Demonstration complete!")
    print("=" * 60)


if __name__ == "__main__":
    demonstration()
