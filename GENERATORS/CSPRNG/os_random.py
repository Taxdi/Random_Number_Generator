"""
Générateur système (os.urandom)

Interface fournie par le système d'exploitation, s'appuyant sur
des sources d'entropie matérielles et logicielles (/dev/urandom
sous Linux, CryptGenRandom sous Windows).

Couramment utilisé comme générateur cryptographiquement sûr en pratique.
"""

import os


def os_generate_bytes(n):
    """Génère n octets véritablement aléatoires via le système."""
    return os.urandom(n)


def os_next_int32():
    """Retourne un entier aléatoire de 32 bits."""
    return int.from_bytes(os.urandom(4), "big")


def os_next_float():
    """Retourne un flottant aléatoire dans [0, 1)."""
    return os_next_int32() / (2**32)


if __name__ == "__main__":
    print("os.urandom - 10 nombres 32-bit :")
    for _ in range(10):
        print(f"  {os_next_int32()}")
    data = os_generate_bytes(16)
    print(f"\n16 octets : {data.hex()}")
