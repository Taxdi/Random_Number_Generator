# Hash_DRBG - Générateur de Bits Aléatoires Déterministe Simple

## Vue d'ensemble

Cette implémentation démontre un **générateur de bits aléatoires déterministe simplifié basé sur SHA-256 (Hash_DRBG)**, un générateur de nombres pseudo-aléatoires cryptographiquement sécurisé (CSPRNG) basé sur la **fonction de hachage SHA-256**.

Contrairement au HMAC_DRBG plus complexe spécifié dans NIST SP 800-90A, cette version simplifiée utilise uniquement SHA-256 pour démontrer les principes fondamentaux de la génération de bits aléatoires déterministe de manière facile à comprendre.

## Description de l'algorithme

### Fondements mathématiques

Hash_DRBG est basé sur la **fonction de hachage cryptographique SHA-256**, qui fournit :
- **Propriété à sens unique** : Étant donné une sortie, il est calculatoirement infaisable de retrouver l'entrée
- **Résistance aux collisions** : Il est calculatoirement infaisable de trouver deux entrées différentes produisant la même sortie
- **Effet d'avalanche** : Un petit changement dans l'entrée produit une sortie complètement différente

### Composants principaux

Le DRBG maintient un état interne composé de :
- **seed** : La valeur d'état interne (32 octets pour SHA-256)
- **counter** : Suit le nombre de requêtes de génération pour assurer l'unicité de l'état

### Opérations du DRBG

#### 1. Instantiation ([Hash_DRBG.py:20-36](Hash_DRBG.py#L20-L36))

Initialise le DRBG avec une entrée d'entropie :
```python
drbg = Simple_Hash_DRBG(
    entropy=os.urandom(32)  # 256 bits minimum
)
```

**Processus** :
1. Vérifier que l'entropie fait au moins 32 octets (256 bits)
2. Initialiser : seed = SHA256(entropy)
3. Définir counter = 0

#### 2. Génération ([Hash_DRBG.py:38-70](Hash_DRBG.py#L38-L70))

Produit une sortie pseudo-aléatoire :
```python
random_bytes = drbg.generate(32)           # Générer 32 octets aléatoires
random_bits = drbg.generate_bits(1000)     # Générer 1000 bits aléatoires
random_int = drbg.randint(1, 100)          # Entier aléatoire dans [1, 100]
```

**Processus** :
1. Initialiser le tampon de sortie et le compteur temporaire
2. Générer la sortie : calculer répétitivement chunk = SHA256(seed || temp_counter)
3. Accumuler les chunks jusqu'à avoir assez d'octets
4. Mettre à jour l'état interne : seed = SHA256(seed || counter)
5. Incrémenter le compteur

#### 3. Reseed ([Hash_DRBG.py:131-143](Hash_DRBG.py#L131-L143))

Ajoute de l'entropie fraîche pour maintenir la sécurité :
```python
drbg.reseed(entropy=os.urandom(32))
```

**Processus** :
1. Combiner l'ancien seed avec la nouvelle entropie
2. Mettre à jour seed = SHA256(old_seed || new_entropy)
3. Réinitialiser counter = 0

#### 4. Fonction de mise à jour d'état ([Hash_DRBG.py:72-80](Hash_DRBG.py#L72-L80))

Mécanisme de mise à jour de l'état interne (appelé après chaque génération) :
```python
# Formule de mise à jour :
seed = SHA256(seed || counter)
counter = counter + 1
```

## Détails d'implémentation

### Force de sécurité

En utilisant **SHA-256** comme fonction de hachage :
- **Force de sécurité** : 256 bits
- **Entrée d'entropie** : Minimum 256 bits (32 octets)
- **Taille de bloc de sortie** : 32 octets par opération de hachage
- **Taille d'état** : 32 octets (seed) + 4 octets (counter)

### Fonctionnalités clés

1. **Conception simplifiée** : Utilise uniquement SHA-256, pas de construction HMAC
2. **Facile à comprendre** : Complexité minimale à des fins éducatives
3. **Cryptographiquement sécurisé** : Basé sur la propriété à sens unique de SHA-256
4. **Support de reseed** : Peut incorporer de l'entropie fraîche à tout moment
5. **Déterministe** : Le même seed produit la même séquence de sortie

### Comparaison avec HMAC_DRBG

| Propriété | Simple Hash_DRBG | HMAC_DRBG |
|-----------|------------------|-----------|
| **Fonction de hachage** | SHA-256 uniquement | HMAC-SHA-256 |
| **État interne** | 1 valeur (seed) | 2 valeurs (V, Key) |
| **Complexité** | Faible | Moyenne |
| **Conformité NIST** | Version simplifiée | Conformité totale |
| **Étapes de mise à jour** | 1 opération de hachage | 2-4 opérations HMAC |
| **Lignes de code** | ~220 | ~310 |
| **Idéal pour** | Apprentissage, compréhension | Usage en production |

## Comment ça marche - Étape par étape

### Initialisation
```
1. entropy = os.urandom(32)          → 32 octets aléatoires
2. seed = SHA256(entropy)             → État interne initial
3. counter = 0                        → Compteur de requêtes
```

### Génération
```
1. temp_counter = 0
2. output = ""
3. while output_length < requested:
   - chunk = SHA256(seed || temp_counter)
   - output += chunk
   - temp_counter += 1
4. result = output[0:requested_length]
5. Mise à jour de l'état :
   - counter += 1
   - seed = SHA256(seed || counter)
```

### Pourquoi c'est sécurisé
- **Sécurité avant** : Après la mise à jour de l'état, les sorties précédentes ne peuvent pas être déterminées
- **Résistance à la prédiction** : Impossible de prédire les sorties futures à partir de la sortie actuelle
- **Fonction à sens unique** : SHA-256 est irréversible

## Tests statistiques

L'implémentation inclut des tests statistiques pour vérifier la qualité de l'aléa :

### 1. Test de distribution des bits
- Compte la fréquence des bits '0' et '1'
- **Résultat attendu** : Environ 50% de chaque

### 2. Analyse des motifs
- Analyse la distribution des bits
- **Résultat attendu** : Distribution uniforme

## Propriétés de sécurité

### 1. Sécurité cryptographique
- Basé sur la propriété à sens unique de SHA-256
- Calculatoirement sécurisé si SHA-256 est sécurisé
- Construction simple réduit la surface d'attaque

### 2. Résistance à la prédiction
Étant donné toutes les sorties précédentes, prédire la prochaine sortie nécessite de casser SHA-256.

### 3. Sécurité avant
Après chaque mise à jour d'état (seed = SHA256(seed || counter)), le seed précédent ne peut pas être récupéré.

### 4. Limitations
- **Pas standardisé NIST** : Version éducative simplifiée
- **Moins robuste que HMAC_DRBG** : Pas de séparation de clé
- **Dépendance à l'entropie** : La sécurité dépend entièrement de la qualité de l'entropie initiale

## Comparaison avec d'autres générateurs

| Propriété | Hash_DRBG (Simple) | HMAC_DRBG | BBS | LCG | MT19937 |
|-----------|-------------------|-----------|-----|-----|---------|
| **Sécurité cryptographique** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Résistance à la prédiction** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Simplicité** | ✓✓✓ | ✓✓ | ✓ | ✓✓✓ | ✓✓ |
| **Vitesse** | Rapide | Rapide | Lent | Très rapide | Très rapide |
| **Standardisé NIST** | ✗ | ✓ | ✗ | ✗ | ✗ |
| **Valeur éducative** | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓ |

## Exemples d'utilisation

### Usage basique
```python
import os
from Hash_DRBG import Simple_Hash_DRBG

# Instantier avec entropie système
drbg = Simple_Hash_DRBG(entropy=os.urandom(32))

# Générer des octets aléatoires
random_bytes = drbg.generate(32)
print(f"Octets aléatoires : {random_bytes.hex()}")

# Générer des bits aléatoires
bits = drbg.generate_bits(1000)
print(f"Premiers 50 bits : {bits[:50]}")

# Générer un entier aléatoire
random_num = drbg.randint(1, 100)
print(f"Nombre aléatoire [1-100] : {random_num}")
```

### Génération de clés cryptographiques
```python
# Générer une clé AES-256
aes_key = drbg.generate(32)  # 256 bits

# Générer un IV pour AES-CBC
iv = drbg.generate(16)  # 128 bits

# Générer un nonce pour AES-GCM
nonce = drbg.generate(12)  # 96 bits
```

### Reseed périodique
```python
# Générer beaucoup de valeurs aléatoires
for i in range(1000):
    random_bytes = drbg.generate(32)

    # Reseed tous les 100 requêtes (exemple)
    if i % 100 == 0:
        fresh_entropy = os.urandom(32)
        drbg.reseed(fresh_entropy)
```

## Exécution de la démonstration

```bash
python GENERATORS/CSPRNG/Hash_DRBG.py
```

**Sortie attendue** :
```
============================================================
Simple Hash_DRBG - Demonstration
============================================================

1. Creating generator with random entropy
   Entropy: a3f8c9...
✓ Generator initialized with seed: 307c57dc3335e553...

2. Generating 16 random bytes
   Result: 4b31c1d600f6a7725fed43c66fad2e21

3. Generating 1000 bits
   First 80 bits: 0110110111101010...
   Statistics: 511 zeros, 489 ones
   Proportion: 51.1% zeros, 48.9% ones

4. Generating 10 integers between 1 and 100
   Results: [28, 31, 32, 62, 56, 35, 21, 20, 51, 93]

5. Reseeding with new entropy
   New entropy: 067c40f0...
✓ Generator reseeded with new seed: 905ea8bb32b85584...

6. Generating after reseed
   Result: 6791c0a3f3bef6208c29742d5b7494ca

============================================================
✓ Demonstration complete!
============================================================

How does it work?
------------------------------------------------------------
1. Start with a SEED (internal state) = SHA256(entropy)
2. To generate:
   - Calculate SHA256(seed + counter)
   - Repeat until we have enough bytes
   - Update seed = SHA256(seed + counter)
3. Seed changes after each generation → unpredictable
4. SHA256 is irreversible → secure

🔒 Why is it secure?
------------------------------------------------------------
- Impossible to calculate seed from outputs (SHA256)
- Impossible to predict next outputs
- Seed changes after each use
```

## Visualisation

### Évolution de l'état
```
État initial :
entropy → [SHA256] → seed₀

Première génération :
seed₀ + 0 → [SHA256] → output₁
seed₀ + counter → [SHA256] → seed₁

Deuxième génération :
seed₁ + 0 → [SHA256] → output₂
seed₁ + counter → [SHA256] → seed₂

...et ainsi de suite
```

### Garantie de sécurité
```
Donné : output₁, output₂, ..., outputₙ
Trouver : seedₙ₊₁ (pour prédire outputₙ₊₁)

Cela nécessite d'inverser SHA256, ce qui est calculatoirement infaisable.
```

## Références

1. **NIST SP 800-90A Rev. 1** : "Recommendation for Random Number Generation Using Deterministic Random Bit Generators" (Janvier 2015)
   - [Publication officielle NIST](https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final)
   - Cette implémentation est une version éducative simplifiée, pas entièrement conforme NIST

2. **FIPS 180-4** : "Secure Hash Standard (SHS)" - Spécification SHA-256
   - [NIST FIPS 180-4](https://csrc.nist.gov/publications/detail/fips/180/4/final)

3. Bellare, M., & Rogaway, P. (1993). "Random Oracles are Practical: A Paradigm for Designing Efficient Protocols."

## Bonnes pratiques

1. **Utiliser suffisamment d'entropie** : Toujours fournir au moins 256 bits (32 octets) d'entropie
2. **Source d'entropie appropriée** : Utiliser des sources cryptographiquement sécurisées comme `os.urandom()`
3. **Reseed périodique** : Envisager de reseed après un grand nombre de requêtes
4. **Protéger l'état interne** : Garder seed et counter sécurisés en mémoire
5. **Utiliser pour l'éducation** : Ceci est une version simplifiée - utiliser HMAC_DRBG ou CTR_DRBG pour la production

## Quand utiliser cette implémentation

### ✓ Bon pour :
- **Apprentissage** : Comprendre les principes du DRBG
- **Éducation** : Enseigner les concepts cryptographiques
- **Prototypage** : Génération rapide de nombres aléatoires pour les tests
- **Applications non critiques** : Où la simplicité est valorisée

### ✗ Non recommandé pour :
- **Systèmes de production** : Utiliser HMAC_DRBG ou CTR_DRBG approuvés NIST
- **Applications hautement sécurisées** : Utiliser des implémentations entièrement standardisées
- **Exigences de conformité** : La conformité NIST/FIPS nécessite des algorithmes approuvés

## Limitations et considérations

- **Conception simplifiée** : Pas entièrement conforme à NIST SP 800-90A
- **Dépendance à l'entropie** : La sécurité dépend entièrement de la qualité de l'entropie initiale
- **Déterministe** : Le même seed produit la même sortie (par conception)
- **Pas d'entrée additionnelle** : Contrairement au DRBG NIST, ne supporte pas d'entrée additionnelle par requête
- **But éducatif** : Conçu pour la compréhension, pas pour l'usage en production

---

**Implémentation** : [Hash_DRBG.py](Hash_DRBG.py)
**Basé sur** : Fonction de hachage SHA-256
**Force de sécurité** : 256 bits (théorique)
**But** : Démonstration éducative des principes DRBG
