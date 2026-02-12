"""
Tests statistiques pour évaluer la qualité des générateurs de nombres aléatoires.

Tests implémentés :
    1. Entropie de Shannon par octet
    2. Test du chi-carré (χ²) pour l'uniformité des octets
    3. Autocorrélation (lags 1, 2, 4, 8, 16)
    4. Test de Kolmogorov-Smirnov (KS)
"""

import math
from collections import Counter

from scipy import stats
import numpy as np


# =============================================================================
# 1. Entropie de Shannon
# =============================================================================

def shannon_entropy(data):
    """
    Calcule l'entropie de Shannon par octet.

    Une source parfaitement aléatoire de 256 symboles possibles
    a une entropie maximale de 8.0 bits/octet.

    Args:
        data : bytes ou list[int] (valeurs 0-255)

    Returns:
        dict avec 'entropy' (float), 'max_entropy' (8.0), 'ratio' (%)
    """
    if isinstance(data, (bytes, bytearray)):
        data = list(data)

    n = len(data)
    if n == 0:
        return {"entropy": 0.0, "max_entropy": 8.0, "ratio": 0.0}

    counts = Counter(data)
    entropy = 0.0
    for count in counts.values():
        p = count / n
        if p > 0:
            entropy -= p * math.log2(p)

    return {
        "entropy": round(entropy, 6),
        "max_entropy": 8.0,
        "ratio": round(entropy / 8.0 * 100, 2),
    }


# =============================================================================
# 2. Test du Chi-carré
# =============================================================================

def chi_squared_test(data, significance=0.05):
    """
    Test du chi-carré pour l'uniformité des octets.

    H0 : les octets sont uniformément distribués sur [0, 255].
    256 catégories, 255 degrés de liberté.

    Args:
        data        : bytes ou list[int]
        significance : seuil de significativité (défaut 0.05)

    Returns:
        dict avec 'chi2' (statistique), 'p_value', 'passed' (bool),
        'significance', 'degrees_of_freedom'
    """
    if isinstance(data, (bytes, bytearray)):
        data = list(data)

    n = len(data)
    expected = n / 256.0

    # Compter les occurrences de chaque octet
    observed = [0] * 256
    for byte in data:
        observed[byte] += 1

    # Calcul de la statistique chi²
    chi2 = sum((obs - expected) ** 2 / expected for obs in observed)

    # p-value
    df = 255
    p_value = 1.0 - stats.chi2.cdf(chi2, df)

    return {
        "chi2": round(chi2, 4),
        "p_value": round(p_value, 6),
        "passed": p_value > significance,
        "significance": significance,
        "degrees_of_freedom": df,
    }


# =============================================================================
# 3. Autocorrélation
# =============================================================================

def autocorrelation(data, lags=None):
    """
    Calcule les coefficients d'autocorrélation pour différents décalages (lags).

    Un bon PRNG doit avoir des coefficients proches de 0 pour tous les lags.

    Args:
        data : bytes ou list[int]
        lags : liste de décalages à tester (défaut : [1, 2, 4, 8, 16])

    Returns:
        dict avec 'correlations' {lag: coefficient}, 'max_abs' (float),
        'passed' (bool, True si max_abs < 0.05)
    """
    if lags is None:
        lags = [1, 2, 4, 8, 16]

    if isinstance(data, (bytes, bytearray)):
        data = list(data)

    arr = np.array(data, dtype=np.float64)
    n = len(arr)
    mean = np.mean(arr)
    var = np.var(arr)

    if var == 0:
        return {
            "correlations": {lag: 0.0 for lag in lags},
            "max_abs": 0.0,
            "passed": False,
        }

    correlations = {}
    for lag in lags:
        if lag >= n:
            correlations[lag] = 0.0
            continue
        cov = np.mean((arr[:n - lag] - mean) * (arr[lag:] - mean))
        correlations[lag] = round(float(cov / var), 6)

    max_abs = max(abs(v) for v in correlations.values())

    return {
        "correlations": correlations,
        "max_abs": round(max_abs, 6),
        "passed": max_abs < 0.05,
    }


# =============================================================================
# 4. Test de Kolmogorov-Smirnov
# =============================================================================

def ks_test(data, significance=0.05):
    """
    Test de Kolmogorov-Smirnov pour comparer la distribution
    empirique des octets à une distribution uniforme U(0, 255).

    Args:
        data        : bytes ou list[int]
        significance : seuil de significativité (défaut 0.05)

    Returns:
        dict avec 'statistic' (D), 'p_value', 'passed' (bool)
    """
    if isinstance(data, (bytes, bytearray)):
        data = list(data)

    # Normaliser les valeurs sur [0, 1) pour le test KS
    # Division par 256 (et non 255) pour obtenir des valeurs dans [0, 1)
    # compatibles avec la distribution uniforme U(0, 1)
    normalized = (np.array(data, dtype=np.float64) + 0.5) / 256.0

    # Test KS contre une distribution uniforme U(0, 1)
    stat, p_value = stats.kstest(normalized, "uniform")

    return {
        "statistic": round(float(stat), 6),
        "p_value": round(float(p_value), 6),
        "passed": p_value > significance,
        "significance": significance,
    }


# =============================================================================
# Fonction utilitaire : exécuter tous les tests
# =============================================================================

def run_all_tests(data, label=""):
    """
    Exécute les 4 tests statistiques et affiche un tableau résumé.

    Args:
        data  : bytes ou list[int]
        label : nom du générateur (pour l'affichage)

    Returns:
        dict avec les résultats de chaque test
    """
    results = {
        "shannon": shannon_entropy(data),
        "chi2": chi_squared_test(data),
        "autocorrelation": autocorrelation(data),
        "ks": ks_test(data),
    }

    # Affichage formaté
    header = f" Tests statistiques : {label} " if label else " Tests statistiques "
    print(f"\n{'=' * 65}")
    print(f"{header:=^65}")
    print(f"{'=' * 65}")
    print(f"  Taille des données : {len(data)} octets")
    print(f"  {'─' * 61}")

    # Shannon
    s = results["shannon"]
    print(f"  Entropie Shannon     : {s['entropy']:.4f} / {s['max_entropy']:.1f} bits/octet ({s['ratio']}%)")

    # Chi²
    c = results["chi2"]
    status = "PASS" if c["passed"] else "FAIL"
    print(f"  Chi² (df=255)        : χ² = {c['chi2']:.2f}, p = {c['p_value']:.4f}  [{status}]")

    # Autocorrélation
    a = results["autocorrelation"]
    status = "PASS" if a["passed"] else "FAIL"
    corr_str = ", ".join(f"lag{k}={v:.4f}" for k, v in a["correlations"].items())
    print(f"  Autocorrélation      : max|r| = {a['max_abs']:.4f}  [{status}]")
    print(f"    {corr_str}")

    # KS
    k = results["ks"]
    status = "PASS" if k["passed"] else "FAIL"
    print(f"  Kolmogorov-Smirnov   : D = {k['statistic']:.4f}, p = {k['p_value']:.4f}  [{status}]")

    print(f"{'=' * 65}\n")

    return results


if __name__ == "__main__":
    import os as _os

    print("Test avec os.urandom (devrait passer tous les tests) :")
    data = _os.urandom(100_000)
    run_all_tests(data, "os.urandom")

    print("Test avec données biaisées (devrait échouer) :")
    biased = bytes([i % 4 for i in range(100_000)])
    run_all_tests(biased, "biaisé (mod 4)")
