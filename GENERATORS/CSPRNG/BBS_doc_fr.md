# Générateur de Nombres Pseudo-Aléatoires Blum-Blum-Shub (BBS)

## Vue d'ensemble

Cette implémentation démontre l'algorithme **Blum-Blum-Shub (BBS)**, un générateur de nombres pseudo-aléatoires cryptographiquement sûr (CSPRNG) avec des propriétés de sécurité prouvables basées sur la difficulté de la factorisation des entiers.

## Description de l'algorithme

### Fondement mathématique

Le générateur BBS est basé sur le problème des résidus quadratiques. Il utilise :
- Deux grands **nombres premiers de Blum** p et q (nombres premiers ≡ 3 mod 4)
- Un module n = p × q (entier de Blum)
- Une graine x₀ copremière avec n : pgcd(x₀, n) = 1

### Processus de génération

1. **Initialisation** :
   - Sélectionner deux nombres premiers de Blum : p = 1 000 003 et q = 2 001 911
   - Calculer n = p × q = 2 003 917 005 933
   - Choisir une graine aléatoire x₀ copremière avec n

2. **Génération de bits** :
   - Pour chaque itération j : x_j = (x_{j-1})² mod n
   - Extraire le bit de poids faible : bit_j = x_j mod 2
   - La séquence de bits extraits forme la sortie pseudo-aléatoire

3. **Sortie** : Générer 10 000 bits aléatoires

## Détails d'implémentation ([BBS.py](BBS.py))

### Composants clés

```python
p = 1000003          # Premier nombre premier de Blum
q = 2001911          # Deuxième nombre premier de Blum
n = p * q            # Module (entier de Blum)
seed = randint(2, n-1) # Graine initiale (x₀)
```

### Validation de la graine
```python
while gcd(seed, n) != 1:
    seed = randint(2, n-1)
```
Assure que la graine est copremière avec n, ce qui est requis pour la correction de l'algorithme. La graine est choisie dans la plage [2, n-1] pour assurer la sécurité cryptographique.

### Boucle de génération de bits ([BBS.py:15-18](BBS.py#L15-L18))
```python
for _ in range(1, 10000):
    seed = (seed * seed) % n  # x_j = (x_{j-1})² mod n
    bit = seed % 2             # Extraire le LSB
    bits += str(bit)           # Concaténer
```

## Tests statistiques

L'implémentation inclut deux tests statistiques pour vérifier le caractère aléatoire :

### 1. Nombre moyen de zéros dans les sous-séquences ([BBS.py:20-27](BBS.py#L20-L27))
- Analyse toutes les sous-séquences de longueur 1000
- Calcule la fréquence moyenne des bits '0'
- **Résultat attendu** : Environ 500 (pour des bits vraiment aléatoires)
- Compte efficacement les zéros dans chaque sous-séquence de 1000 bits

### 2. Distribution de fréquence des motifs de 4 bits ([BBS.py:32-48](BBS.py#L32-L48))
- Génère tous les 16 motifs possibles de 4 bits (0000 à 1111)
- Compte les occurrences de chaque motif dans la séquence générée
- **Résultat attendu** : Chaque motif devrait apparaître environ 625 fois (10000/16)

## Propriétés de sécurité

1. **Sécurité prouvable** : Le générateur BBS est prouvablement sûr sous l'hypothèse que factoriser de grands nombres est computationnellement difficile
2. **Période** : La séquence a une période maximale de λ(λ(n)) où λ est la fonction de Carmichael
3. **Imprévisibilité** : Étant donnée la séquence de sortie, prédire les bits futurs est aussi difficile que factoriser n

## Extension à trois nombres premiers de Blum

Pour votre modification de thèse utilisant trois nombres premiers de Blum (p, q, r) :

### Modifications proposées
```python
p = 1000003      # Premier nombre premier de Blum
q = 2001911      # Deuxième nombre premier de Blum
r = 3000017      # Troisième nombre premier de Blum
n = p * q * r    # Nouveau module
```

### Considérations
- Le module n sera beaucoup plus grand (meilleure sécurité)
- La période sera différente : λ(λ(n))
- L'analyse de sécurité devra être adaptée
- Le problème de factorisation devient légèrement différent (trois facteurs au lieu de deux)
- La graine doit toujours satisfaire pgcd(graine, n) = 1

## Références

- Blum, L., Blum, M., & Shub, M. (1986). "A Simple Unpredictable Pseudo-Random Number Generator". SIAM Journal on Computing.
- La sécurité de l'algorithme est basée sur le problème de résidualité quadratique.

## Utilisation

```bash
python BBS.py
```

Exemple de sortie :
```
The average number of zeros per subsequence: [valeur]

Frequency of length 4 subsequences:
Subsequence  Count
0000         [compte]
0001         [compte]
...
```
