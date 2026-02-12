"""
Mersenne Twister (MT19937)

Implémentation complète du générateur pseudo-aléatoire MT19937.
État interne de 624 mots de 32 bits, période de 2^19937 - 1.

L'état est représenté par un dict {"mt": list[int], "index": int}.

Excellentes propriétés statistiques mais INADAPTÉ aux usages
cryptographiques car l'état interne peut être reconstruit
à partir de 624 sorties consécutives.
"""

# Constantes MT19937
N = 624
M = 397
MATRIX_A = 0x9908B0DF
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7FFFFFFF
MASK_32 = 0xFFFFFFFF


def mt_init(seed=5489):
    """
    Initialise l'état interne du MT à partir d'une graine.

    Returns:
        dict {"mt": list[int], "index": int}
    """
    mt = [0] * N
    mt[0] = seed & MASK_32
    for i in range(1, N):
        mt[i] = (1812433253 * (mt[i - 1] ^ (mt[i - 1] >> 30)) + i) & MASK_32
    return {"mt": mt, "index": N}


def mt_twist(state):
    """
    Génère les N prochains mots de l'état interne (twist).
    Modifie l'état en place.
    """
    mt = state["mt"]
    for i in range(N):
        x = (mt[i] & UPPER_MASK) | (mt[(i + 1) % N] & LOWER_MASK)
        x_a = x >> 1
        if x & 1:
            x_a ^= MATRIX_A
        mt[i] = mt[(i + M) % N] ^ x_a
    state["index"] = 0


def temper(y):
    """Applique la fonction de tempering (diffusion des bits)."""
    y ^= (y >> 11)
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= (y >> 18)
    return y


def untemper(y):
    """Inverse la fonction de tempering. Utilisé pour l'attaque de reconstruction."""
    # Inverse y ^= (y >> 18)
    y ^= (y >> 18)

    # Inverse y ^= (y << 15) & 0xEFC60000
    y ^= (y << 15) & 0xEFC60000

    # Inverse y ^= (y << 7) & 0x9D2C5680
    tmp = y
    tmp = y ^ ((tmp << 7) & 0x9D2C5680)
    tmp = y ^ ((tmp << 7) & 0x9D2C5680)
    tmp = y ^ ((tmp << 7) & 0x9D2C5680)
    tmp = y ^ ((tmp << 7) & 0x9D2C5680)
    y = tmp

    # Inverse y ^= (y >> 11)
    tmp = y
    tmp = y ^ (tmp >> 11)
    tmp = y ^ (tmp >> 11)
    y = tmp

    return y & MASK_32


def mt_extract(state):
    """
    Extrait le prochain nombre pseudo-aléatoire de 32 bits.

    Returns:
        (valeur_32bits, state)
    """
    if state["index"] >= N:
        mt_twist(state)

    y = state["mt"][state["index"]]
    y = temper(y)
    state["index"] += 1
    return y & MASK_32, state


def mt_next_float(state):
    """
    Retourne un flottant dans [0, 1).

    Returns:
        (flottant, state)
    """
    val, state = mt_extract(state)
    return val / (2**32), state


def mt_generate_bytes(n, seed):
    """
    Génère n octets pseudo-aléatoires.

    Returns:
        (bytes, state)
    """
    state = mt_init(seed)
    result = bytearray()
    while len(result) < n:
        val, state = mt_extract(state)
        result.extend(val.to_bytes(4, "big"))
    return bytes(result[:n]), state


def mt_generate_sequence(n, seed):
    """
    Génère une séquence de n entiers de 32 bits.

    Returns:
        (liste d'entiers, state)
    """
    state = mt_init(seed)
    values = []
    for _ in range(n):
        val, state = mt_extract(state)
        values.append(val)
    return values, state


if __name__ == "__main__":
    state = mt_init(seed=42)
    print("Mersenne Twister - 10 premiers nombres :")
    for _ in range(10):
        val, state = mt_extract(state)
        print(f"  {val}")
    data, _ = mt_generate_bytes(16, seed=42)
    print(f"\n16 octets : {data.hex()}")