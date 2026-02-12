"""
NIST SP 800-90A Hash_DRBG (SHA-256)

Implémentation simplifiée du Deterministic Random Bit Generator
basé sur SHA-256, conforme au standard NIST SP 800-90A.

L'état est représenté par un dict {"V": bytes, "C": bytes, "reseed_counter": int}.

Ce CSPRNG offre des garanties contre la prédiction des sorties
futures et supporte le reseed pour rafraîchir l'entropie.
"""

import hashlib
import os

SEED_LEN = 55  # seedlen pour SHA-256 = 440 bits = 55 octets


def _sha256(data):
    """SHA-256 hash."""
    return hashlib.sha256(data).digest()


def _hash_df(input_data, num_bytes):
    """
    Hash derivation function (Hash_df) selon NIST SP 800-90A.
    Dérive num_bytes octets à partir des données d'entrée.
    """
    hash_len = 32
    num_blocks = (num_bytes + hash_len - 1) // hash_len
    result = b""
    for counter in range(1, num_blocks + 1):
        to_hash = counter.to_bytes(1, "big") + num_bytes.to_bytes(4, "big") + input_data
        result += _sha256(to_hash)
    return result[:num_bytes]


def drbg_instantiate(entropy=None, nonce=None, personalization=b""):
    """
    Instancie le DRBG.

    Args:
        entropy          : entropie initiale (bytes). Si None, os.urandom.
        nonce            : nonce (bytes). Si None, os.urandom.
        personalization  : chaîne de personnalisation optionnelle

    Returns:
        state : dict {"V", "C", "reseed_counter"}
    """
    if entropy is None:
        entropy = os.urandom(SEED_LEN)
    if nonce is None:
        nonce = os.urandom(SEED_LEN // 2)

    seed_material = entropy + nonce + personalization
    seed = _hash_df(seed_material, SEED_LEN)

    V = seed
    C = _hash_df(b"\x00" + seed, SEED_LEN)
    return {"V": V, "C": C, "reseed_counter": 1}


def drbg_reseed(state, entropy=None):
    """
    Reseed le DRBG avec de la nouvelle entropie.

    Args:
        state   : état courant
        entropy : nouvelle entropie (bytes). Si None, os.urandom.

    Returns:
        state mis à jour
    """
    if entropy is None:
        entropy = os.urandom(SEED_LEN)

    seed = _hash_df(b"\x01" + state["V"] + entropy, SEED_LEN)
    state["V"] = seed
    state["C"] = _hash_df(b"\x00" + seed, SEED_LEN)
    state["reseed_counter"] = 1
    return state


def drbg_generate(state, num_bytes):
    """
    Génère num_bytes octets pseudo-aléatoires.

    Args:
        state     : état courant
        num_bytes : nombre d'octets à générer

    Returns:
        (output_bytes, state)
    """
    hash_len = 32
    m = (num_bytes + hash_len - 1) // hash_len
    W = b""
    data = state["V"]
    for _ in range(m):
        W += _sha256(data)
        int_data = (int.from_bytes(data, "big") + 1) % (2 ** (len(data) * 8))
        data = int_data.to_bytes(len(state["V"]), "big")
    output = W[:num_bytes]

    # Mise à jour de l'état
    H = _sha256(b"\x03" + state["V"])
    int_v = int.from_bytes(state["V"], "big")
    int_h = int.from_bytes(H, "big")
    int_c = int.from_bytes(state["C"], "big")
    mod = 2 ** (SEED_LEN * 8)
    new_v = (int_v + int_h + int_c + state["reseed_counter"]) % mod
    state["V"] = new_v.to_bytes(SEED_LEN, "big")
    state["reseed_counter"] += 1

    return output, state


def drbg_generate_bytes(n, entropy=None, nonce=None):
    """
    Fonction raccourci : instancie le DRBG et génère n octets.

    Returns:
        bytes de longueur n
    """
    state = drbg_instantiate(entropy=entropy, nonce=nonce)
    output, _ = drbg_generate(state, n)
    return output


if __name__ == "__main__":
    state = drbg_instantiate(entropy=b"A" * 55, nonce=b"B" * 28)
    print("Hash_DRBG (SHA-256) - 32 octets :")
    data, state = drbg_generate(state, 32)
    print(f"  {data.hex()}")
    print(f"\nAprès reseed - 32 octets :")
    state = drbg_reseed(state, b"C" * 55)
    data, state = drbg_generate(state, 32)
    print(f"  {data.hex()}")
