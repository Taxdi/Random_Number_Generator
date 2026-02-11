"""
Attaque : Réutilisation de nonce en AES-CTR

Modèle de menace :
    - L'attaquant observe deux chiffrés c1 et c2 produits avec la
      même clé K et le même nonce/IV en mode AES-CTR.
    - L'attaquant connaît (ou devine) un des deux messages clairs.

Algorithme :
    AES-CTR : c = m XOR AES_K(nonce || counter)
    Si même nonce :
        c1 XOR c2 = m1 XOR m2
    Connaissant m1 (ou un fragment), on récupère m2.

Condition de succès :
    L'attaquant récupère le second message à partir du premier
    et des deux chiffrés.

Métriques :
    - Taux de récupération du message
    - Démonstration du crib-dragging
"""

from Crypto.Cipher import AES
import os


def aes_ctr_encrypt(key, nonce, plaintext):
    """
    Chiffre un message en AES-CTR.

    Args:
        key       : clé AES de 16 octets
        nonce     : nonce de 8 octets
        plaintext : message clair (bytes)

    Returns:
        ciphertext (bytes)
    """
    cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    return cipher.encrypt(plaintext)


def xor_bytes(a, b):
    """XOR de deux séquences d'octets (longueur min)."""
    return bytes(x ^ y for x, y in zip(a, b))


def crib_drag(c1_xor_c2, known_fragment, position=0):
    """
    Technique de crib-dragging : glisser un fragment connu le long
    du XOR des chiffrés pour récupérer le message correspondant.

    Args:
        c1_xor_c2      : XOR des deux chiffrés (= m1 XOR m2)
        known_fragment  : fragment connu d'un des deux messages
        position        : position de départ du fragment

    Returns:
        Liste de (position, fragment_récupéré) pour chaque position testée
    """
    results = []
    frag_len = len(known_fragment)

    for pos in range(len(c1_xor_c2) - frag_len + 1):
        # Si on connaît m1[pos:pos+frag_len], on récupère m2[pos:pos+frag_len]
        recovered = xor_bytes(c1_xor_c2[pos:pos + frag_len], known_fragment)
        # Vérifier si le résultat ressemble à du texte
        try:
            text = recovered.decode("ascii")
            if all(c.isprintable() or c in "\n\r\t" for c in text):
                results.append((pos, text))
        except (UnicodeDecodeError, ValueError):
            pass

    return results


def demo_aes_ctr_nonce_reuse():
    """
    Démonstration complète de l'attaque par réutilisation de nonce AES-CTR.

    Returns:
        dict avec les résultats de l'attaque
    """
    print("=" * 65)
    print(" ATTAQUE : Réutilisation de nonce AES-CTR ".center(65, "="))
    print("=" * 65)

    # Paramètres
    key = os.urandom(16)
    nonce = os.urandom(8)  # MÊME nonce pour les deux chiffrements

    m1 = b"Virement de 1000 euros vers le compte de Alice aujourd'hui."
    m2 = b"Le mot de passe du serveur principal est: Sup3rS3cr3t!2026"

    # Padding pour avoir la même longueur
    max_len = max(len(m1), len(m2))
    m1_padded = m1.ljust(max_len)
    m2_padded = m2.ljust(max_len)

    print(f"\n  Clé AES    : {key.hex()}")
    print(f"  Nonce      : {nonce.hex()} (RÉUTILISÉ !)")
    print(f"\n  Message 1  : {m1_padded.decode()}")
    print(f"  Message 2  : {m2_padded.decode()}")

    # Étape 1 : chiffrement avec le même nonce
    c1 = aes_ctr_encrypt(key, nonce, m1_padded)
    c2 = aes_ctr_encrypt(key, nonce, m2_padded)

    print(f"\n  [1] Chiffrement AES-CTR avec le même nonce")
    print(f"      c1 (hex) : {c1[:32].hex()}...")
    print(f"      c2 (hex) : {c2[:32].hex()}...")

    # Étape 2 : XOR des chiffrés = XOR des clairs
    c1_xor_c2 = xor_bytes(c1, c2)
    m1_xor_m2 = xor_bytes(m1_padded, m2_padded)

    print(f"\n  [2] c1 XOR c2 = m1 XOR m2")
    print(f"      c1 XOR c2 == m1 XOR m2 : {c1_xor_c2 == m1_xor_m2}")

    # Étape 3 : connaissant m1, récupérer m2
    print(f"\n  [3] L'attaquant connaît m1 → récupération de m2")
    recovered_m2 = xor_bytes(c1_xor_c2, m1_padded)
    print(f"      m2 récupéré : {recovered_m2.decode()}")
    success_full = (recovered_m2 == m2_padded)

    # Étape 4 : crib-dragging avec un fragment
    print(f"\n  [4] Crib-dragging avec fragment 'mot de passe'")
    crib = b"mot de passe"
    drag_results = crib_drag(c1_xor_c2, crib)
    print(f"      Positions trouvées avec du texte lisible :")
    for pos, text in drag_results[:5]:
        print(f"        pos {pos:3d} : '{text}'")

    success = success_full
    print(f"\n  Résultat : {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"  Message 2 intégralement récupéré : {success_full}")
    print("=" * 65)

    return {
        "m1": m1_padded,
        "m2": m2_padded,
        "recovered_m2": recovered_m2,
        "success": success,
        "crib_results": drag_results,
    }


if __name__ == "__main__":
    demo_aes_ctr_nonce_reuse()
