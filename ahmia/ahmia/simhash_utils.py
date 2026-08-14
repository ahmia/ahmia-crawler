"""
SimHashによる近似重複検出のためのユーティリティ関数群

n=3（文字trigram）を採用。根拠は以下の先行研究:
Oguni, Seki, Hirate. "Character 3-gram Mover's Distance:
An Effective Method for Detecting Near-duplicate Japanese-language
Recipes" arXiv:1912.05171, 2019.
"""

import hashlib
from collections import Counter

# ==========================
# 設定パラメータ
# ==========================

SIMHASH_N = 3      # n-gramサイズ
SIMHASH_BITS = 64  # フィンガープリントのビット数


def make_ngrams(text, n=SIMHASH_N):
    """
    文字n-gram（shingle）のリストを生成する

    例: make_ngrams("gift", n=3) -> ["gif", "ift"]
    """
    if len(text) < n:
        return [text] if text else []
    return [text[i:i + n] for i in range(len(text) - n + 1)]


def _hash_ngram(ngram, bits=SIMHASH_BITS):
    """
    1つのn-gramを、指定ビット数の整数ハッシュ値に変換する
    """
    digest = hashlib.md5(ngram.encode('utf-8')).digest()
    return int.from_bytes(digest[:bits // 8], byteorder='big')


def compute_simhash(text, n=SIMHASH_N, bits=SIMHASH_BITS):
    """
    テキストからSimHash値（整数）を計算する
    """
    ngrams = make_ngrams(text, n)
    if not ngrams:
        return 0

    counts = Counter(ngrams)
    votes = [0] * bits

    for ngram, weight in counts.items():
        h = _hash_ngram(ngram, bits)
        for i in range(bits):
            bit = (h >> i) & 1
            if bit == 1:
                votes[i] += weight
            else:
                votes[i] -= weight

    fingerprint = 0
    for i in range(bits):
        if votes[i] > 0:
            fingerprint |= (1 << i)

    return fingerprint


def hamming_distance(hash1, hash2):
    """
    2つのSimHash値のハミング距離（異なるビット数）を計算する
    """
    return bin(hash1 ^ hash2).count('1')
