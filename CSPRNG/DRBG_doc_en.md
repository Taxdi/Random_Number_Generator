# HMAC_DRBG - NIST SP 800-90A Deterministic Random Bit Generator

## Overview

This implementation demonstrates the **HMAC-based Deterministic Random Bit Generator (HMAC_DRBG)**, a cryptographically secure pseudorandom number generator (CSPRNG) defined in **NIST Special Publication 800-90A Revision 1**.

HMAC_DRBG is one of the most widely used and recommended CSPRNGs, providing provable security properties and used in numerous cryptographic applications including TLS, Bitcoin, and secure key generation.

## Algorithm Description

### Mathematical Foundation

HMAC_DRBG is based on the **HMAC (Hash-based Message Authentication Code)** construction, which provides:
- **Prediction resistance**: Given current and previous outputs, it is computationally infeasible to predict future outputs
- **Backtracking resistance**: Given current state, it is computationally infeasible to determine previous outputs
- **Forward security**: Compromise of current state does not reveal previous outputs

### Core Components

The DRBG maintains an internal state consisting of:
- **V**: A value that is updated each iteration (32 bytes for SHA-256)
- **Key**: The key for the HMAC function (32 bytes for SHA-256)
- **reseed_counter**: Tracks the number of generate requests since last instantiation/reseed

### DRBG Operations

#### 1. Instantiate ([HMAC_DRBG.py:43-58](HMAC_DRBG.py#L43-L58))

Initializes the DRBG with entropy input:
```python
drbg = HMAC_DRBG(
    entropy=os.urandom(32),        # 256 bits minimum
    nonce=os.urandom(16),          # 128 bits recommended
    personalization=b"My_App_2026" # Optional
)
```

**Process**:
1. Construct seed_material = entropy || nonce || personalization
2. Initialize: Key = 0x00...00 (32 bytes), V = 0x01...01 (32 bytes)
3. Update internal state using Update function
4. Set reseed_counter = 1

#### 2. Generate ([HMAC_DRBG.py:103-134](HMAC_DRBG.py#L103-L134))

Produces pseudorandom output:
```python
random_bytes = drbg.generate(32)  # Generate 32 random bytes
random_bits = drbg.generate_bits(10000)  # Generate 10000 random bits
random_int = drbg.randint(1, 100)  # Random integer in [1, 100]
```

**Process**:
1. Check if reseed_counter > reseed_interval (default: 10,000)
2. If additional_input provided, update state
3. Generate output: repeatedly compute V = HMAC(Key, V)
4. Update internal state
5. Increment reseed_counter

#### 3. Reseed ([HMAC_DRBG.py:94-101](HMAC_DRBG.py#L94-L101))

Adds fresh entropy to maintain security:
```python
drbg.reseed(entropy=os.urandom(32))
```

**Process**:
1. Construct seed_material = entropy || additional_input
2. Update internal state with seed_material
3. Reset reseed_counter = 1

#### 4. Update Function ([HMAC_DRBG.py:60-92](HMAC_DRBG.py#L60-L92))

Internal state update mechanism (NIST SP 800-90A Section 10.1.2.2):
```python
# Step 1: Key = HMAC(Key, V || 0x00 || provided_data)
# Step 2: V = HMAC(Key, V)
# Step 3: If provided_data exists:
#         Key = HMAC(Key, V || 0x01 || provided_data)
#         V = HMAC(Key, V)
```

## Implementation Details

### Security Strength

Using **SHA-256** as the hash function:
- **Security strength**: 256 bits
- **Entropy input**: Minimum 256 bits (32 bytes)
- **Nonce**: Recommended 128 bits (16 bytes)
- **Reseed interval**: 10,000 requests (configurable)

### Key Features

1. **Full compliance with NIST SP 800-90A Rev. 1**
2. **Prediction resistance**: Cannot predict future outputs even with knowledge of previous outputs
3. **Backtracking resistance**: Cannot recover previous outputs from current state
4. **Reseed support**: Can incorporate fresh entropy at any time
5. **Personalization**: Supports personalization strings for application-specific instances
6. **Additional input**: Supports additional input for each generate request

## Statistical Tests

The implementation includes comprehensive statistical tests to verify randomness quality:

### 1. Bit Distribution Test
- Counts frequency of '0' and '1' bits
- **Expected result**: Approximately 50% each

### 2. Subsequence Analysis
- Analyzes average number of zeros in 1000-bit windows
- **Expected result**: Approximately 500 zeros per subsequence

### 3. Pattern Frequency Test
- Counts all 16 possible 4-bit patterns (0000 through 1111)
- **Expected result**: Each pattern appears ~625 times in 10,000 bits

## Security Properties

### 1. Cryptographic Security
- **Provably secure** under the assumption that HMAC is a secure PRF (Pseudorandom Function)
- Based on well-studied cryptographic primitives (SHA-256, HMAC)
- Widely reviewed and standardized by NIST

### 2. Prediction Resistance
Given all previous outputs, predicting the next output is computationally infeasible.

### 3. Backtracking Resistance
Compromise of the current internal state does not reveal previous outputs due to the one-way nature of HMAC.

### 4. State Compromise Extension Resistance
After reseeding with fresh entropy, previous state compromise does not affect security.

## Comparison with Other Generators

| Property | HMAC_DRBG | BBS | LCG | MT19937 |
|----------|-----------|-----|-----|---------|
| **Cryptographic Security** | ✓ | ✓ | ✗ | ✗ |
| **Prediction Resistance** | ✓ | ✓ | ✗ | ✗ |
| **Backtracking Resistance** | ✓ | ✓ | ✗ | ✗ |
| **Speed** | Fast | Slow | Very Fast | Very Fast |
| **Standardized** | NIST | Academic | N/A | N/A |
| **Widely Used** | ✓ | ✗ | ✗ | ✓ |

## Usage Examples

### Basic Usage
```python
import os
from HMAC_DRBG import HMAC_DRBG

# Instantiate with system entropy
drbg = HMAC_DRBG(
    entropy=os.urandom(32),
    nonce=os.urandom(16),
    personalization=b"MyApplication"
)

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
for i in range(20000):
    random_bytes = drbg.generate(32)

    # Reseed every 10000 requests
    if drbg.reseed_counter > 10000:
        fresh_entropy = os.urandom(32)
        drbg.reseed(fresh_entropy)
```

## Running the Demonstration

```bash
python CSPRNG/HMAC_DRBG.py
```

**Expected Output**:
```
======================================================================
HMAC_DRBG - NIST SP 800-90A Demonstration
======================================================================

1. Instantiating HMAC_DRBG with entropy...
   Entropy: a3f8c9...
   Nonce: 7b2e1a...
   Personalization: HMAC_DRBG_Demo_2026

2. Generating 32 random bytes...
   Random bytes: [hex output]

3. Generating 10000 random bits for statistical analysis...
   Total bits: 10000
   Zero count: ~5000 (~50.00%)
   One count: ~5000 (~50.00%)

4. Statistical Test: Average zeros per 1000-bit subsequence
   Expected: ~500
   Actual: [value close to 500]
   Deviation: [small value]

5. Statistical Test: 4-bit pattern distribution
   Expected frequency per pattern: ~625
   [Distribution table showing uniform distribution]

6. Generating random integers in range [1, 100]...
   Random integers: [list of random integers]

7. Reseeding with fresh entropy...
   Fresh entropy: [hex value]
   Reseed counter reset to: 1
   Random bytes after reseed: [hex output]
```

## References

1. **NIST SP 800-90A Rev. 1**: "Recommendation for Random Number Generation Using Deterministic Random Bit Generators" (January 2015)
   - [Official NIST Publication](https://csrc.nist.gov/publications/detail/sp/800-90a/rev-1/final)

2. **RFC 6979**: "Deterministic Usage of the Digital Signature Algorithm (DSA) and Elliptic Curve Digital Signature Algorithm (ECDSA)"
   - Uses HMAC_DRBG for deterministic signature generation

3. Bellare, M., & Rogaway, P. (1996). "The Exact Security of Digital Signatures: How to Sign with RSA and Rabin." *Advances in Cryptology — EUROCRYPT '96*.

4. Krawczyk, H., Bellare, M., & Canetti, R. (1997). "HMAC: Keyed-Hashing for Message Authentication." *RFC 2104*.

## Best Practices

1. **Use sufficient entropy**: Always provide at least 256 bits of entropy for SHA-256
2. **Include a nonce**: Use at least 128 bits of nonce for additional security
3. **Reseed periodically**: Reseed after 10,000 requests or after security-critical operations
4. **Use personalization strings**: Different applications should use different personalization
5. **Protect internal state**: Keep V and Key secure in memory
6. **Source entropy properly**: Use cryptographically secure sources like `os.urandom()`

## Limitations and Considerations

- **Entropy dependency**: Security depends on the quality of initial entropy
- **Deterministic**: Given the same seed, produces the same output (by design)
- **Memory**: Requires secure storage of internal state (64 bytes for SHA-256)
- **Performance**: Slower than non-cryptographic PRNGs but acceptable for most applications

---

**Implementation**: [HMAC_DRBG.py](HMAC_DRBG.py)
**Standard**: NIST SP 800-90A Revision 1
**Security Strength**: 256 bits (with SHA-256)
