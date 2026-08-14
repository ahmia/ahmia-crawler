"""
SimHash計算ロジックの動作確認用スクリプト
本番のクロールパイプラインに組み込む前に、
サンプルデータで正しく計算・比較できるかを確認する。
"""

from simhash_utils import compute_simhash, hamming_distance


def preprocess(text):
    """既存のpreprocess関数（脚注除去含むVer2版）をここに複製、
       または本体からimportして使う"""
    import re
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[a-z2-7]{56}\.onion', '', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'\b(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}\b', '', text)
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    text = re.sub(r'\*\[[^\]]+\]:\s*[^*]*', '', text)
    text = re.sub(r'[*#|_\-]{2,}', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def run_tests():
    test_cases = [
        {
            "name": "完全一致",
            "text1": "Gift Card Xpress - Buy cheap gift cards",
            "text2": "Gift Card Xpress - Buy cheap gift cards",
            "expect_distance": 0,
        },
        {
            "name": "空白差のみ",
            "text1": "gift  card    xpress   buy now",
            "text2": "gift card xpress buy now",
            "expect_distance": 0,  # preprocessで吸収されるはず
        },
        {
            "name": "全く別内容",
            "text1": "Buy drugs cannabis weed cocaine heroin",
            "text2": "Legit CC vendors carding fullz dumps",
            "expect_distance": "large",  # 大きく離れているはず
        },
    ]

    print(f"{'テストケース':<15} {'距離':>6} {'判定'}")
    print("-" * 40)

    for case in test_cases:
        c1 = preprocess(case["text1"])
        c2 = preprocess(case["text2"])
        h1 = compute_simhash(c1)
        h2 = compute_simhash(c2)
        dist = hamming_distance(h1, h2)

        if case["expect_distance"] == "large":
            ok = dist > 10
        else:
            ok = dist == case["expect_distance"]

        status = "OK" if ok else "NG ★要確認"
        print(f"{case['name']:<15} {dist:>6}  {status}")


if __name__ == "__main__":
    run_tests()