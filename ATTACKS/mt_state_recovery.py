"""
Attaque : Reconstruction de l'état interne du Mersenne Twister (MT19937)

Modèle de menace :
    - L'attaquant peut observer 624 sorties consécutives de 32 bits
      du générateur MT19937.
    - L'attaquant connaît l'algorithme (MT19937 est public).

Algorithme :
    1. Collecter 624 sorties de 32 bits du MT cible
    2. Appliquer la fonction untemper() sur chaque sortie pour
       retrouver l'état interne (inverser le tempering)
    3. Créer un clone du MT avec l'état reconstruit
    4. Prédire les sorties futures

Condition de succès :
    Les prédictions du clone correspondent exactement aux sorties
    futures du MT original.
"""

import os

from GENERATORS import mt_init, mt_extract, untemper, N


def clone_mt(outputs):
    """
    Clone un Mersenne Twister à partir de 624 sorties consécutives.

    Args:
        outputs : liste de 624 entiers de 32 bits (sorties observées)

    Returns:
        state dict cloné avec l'état interne reconstruit
    """
    assert len(outputs) == N, f"Besoin de {N} sorties, reçu {len(outputs)}"

    # Créer un état et remplacer les valeurs internes
    cloned = mt_init(seed=0)

    # Reconstruire l'état en inversant le tempering
    for i in range(N):
        cloned["mt"][i] = untemper(outputs[i])

    cloned["index"] = N  # Forcer un twist au prochain extract

    return cloned


def demo_mt_state_recovery():
    """
    Démonstration complète de la reconstruction d'état MT19937.

    Returns:
        dict avec les résultats de l'attaque
    """
    print("=" * 65)
    print(" ATTAQUE : Reconstruction d'état MT19937 ".center(65, "="))
    print("=" * 65)

    # Créer un MT "victime" avec une graine aléatoire
    victim_seed = int.from_bytes(os.urandom(4), "big")
    victim = mt_init(seed=victim_seed)
    print(f"\n  MT victime initialisé (graine inconnue de l'attaquant)")

    # Étape 1 : observer 624 sorties
    print(f"\n  [1] Collecte de 624 sorties consécutives de 32 bits...")
    observed = []
    for _ in range(N):
        val, victim = mt_extract(victim)
        observed.append(val)
    print(f"      Premières sorties observées : {observed[:5]}...")

    # Étape 2 : reconstruire l'état
    print(f"\n  [2] Reconstruction de l'état interne via untemper()...")
    cloned = clone_mt(observed)
    print(f"      État reconstruit avec succès")

    # Étape 3 : prédire les sorties futures
    n_predictions = 1000
    print(f"\n  [3] Prédiction des {n_predictions} prochaines sorties...")

    victim_future = []
    cloned_future = []
    for _ in range(n_predictions):
        v, victim = mt_extract(victim)
        c, cloned = mt_extract(cloned)
        victim_future.append(v)
        cloned_future.append(c)

    # Vérification
    matches = sum(1 for v, c in zip(victim_future, cloned_future) if v == c)
    success_rate = matches / n_predictions * 100

    print(f"      Correspondances : {matches}/{n_predictions} ({success_rate:.1f}%)")
    print(f"\n      Exemples de prédictions :")
    print(f"      {'Victime':>15} | {'Clone':>15} | {'Match':>5}")
    print(f"      {'─' * 15}-+-{'─' * 15}-+-{'─' * 5}")
    for i in range(10):
        match = "OK" if victim_future[i] == cloned_future[i] else "FAIL"
        print(f"      {victim_future[i]:>15} | {cloned_future[i]:>15} | {match:>5}")

    success = (matches == n_predictions)
    print(f"\n  Résultat : {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"  Prédiction parfaite : {success}")
    print("=" * 65)

    return {
        "observed_count": N,
        "predictions_count": n_predictions,
        "matches": matches,
        "success_rate": success_rate,
        "success": success,
    }


if __name__ == "__main__":
    demo_mt_state_recovery()
