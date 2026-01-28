# Blum-Blum-Shub (BBS) Pseudorandom Number Generator

## Overview

This implementation demonstrates the **Blum-Blum-Shub (BBS)** algorithm, a cryptographically secure pseudorandom number generator (CSPRNG) with provable security properties based on the difficulty of integer factorization.

## Algorithm Description

### Mathematical Foundation

The BBS generator is based on the quadratic residue problem. It uses:
- Two large **Blum primes** p and q (primes ≡ 3 mod 4)
- A modulus n = p × q (Blum integer)
- A seed x₀ that is coprime with n: gcd(x₀, n) = 1

### Generation Process

1. **Initialization**:
   - Select two Blum primes: p = 1,000,003 and q = 2,001,911
   - Compute n = p × q = 2,003,917,005,933
   - Choose a random seed x₀ coprime to n

2. **Bit Generation**:
   - For each iteration j: x_j = (x_{j-1})² mod n
   - Extract the least significant bit: bit_j = x_j mod 2
   - The sequence of extracted bits forms the pseudorandom output

3. **Output**: Generate 10,000 random bits

## Implementation Details ([BBS.py](BBS.py))

### Key Components

```python
p = 1000003          # First Blum prime
q = 2001911          # Second Blum prime
n = p * q            # Modulus (Blum integer)
seed = randint(2, n-1) # Initial seed (x₀)
```

### Seed Validation
```python
while gcd(seed, n) != 1:
    seed = randint(2, n-1)
```
Ensures the seed is coprime with n, which is required for the algorithm's correctness. The seed is chosen from the range [2, n-1] for cryptographic security.

### Bit Generation Loop ([BBS.py:15-18](BBS.py#L15-L18))
```python
for _ in range(1, 10000):
    seed = (seed * seed) % n  # x_j = (x_{j-1})² mod n
    bit = seed % 2             # Extract LSB
    bits += str(bit)           # Concatenate
```

## Statistical Tests

The implementation includes two statistical tests to verify randomness:

### 1. Average Number of Zeros in Subsequences ([BBS.py:20-27](BBS.py#L20-L27))
- Analyzes all subsequences of length 1000
- Computes the average frequency of '0' bits
- **Expected result**: Approximately 500 (for truly random bits)
- Efficiently counts zeros in each subsequence of 1000 bits

### 2. Frequency Distribution of 4-bit Patterns ([BBS.py:32-48](BBS.py#L32-L48))
- Generates all 16 possible 4-bit patterns (0000 to 1111)
- Counts occurrences of each pattern in the generated sequence
- **Expected result**: Each pattern should appear approximately 625 times (10000/16)

## Security Properties

1. **Provable Security**: The BBS generator is provably secure under the assumption that factoring large numbers is computationally hard
2. **Period**: The sequence has a maximum period of λ(λ(n)) where λ is the Carmichael function
3. **Unpredictability**: Given the output sequence, predicting future bits is as hard as factoring n

## Extension to Three Blum Primes

For your thesis modification using three Blum primes (p, q, r):

### Proposed Changes
```python
p = 1000003      # First Blum prime
q = 2001911      # Second Blum prime
r = 3000017      # Third Blum prime
n = p * q * r    # New modulus
```

### Considerations
- The modulus n will be much larger (better security)
- The period will be different: λ(λ(n))
- Security analysis will need to be adapted
- The factorization problem becomes slightly different (three factors instead of two)
- Seed must still satisfy gcd(seed, n) = 1

## References

- Blum, L., Blum, M., & Shub, M. (1986). "A Simple Unpredictable Pseudo-Random Number Generator". SIAM Journal on Computing.
- The algorithm's security is based on the quadratic residuosity problem.

## Usage

```bash
python BBS.py
```

Output example:
```
The average number of zeros per subsequence: [value]

Frequency of length 4 subsequences:
Subsequence  Count
0000         [count]
0001         [count]
...
```
