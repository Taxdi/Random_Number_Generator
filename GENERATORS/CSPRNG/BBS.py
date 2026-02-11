import math
from random import randint
from itertools import product

# Paramètres par défaut (p ≡ 3 mod 4, q ≡ 3 mod 4)
DEFAULT_P = 1000003
DEFAULT_Q = 2001911


def bbs_init(seed=None, p=DEFAULT_P, q=DEFAULT_Q):
    M = p * q
    if seed is None:
        seed = randint(2, M - 1)
        while math.gcd(seed, M) != 1:
            seed = randint(2, M - 1)

    if math.gcd(seed, M) != 1:
        raise ValueError(f"La graine {seed} n'est pas coprime avec M={M}")

    return {"state": seed, "M": M, "p": p, "q": q}


def bbs_next_bit(bbs_state):
    bbs_state["state"] = (bbs_state["state"] ** 2) % bbs_state["M"]
    return bbs_state["state"] % 2, bbs_state


def bbs_generate_bits(n, seed=None, p=DEFAULT_P, q=DEFAULT_Q):
    bbs_state = bbs_init(seed, p, q)
    bits = []
    for _ in range(n):
        bit, bbs_state = bbs_next_bit(bbs_state)
        bits.append(bit)
    return bits, bbs_state


def bbs_generate_bitstring(n, seed=None, p=DEFAULT_P, q=DEFAULT_Q):
    bits, _ = bbs_generate_bits(n, seed, p, q)
    return "".join(str(b) for b in bits)


def bbs_generate_bytes(n, seed=None, p=DEFAULT_P, q=DEFAULT_Q):
    bbs_state = bbs_init(seed, p, q)
    result = bytearray(n)
    for i in range(n):
        byte = 0
        for _ in range(8):
            bit, bbs_state = bbs_next_bit(bbs_state)
            byte = (byte << 1) | bit
        result[i] = byte
    return bytes(result)


def bbs_next_int32(bbs_state):
    result = 0
    for _ in range(32):
        bit, bbs_state = bbs_next_bit(bbs_state)
        result = (result << 1) | bit
    return result, bbs_state


def analyze_bbs_sequence(bits_str, subseq_len=1000, pattern_len=4):
    # 1. Moyenne des 0 par sous-séquence
    total_zeros = 0
    count = 0
    for i in range(len(bits_str) - subseq_len):
        total_zeros += bits_str[i:i + subseq_len].count("0")
        count += 1
    avg_zeros = total_zeros / count if count > 0 else 0

    # 2. Fréquence des sous-séquences de longueur pattern_len
    all_patterns = ["".join(nums) for nums in product("01", repeat=pattern_len)]
    freq = {p: 0 for p in all_patterns}
    for i in range(len(bits_str) - pattern_len):
        pattern = bits_str[i:i + pattern_len]
        freq[pattern] += 1

    return {
        "avg_zeros": avg_zeros,
        "expected_zeros": subseq_len / 2,
        "pattern_freq": freq,
    }


if __name__ == "__main__":
    seed = 123456
    n = DEFAULT_P * DEFAULT_Q
    print(f"BBS (M = {DEFAULT_P} x {DEFAULT_Q} = {n})")

    # Génération de 10 000 bits
    bits = bbs_generate_bitstring(10000, seed=seed)
    print(f"\nGénéré {len(bits)} bits")

    # Analyse
    analysis = analyze_bbs_sequence(bits)
    print(f"\nMoyenne de 0 par sous-séquence de 1000 : {analysis['avg_zeros']:.2f}")
    print(f"Attendu (distribution uniforme) : {analysis['expected_zeros']:.1f}")

    print(f"\nFréquence des sous-séquences de longueur 4 :")
    print(f"{'Sous-seq':<12} {'Compte':<8}")
    for pattern, count in analysis["pattern_freq"].items():
        print(f"{pattern:<12} {count:<8}")
