# Hash_DRBG - Simple Deterministic Random Bit Generator

## Overview

This implementation demonstrates a **simplified Hash-based Deterministic Random Bit Generator (Hash_DRBG)**, a cryptographically secure pseudorandom number generator (CSPRNG) based on the **SHA-256 hash function**.

Unlike the more complex HMAC_DRBG specified in NIST SP 800-90A, this simplified version uses only SHA-256 to demonstrate the core principles of deterministic random bit generation in an easy-to-understand manner.

## Algorithm Description

### Mathematical Foundation

Hash_DRBG is based on the **SHA-256 cryptographic hash function**, which provides:
- **One-way property**: Given an output, it is computationally infeasible to find the input
- **Collision resistance**: It is computationally infeasible to find two different inputs that produce the same output
- **Avalanche effect**: A small change in input produces a completely different output

### Core Components

The DRBG maintains an internal state consisting of:
- **seed**: The internal state value (32 bytes for SHA-256)
- **counter**: Tracks the number of generate requests to ensure state uniqueness

### DRBG Operations

#### 1. Instantiate ([Hash_DRBG.py:20-36](Hash_DRBG.py#L20-L36))

Initializes the DRBG with entropy input:
```python
drbg = Simple_Hash_DRBG(
    entropy=os.urandom(32)  # 256 bits minimum
)
```

**Process**:
1. Verify entropy is at least 32 bytes (256 bits)
2. Initialize: seed = SHA256(entropy)
3. Set counter = 0

#### 2. Generate ([Hash_DRBG.py:38-70](Hash_DRBG.py#L38-L70))

Produces pseudorandom output:
```python
random_bytes = drbg.generate(32)           # Generate 32 random bytes
random_bits = drbg.generate_bits(1000)     # Generate 1000 random bits
random_int = drbg.randint(1, 100)          # Random integer in [1, 100]
```

**Process**:
1. Initialize output buffer and temporary counter
2. Generate output: repeatedly compute chunk = SHA256(seed || temp_counter)
3. Accumulate chunks until we have enough bytes
4. Update internal state: seed = SHA256(seed || counter)
5. Increment counter

#### 3. Reseed ([Hash_DRBG.py:131-143](Hash_DRBG.py#L131-L143))

Adds fresh entropy to maintain security:
```python
drbg.reseed(entropy=os.urandom(32))
```

**Process**:
1. Combine old seed with new entropy
2. Update seed = SHA256(old_seed || new_entropy)
3. Reset counter = 0

#### 4. Update State Function ([Hash_DRBG.py:72-80](Hash_DRBG.py#L72-L80))

Internal state update mechanism (called after each generation):
```python
# Update formula:
seed = SHA256(seed || counter)
counter = counter + 1
```

## Implementation Details

### Security Strength

Using **SHA-256** as the hash function:
- **Security strength**: 256 bits
- **Entropy input**: Minimum 256 bits (32 bytes)
- **Output block size**: 32 bytes per hash operation
- **State size**: 32 bytes (seed) + 4 bytes (counter)

### Key Features

1. **Simplified design**: Uses only SHA-256, no HMAC construction
2. **Easy to understand**: Minimal complexity for educational purposes
3. **Cryptographically secure**: Based on SHA-256's one-way property
4. **Reseed support**: Can incorporate fresh entropy at any time
5. **Deterministic**: Same seed produces same output sequence

### Comparison with HMAC_DRBG

| Property | Simple Hash_DRBG | HMAC_DRBG |
|----------|------------------|-----------|
| **Hash Function** | SHA-256 only | HMAC-SHA-256 |
| **Internal State** | 1 value (seed) | 2 values (V, Key) |
| **Complexity** | Low | Medium |
| **NIST Compliance** | Simplified version | Full compliance |
| **Update Steps** | 1 hash operation | 2-4 HMAC operations |
| **Code Lines** | ~220 | ~310 |
| **Best For** | Learning, understanding | Production use |

## How It Works - Step by Step

### Initialization
```
1. entropy = os.urandom(32)          → 32 random bytes
2. seed = SHA256(entropy)             → Initial internal state
3. counter = 0                        → Request counter
```

### Generation
```
1. temp_counter = 0
2. output = ""
3. while output_length < requested:
   - chunk = SHA256(seed || temp_counter)
   - output += chunk
   - temp_counter += 1
4. result = output[0:requested_length]
5. Update state:
   - counter += 1
   - seed = SHA256(seed || counter)
```

### Why It's Secure
- **Forward security**: After state update, previous outputs cannot be determined
- **Prediction resistance**: Cannot predict future outputs from current output
- **One-way function**: SHA-256 is irreversible

## Statistical Tests

The implementation includes statistical tests to verify randomness quality:

### 1. Bit Distribution Test
- Counts frequency of '0' and '1' bits
- **Expected result**: Approximately 50% each

### 2. Pattern Analysis
- Analyzes distribution of bits
- **Expected result**: Uniform distribution

## Security Properties

### 1. Cryptographic Security
- Based on SHA-256's one-way property
- Computationally secure if SHA-256 is secure
- Simple construction reduces attack surface

### 2. Prediction Resistance
Given all previous outputs, predicting the next output requires breaking SHA-256.

### 3. Forward Security
After each state update (seed = SHA256(seed || counter)), the previous seed cannot be recovered.

### 4. Limitations
- **Not NIST standardized**: Simplified educational version
- **Less robust than HMAC_DRBG**: No key separation
- **Entropy dependency**: Security depends entirely on initial entropy quality

## Comparison with Other Generators

| Property | Hash_DRBG (Simple) | HMAC_DRBG | BBS | LCG | MT19937 |
|----------|-------------------|-----------|-----|-----|---------|
| **Cryptographic Security** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Prediction Resistance** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Simplicity** | ✓✓✓ | ✓✓ | ✓ | ✓✓✓ | ✓✓ |
| **Speed** | Fast | Fast | Slow | Very Fast | Very Fast |
| **NIST Standardized** | ✗ | ✓ | ✗ | ✗ | ✗ |
| **Educational Value** | ✓✓✓ | ✓✓ | ✓ | ✓ | ✓ |

## Usage Examples

### Basic Usage
```python
import os
from Hash_DRBG import Simple_Hash_DRBG

# Instantiate with system entropy
drbg = Simple_Hash_DRBG(entropy=os.urandom(32))

# Generate random bytes
random_bytes = drbg.generate(32)
print(f"Random bytes: {random_bytes.hex()}")

# Generate random bits
bits = drbg.generate_bits(1000)
print(f"First 50 bits: {bits[:50]}")

# Generate random integer
random_num = drbg.randint(1, 100)
print(f"Random number [1-100]: {random_num}")
```

### Cryptographic Key Generation
```python
# Generate AES-256 key
aes_key = drbg.generate(32)  # 256 bits

# Generate IV for AES-CBC
iv = drbg.generate(16)  # 128 bits

# Generate nonce for AES-GCM
nonce = drbg.generate(12)  # 96 bits
```

### Periodic Reseeding
```python
# Generate many random values
for i in range(1000):
    random_bytes = drbg.generate(32)

    # Reseed every 100 requests (example)
    if i % 100 == 0:
        fresh_entropy = os.urandom(32)
        drbg.reseed(fresh_entropy)
```

## Running the Demonstration

```bash
python GENERATORS/CSPRNG/Hash_DRBG.py
```

**Expected Output**:
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

💡 How does it work?
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

## Visualization

### State Evolution
```
Initial State:
entropy → [SHA256] → seed₀

First Generation:
seed₀ + 0 → [SHA256] → output₁
seed₀ + counter → [SHA256] → seed₁

Second Generation:
seed₁ + 0 → [SHA256] → output₂
seed₁ + counter → [SHA256] → seed₂

...and so on
```

### Security Guarantee
```
Given: output₁, output₂, ..., outputₙ
Find: seedₙ₊₁ (to predict outputₙ₊₁)

This requires inverting SHA256, which is computationally infeasible.
```

## References

1. **NIST SP 800-90A Rev. 1**: "Recommendation for Random Number Generation Using Deterministic Random Bit Generators" (January 2015)
   - [Official NIST Publication](https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final)
   - This implementation is a simplified educational version, not fully NIST-compliant

2. **FIPS 180-4**: "Secure Hash Standard (SHS)" - SHA-256 specification
   - [NIST FIPS 180-4](https://csrc.nist.gov/publications/detail/fips/180/4/final)

3. Bellare, M., & Rogaway, P. (1993). "Random Oracles are Practical: A Paradigm for Designing Efficient Protocols."

## Best Practices

1. **Use sufficient entropy**: Always provide at least 256 bits (32 bytes) of entropy
2. **Source entropy properly**: Use cryptographically secure sources like `os.urandom()`
3. **Reseed periodically**: Consider reseeding after a large number of requests
4. **Protect internal state**: Keep seed and counter secure in memory
5. **Use for education**: This is a simplified version - use HMAC_DRBG or CTR_DRBG for production

## When to Use This Implementation

### ✓ Good For:
- **Learning**: Understanding DRBG principles
- **Education**: Teaching cryptographic concepts
- **Prototyping**: Quick random number generation for testing
- **Non-critical applications**: Where simplicity is valued

### ✗ Not Recommended For:
- **Production systems**: Use NIST-approved HMAC_DRBG or CTR_DRBG
- **High-security applications**: Use fully standardized implementations
- **Compliance requirements**: NIST/FIPS compliance requires approved algorithms

## Limitations and Considerations

- **Simplified design**: Not fully NIST SP 800-90A compliant
- **Entropy dependency**: Security entirely depends on initial entropy quality
- **Deterministic**: Given the same seed, produces the same output (by design)
- **No additional input**: Unlike NIST DRBG, doesn't support additional input per request
- **Educational purpose**: Designed for understanding, not production use

---

**Implementation**: [Hash_DRBG.py](Hash_DRBG.py)
**Based on**: SHA-256 hash function
**Security Strength**: 256 bits (theoretical)
**Purpose**: Educational demonstration of DRBG principles