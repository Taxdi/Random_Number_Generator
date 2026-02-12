"""
Construction XOR NRBG (Non-Random Bit Generator)

Générateur hybride combinant plusieurs générateurs (ou sources)
de bits via une opération XOR bit à bit.

Cette construction vise à améliorer la robustesse : si au moins
une des sources produit de l'aléa de qualité, le résultat
combiné hérite de cette qualité.

    output = source_1 XOR source_2 XOR ... XOR source_n
"""

from ..PRNG_non_cryptographics.lcg import lcg_generate_bytes
from ..PRNG_non_cryptographics.mersenne_twister import mt_generate_bytes
from ..CSPRNG.os_random import os_generate_bytes


def xor_bytes_list(byte_arrays):
    """
    XOR bit à bit d'une liste de séquences d'octets.

    Args:
        byte_arrays : liste de bytes de même longueur

    Returns:
        bytes résultat du XOR
    """
    n = len(byte_arrays[0])
    result = bytearray(n)
    for ba in byte_arrays:
        for i in range(n):
            result[i] ^= ba[i]
    return bytes(result)


def xor_nrbg_generate_bytes(n, seed=42):
    """
    Génère n octets en combinant LCG, MT et os.urandom par XOR.

    Args:
        n    : nombre d'octets à générer
        seed : graine pour les générateurs déterministes

    Returns:
        bytes de longueur n
    """
    lcg_data, _ = lcg_generate_bytes(n, seed=seed)
    mt_data, _ = mt_generate_bytes(n, seed=seed)
    os_data = os_generate_bytes(n)

    return xor_bytes_list([lcg_data, mt_data, os_data])


def xor_nrbg_generate_custom(n, generator_outputs):
    """
    Combine des sorties de générateurs arbitraires par XOR.

    Args:
        n                  : nombre d'octets attendus
        generator_outputs  : liste de bytes (chacun de longueur >= n)

    Returns:
        bytes de longueur n
    """
    return xor_bytes_list([o[:n] for o in generator_outputs])


if __name__ == "__main__":
    print("XOR NRBG (LCG + MT + os.urandom) - 16 octets :")
    data = xor_nrbg_generate_bytes(16, seed=42)
    print(f"  {data.hex()}")

    print("\n10 séquences de 4 octets :")
    for i in range(10):
        chunk = xor_nrbg_generate_bytes(4, seed=42 + i)
        val = int.from_bytes(chunk, "big")
        print(f"  {val}")
