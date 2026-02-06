# generators/os_random.py
""" A REPRENDRE
Interface vers générateurs système (os.urandom, secrets)
Source d'entropie de qualité cryptographique fournie par l'OS
"""

import os
import secrets


def os_urandom_bytes(n_bytes):
    """
    Génère octets via os.urandom (source entropie noyau)
    
    Source:
        - Linux: /dev/urandom (pool entropie CSPRNG du noyau)
        - Windows: CryptGenRandom
        - macOS: /dev/urandom (Yarrow)
    
    Paramètres:
        n_bytes: nombre d'octets à générer
    
    Retourne:
        Octets cryptographiquement sécurisés (bytes)
    
    Note: Bloquant sur Linux si entropie insuffisante au boot
    """
    return os.urandom(n_bytes)


def os_urandom_integers(n, bits=32):
    """
    Génère entiers via os.urandom
    
    Paramètres:
        n: nombre d'entiers
        bits: nombre de bits par entier (8, 16, 32, 64...)
    
    Retourne:
        Liste de n entiers
    """
    bytes_per_int = (bits + 7) // 8
    random_bytes = os.urandom(n * bytes_per_int)
    
    results = []
    for i in range(n):
        start = i * bytes_per_int
        end = start + bytes_per_int
        value = int.from_bytes(random_bytes[start:end], 'big')
        results.append(value)
    
    return results


def secrets_bytes(n_bytes):
    """
    Génère octets via module secrets (Python 3.6+)
    
    Plus haut niveau que os.urandom, adapté pour:
        - Tokens de sécurité
        - Mots de passe aléatoires
        - Clés cryptographiques
    
    Paramètres:
        n_bytes: nombre d'octets
    
    Retourne:
        Octets cryptographiquement sécurisés (bytes)
    """
    return secrets.token_bytes(n_bytes)


def secrets_integers(n, bits=32):
    """
    Génère entiers via module secrets
    
    Paramètres:
        n: nombre d'entiers
        bits: bits par entier
    
    Retourne:
        Liste de n entiers
    """
    return [secrets.randbits(bits) for _ in range(n)]


def compare_sources(n_bytes=16):
    """
    Compare les différentes sources système
    
    Utile pour vérifier disponibilité et comportement
    """
    print("Comparaison sources entropie système:")
    print(f"\nos.urandom({n_bytes}):")
    print(f"  {os_urandom_bytes(n_bytes).hex()}")
    
    print(f"\nsecrets.token_bytes({n_bytes}):")
    print(f"  {secrets_bytes(n_bytes).hex()}")
    
    print(f"\nEntiers 32-bits (n=5):")
    print(f"  os.urandom: {os_urandom_integers(5, 32)}")
    print(f"  secrets:    {secrets_integers(5, 32)}")
