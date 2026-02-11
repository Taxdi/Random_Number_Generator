"""
Transformée de Box-Muller

Algorithme permettant de transformer deux variables aléatoires
uniformes indépendantes U1, U2 ~ U(0,1) en deux variables
suivant une loi normale standard N(0,1) :

    Z0 = sqrt(-2 * ln(U1)) * cos(2 * pi * U2)
    Z1 = sqrt(-2 * ln(U1)) * sin(2 * pi * U2)
"""

import math
from .mersenne_twister import mt_init, mt_next_float


def box_muller(u1, u2):
    """
    Applique la transformée de Box-Muller.

    Args:
        u1, u2 : deux valeurs uniformes dans (0, 1)

    Returns:
        (z0, z1) : deux valeurs suivant N(0, 1)
    """
    r = math.sqrt(-2.0 * math.log(u1))
    theta = 2.0 * math.pi * u2
    z0 = r * math.cos(theta)
    z1 = r * math.sin(theta)
    return z0, z1


def box_muller_generate(n, seed=42, mu=0.0, sigma=1.0):
    """
    Génère n valeurs suivant N(mu, sigma²) via Box-Muller.
    Utilise le Mersenne Twister comme source uniforme.

    Args:
        n     : nombre de valeurs à générer
        seed  : graine pour le MT
        mu    : moyenne de la distribution
        sigma : écart-type de la distribution

    Returns:
        liste de n flottants
    """
    state = mt_init(seed)
    values = []
    spare = None

    for _ in range(n):
        if spare is not None:
            values.append(mu + sigma * spare)
            spare = None
            continue

        u1, state = mt_next_float(state)
        u2, state = mt_next_float(state)
        while u1 == 0.0:
            u1, state = mt_next_float(state)

        z0, z1 = box_muller(u1, u2)
        values.append(mu + sigma * z0)
        spare = z1

    return values


def box_muller_generate_bytes(n, seed=42):
    """
    Génère n octets en convertissant des valeurs gaussiennes.
    Les valeurs sont mappées sur [0, 255] via clamp [-4, 4].

    Returns:
        bytes de longueur n
    """
    values = box_muller_generate(n, seed=seed)
    result = bytearray(n)
    for i, z in enumerate(values):
        z_clamped = max(-4.0, min(4.0, z))
        val = int((z_clamped + 4.0) / 8.0 * 256)
        result[i] = max(0, min(255, val))
    return bytes(result)


if __name__ == "__main__":
    print("Box-Muller - 10 valeurs N(0,1) :")
    vals = box_muller_generate(10, seed=42)
    for v in vals:
        print(f"  {v:.6f}")

    print(f"\n10 valeurs N(100, 15²) :")
    vals = box_muller_generate(10, seed=42, mu=100, sigma=15)
    for v in vals:
        print(f"  {v:.2f}")
