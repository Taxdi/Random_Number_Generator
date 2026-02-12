"""
Attaque : Récupération de la graine LCG

Modèle de menace :
    - L'attaquant connaît les paramètres publics du LCG (a, c, m)
    - L'attaquant dispose d'un chiffré et d'un fragment de texte clair
      (known-plaintext attack via chiffrement XOR avec keystream LCG)
    - L'espace de graine est petit (16 bits pour la démo)

Algorithme :
    1. Chiffrer un message avec XOR(message, keystream_LCG)
    2. Récupérer le keystream via XOR(clair connu, chiffré correspondant)
    3. Recherche exhaustive de la graine sur [0, 2^16)
    4. Vérifier que le keystream généré correspond

Condition de succès :
    La graine retrouvée permet de déchiffrer l'intégralité du message.
"""

from GENERATORS import lcg_generate_bytes


def lcg_encrypt(plaintext, seed, a, c, m):
    """
    Chiffre un message par XOR avec le keystream du LCG.

    Args:
        plaintext : bytes du message clair
        seed      : graine du LCG
        a, c, m   : paramètres du LCG

    Returns:
        (ciphertext, keystream)
    """
    keystream, _ = lcg_generate_bytes(len(plaintext), seed, a, c, m)
    ciphertext = bytes(p ^ k for p, k in zip(plaintext, keystream))
    return ciphertext, keystream


def recover_lcg_seed(known_plain, known_cipher, a, c, m, seed_space=2**16):
    """
    Récupère la graine du LCG par recherche exhaustive.

    Args:
        known_plain  : fragment de texte clair connu (bytes)
        known_cipher : fragment de chiffré correspondant (bytes)
        a, c, m      : paramètres du LCG
        seed_space   : taille de l'espace de recherche (défaut 2^16)

    Returns:
        graine trouvée (int) ou None si échec
    """
    # Keystream attendu = clair XOR chiffré
    expected_keystream = bytes(p ^ c_ for p, c_ in zip(known_plain, known_cipher))

    for candidate_seed in range(seed_space):
        candidate_keystream, _ = lcg_generate_bytes(len(expected_keystream), candidate_seed, a, c, m)
        if candidate_keystream == expected_keystream:
            return candidate_seed

    return None


def demo_lcg_seed_recovery():
    """
    Démonstration complète de l'attaque de récupération de graine LCG.

    Returns:
        dict avec les résultats de l'attaque
    """
    # Paramètres du LCG (espace de graine réduit pour la démo)
    a, c, m = 1103515245, 12345, 2**16  # m = 2^16 pour brute-force rapide
    secret_seed = 42424

    # Message secret
    message = b"Ceci est un message secret chiffre avec un LCG vulnerable!"

    print("=" * 65)
    print(" ATTAQUE : Récupération de graine LCG ".center(65, "="))
    print("=" * 65)
    print(f"\n  Paramètres LCG : a={a}, c={c}, m={m}")
    print(f"  Graine secrète : {secret_seed}")
    print(f"  Message clair  : {message.decode()}")

    # Étape 1 : chiffrement
    ciphertext, _ = lcg_encrypt(message, secret_seed, a, c, m)
    print(f"\n  [1] Chiffrement XOR avec keystream LCG")
    print(f"      Chiffré (hex) : {ciphertext[:32].hex()}...")

    # Étape 2 : l'attaquant connaît les 10 premiers octets
    known_length = 10
    known_plain = message[:known_length]
    known_cipher = ciphertext[:known_length]
    print(f"\n  [2] Known-plaintext : {known_length} premiers octets connus")
    print(f"      Clair connu : {known_plain}")

    # Étape 3 : brute-force
    print(f"\n  [3] Recherche exhaustive sur {m} graines possibles...")
    recovered_seed = recover_lcg_seed(known_plain, known_cipher, a, c, m)

    if recovered_seed is not None:
        print(f"      Graine trouvée : {recovered_seed}")

        # Étape 4 : déchiffrement complet
        decrypted, _ = lcg_encrypt(ciphertext, recovered_seed, a, c, m)
        print(f"\n  [4] Déchiffrement du message complet :")
        print(f"      {decrypted.decode()}")

        success = (decrypted == message)
        print(f"\n  Résultat : {'SUCCÈS' if success else 'ÉCHEC'}")
        print(f"  Message intégralement déchiffré : {success}")
        if recovered_seed != secret_seed:
            print(f"  Note : graine équivalente trouvée ({recovered_seed} != {secret_seed})")
            print(f"         (plusieurs graines produisent le même keystream sur les bits bas)")
    else:
        success = False
        decrypted = None
        print("      ÉCHEC : graine non trouvée")

    print("=" * 65)

    return {
        "secret_seed": secret_seed,
        "recovered_seed": recovered_seed,
        "success": success,
        "message": message,
        "decrypted": decrypted,
        "ciphertext": ciphertext,
    }


if __name__ == "__main__":
    demo_lcg_seed_recovery()
