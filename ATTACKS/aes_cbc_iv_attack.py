"""
Attaque : IV prévisible en AES-CBC

Modèle de menace :
    - Le système utilise AES-CBC avec un IV prévisible
      (par exemple un compteur incrémental).
    - L'attaquant peut soumettre des messages et observer les chiffrés.
    - L'attaquant connaît le prochain IV qui sera utilisé.

Algorithme :
    En AES-CBC : C_0 = AES_K(P_0 XOR IV)
    Si l'attaquant connaît IV_{next} et veut tester si un message
    cible M_target a été chiffré précédemment avec IV_prev :
        Il soumet P_chosen = IV_{next} XOR IV_prev XOR M_target
        Si C_new[0] == C_prev[0], alors M_target == M_prev

Condition de succès :
    L'attaquant détecte correctement l'égalité entre deux messages
    chiffrés avec des IV différents mais prévisibles.

Métriques :
    - Taux de détection des messages identiques
    - Nombre de requêtes nécessaires
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import os


def aes_cbc_encrypt(key, iv, plaintext):
    """
    Chiffre un message en AES-CBC.

    Args:
        key       : clé AES de 16 octets
        iv        : vecteur d'initialisation de 16 octets
        plaintext : message clair (bytes)

    Returns:
        ciphertext (bytes)
    """
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    return cipher.encrypt(pad(plaintext, AES.block_size))


def xor_bytes(a, b):
    """XOR de deux séquences d'octets."""
    return bytes(x ^ y for x, y in zip(a, b))


# --- Oracle à IV prévisible (état géré par dict) ---

def oracle_init(key=None):
    """
    Crée un oracle de chiffrement avec IV prévisible (compteur).

    Returns:
        dict {"key", "iv_counter"}
    """
    return {
        "key": key if key is not None else os.urandom(16),
        "iv_counter": 0,
    }


def oracle_get_next_iv(oracle):
    """Retourne le prochain IV (prévisible car compteur)."""
    return oracle["iv_counter"].to_bytes(16, "big")


def oracle_encrypt(oracle, plaintext):
    """
    Chiffre le message avec l'IV courant et incrémente le compteur.

    Returns:
        (iv_used, ciphertext, oracle)
    """
    iv = oracle_get_next_iv(oracle)
    oracle["iv_counter"] += 1
    ciphertext = aes_cbc_encrypt(oracle["key"], iv, plaintext)
    return iv, ciphertext, oracle


def detect_equal_plaintexts(oracle, iv_prev, c_prev_block0, m_target):
    """
    Détecte si m_target a été chiffré pour produire c_prev_block0
    avec iv_prev.

    L'attaquant connaît :
        - iv_prev : l'IV utilisé pour le chiffrement précédent
        - c_prev_block0 : le premier bloc du chiffré précédent
        - m_target : le message qu'il veut tester

    Méthode :
        P_chosen = IV_next XOR IV_prev XOR M_target
        Si encrypt(P_chosen) premier bloc == c_prev_block0
        alors m_target == message précédent
    """
    iv_next = oracle_get_next_iv(oracle)

    # Construire le plaintext choisi
    target_padded = pad(m_target, AES.block_size)[:16]
    p_chosen = xor_bytes(xor_bytes(iv_next, iv_prev), target_padded)

    # Chiffrer avec l'oracle
    _, c_new, oracle = oracle_encrypt(oracle, p_chosen)
    c_new_block0 = c_new[:16]

    return c_new_block0 == c_prev_block0, oracle


def demo_aes_cbc_iv_attack():
    """
    Démonstration de l'attaque par IV prévisible en AES-CBC.

    Returns:
        dict avec les résultats de l'attaque
    """
    print("=" * 65)
    print(" ATTAQUE : IV prévisible en AES-CBC ".center(65, "="))
    print("=" * 65)

    oracle = oracle_init()

    # Messages possibles (l'attaquant veut deviner lequel a été chiffré)
    messages = [
        b"Compte valide  ",  # exactement 16 octets (1 bloc)
        b"Compte invalide",
        b"Acces autorise ",
        b"Acces refuse!! ",
    ]

    # Le serveur chiffre un message secret
    secret_message = messages[0]  # "Compte valide  "

    print(f"\n  IV utilisé : compteur incrémental (prévisible)")
    print(f"  Message secret chiffré par le serveur : ???")
    print(f"  Messages candidats :")
    for i, m in enumerate(messages):
        print(f"    [{i}] {m.decode()}")

    # Étape 1 : le serveur chiffre le message secret
    iv_prev, c_prev, oracle = oracle_encrypt(oracle, secret_message)
    c_prev_block0 = c_prev[:16]

    print(f"\n  [1] Chiffrement du message secret")
    print(f"      IV utilisé    : {iv_prev.hex()}")
    print(f"      Chiffré (hex) : {c_prev.hex()}")

    # Étape 2 : l'attaquant teste chaque message candidat
    print(f"\n  [2] L'attaquant teste chaque message candidat...")

    found = None
    tests_count = 0
    for i, candidate in enumerate(messages):
        tests_count += 1
        is_match, oracle = detect_equal_plaintexts(oracle, iv_prev, c_prev_block0, candidate)
        status = "MATCH !" if is_match else "non"
        print(f"      [{i}] '{candidate.decode()}' -> {status}")
        if is_match:
            found = candidate

    success = (found == secret_message)

    print(f"\n  [3] Résultat de l'attaque")
    if found:
        print(f"      Message identifié : '{found.decode()}'")
        print(f"      Nombre de tests   : {tests_count}")
    else:
        print(f"      Aucun message identifié")

    # Démonstration supplémentaire : détection de messages répétés
    print(f"\n  [4] Détection de messages répétés avec IV prévisible")
    oracle2 = oracle_init()
    repeated_messages = [b"Hello World !!! ", b"Message unique! ", b"Hello World !!! ",
                         b"Autre message! !", b"Hello World !!! "]

    encryptions = []
    for msg in repeated_messages:
        iv, ct, oracle2 = oracle_encrypt(oracle2, msg)
        encryptions.append((iv, ct[:16], msg))

    print(f"      Messages chiffrés (5 messages, certains répétés) :")
    detected_pairs = []
    for i in range(len(encryptions)):
        for j in range(i + 1, len(encryptions)):
            if encryptions[i][2] == encryptions[j][2]:
                detected_pairs.append((i, j))

    for i, (iv, ct, msg) in enumerate(encryptions):
        print(f"      [{i}] IV={iv.hex()[:8]}... -> {ct.hex()[:16]}... ({msg.decode()})")

    print(f"\n      Messages identiques détectés aux positions :")
    for i, j in detected_pairs:
        print(f"        [{i}] et [{j}] : même message")

    print(f"\n  Résultat : {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"  Le message secret a été identifié : {success}")
    print("=" * 65)

    return {
        "secret_message": secret_message,
        "found_message": found,
        "success": success,
        "tests_count": tests_count,
        "detected_pairs": detected_pairs,
    }


if __name__ == "__main__":
    demo_aes_cbc_iv_attack()
