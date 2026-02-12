"""
Linear Congruential Generator (LCG)

Générateur pseudo-aléatoire basé sur la relation de récurrence :
    X_{n+1} = (a * X_n + c) mod m

Paramètres par défaut : ceux de glibc.
Le LCG est rapide mais présente de faibles propriétés statistiques
et n'offre aucune sécurité cryptographique.
"""

# Paramètres glibc par défaut
DEFAULT_A = 1103515245
DEFAULT_C = 12345
DEFAULT_M = 2**31


def lcg_next(state, a=DEFAULT_A, c=DEFAULT_C, m=DEFAULT_M):
    """
    Calcule le prochain état du LCG et retourne la valeur.

    Returns:
        (valeur, nouvel_état)
    """
    new_state = (a * state + c) % m
    return new_state, new_state


def lcg_next_float(state, a=DEFAULT_A, c=DEFAULT_C, m=DEFAULT_M):
    """
    Retourne un flottant dans [0, 1) et le nouvel état.

    Returns:
        (flottant, nouvel_état)
    """
    val, state = lcg_next(state, a, c, m)
    return val / m, state


def lcg_generate_bytes(n, seed, a=DEFAULT_A, c=DEFAULT_C, m=DEFAULT_M):
    """
    Génère n octets pseudo-aléatoires.

    Returns:
        (bytes, état_final)
    """
    state = seed % m
    result = bytearray(n)
    for i in range(n):
        state = (a * state + c) % m
        result[i] = state & 0xFF
    return bytes(result), state


def lcg_generate_sequence(n, seed, a=DEFAULT_A, c=DEFAULT_C, m=DEFAULT_M):
    """
    Génère une séquence de n entiers pseudo-aléatoires.

    Returns:
        (liste d'entiers, état_final)
    """
    state = seed % m
    values = []
    for _ in range(n):
        state = (a * state + c) % m
        values.append(state)
    return values, state


if __name__ == "__main__":
    seed = 42
    print("LCG - 10 premiers nombres :")
    state = seed
    for _ in range(10):
        val, state = lcg_next(state)
        print(f"  {val}")
    data, _ = lcg_generate_bytes(16, seed=42)
    print(f"\n16 octets : {data.hex()}")
