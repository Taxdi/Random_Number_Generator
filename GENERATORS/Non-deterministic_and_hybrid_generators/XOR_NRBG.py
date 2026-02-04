def xor_nrbg(state):
    """
    Générateur pseudo-aléatoire XOR (XORShift32)
    :param state: état interne (int != 0)
    :return: (nouvel_etat, nombre_aleatoire)
    """
    if state == 0:
        raise ValueError("L'état ne doit pas être 0")

    x = state & 0xFFFFFFFF
    x ^= (x << 13) & 0xFFFFFFFF
    x ^= (x >> 17)
    x ^= (x << 5) & 0xFFFFFFFF

    return x & 0xFFFFFFFF, x & 0xFFFFFFFF


state = 123456789

for _ in range(5):
    state, rnd = xor_nrbg(state)
    print(rnd)