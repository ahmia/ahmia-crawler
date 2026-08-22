"""
サイト死活判定のための共通ユーティリティ関数群
========================================
クロール失敗を記録し、一定回数連続で失敗したサイトを
「死亡」とみなして is_alive: false を立てる。

設計方針:
- 1回の失敗だけでは死亡と判定しない
  （Tor回線の一時的な不調、タイムアウト、運営者側の
    一時的なメンテナンス等と区別がつかないため）
- 連続 FAILURE_THRESHOLD 回失敗して初めて死亡と判定する
- 成功時のリセット処理は明示的には不要
  （index_item()側のindex操作による全項目上書きで、
    consecutive_failures / is_alive フィールドごと自然に消えるため）
- ①（crawler側のerrback）②（index側の定期巡回バッチ）の
  両方から、本モジュールの関数を呼び出す想定
"""

import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


# ==========================
# 設定パラメータ
# ==========================

# 連続何回失敗したら死亡とみなすか
# 60秒のタイムアウト設定を踏まえ、一時的な不調をノイズとして
# 吸収できるだけの余裕を持たせた値。実データでの検証により調整すること。
FAILURE_THRESHOLD = 3


def build_failure_update_script(threshold=FAILURE_THRESHOLD):
    """
    Elasticsearchのupdate APIに渡す、失敗記録用のPainlessスクリプトを組み立てる。

    処理内容:
      1. consecutive_failures を +1 する（無ければ1から開始）
      2. last_failed_at に現在時刻を記録する
      3. consecutive_failures が閾値に達したら is_alive を false にする

    Returns:
        dict: es.update() の script引数にそのまま渡せる形式
    """
    script_source = """
        ctx._source.consecutive_failures =
            (ctx._source.consecutive_failures == null ? 0 : ctx._source.consecutive_failures) + 1;
        ctx._source.last_failed_at = params.now;
        if (ctx._source.consecutive_failures >= params.threshold) {
            ctx._source.is_alive = false;
        }
    """
    return {
        "source": script_source,
        "lang": "painless",
        "params": {
            "now": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'),
            "threshold": threshold,
        },
    }


def record_crawl_failure(es, index_name, doc_id, url, threshold=FAILURE_THRESHOLD):
    """
    既存ドキュメントに対して、クロール失敗を1回分記録する。

    既存ドキュメントが存在しない場合（一度も成功したことがないURL）は
    記録する対象が無いため、何もしない。

    Args:
        es: Elasticsearchクライアント
        index_name: 対象インデックス名
        doc_id: ドキュメントID（url のsha1ハッシュ）
        url: 対象URL（ログ出力用）
        threshold: 死亡と判定する連続失敗回数

    Returns:
        bool: 記録処理を実行したらTrue、対象が存在せず何もしなければFalse
    """
    try:
        exists = es.exists(index=index_name, id=doc_id)
    except Exception:
        logger.exception(f"死活チェック中にESへの接続に失敗しました: {url}")
        return False

    if not exists:
        # 一度も成功したことがないURL。記録する対象が無いのでスキップ。
        return False

    script = build_failure_update_script(threshold)

    try:
        es.update(index=index_name, id=doc_id, script=script)
        logger.info(f"クロール失敗を記録しました: {url}")
        return True
    except Exception:
        logger.exception(f"死活フラグの更新に失敗しました: {url}")
        return False


def compute_doc_id(url):
    """
    URLからドキュメントIDを計算する。
    既存のindex_item()と同じロジック（sha1）に合わせている。
    """
    import hashlib
    return hashlib.sha1(url.encode('utf-8')).hexdigest()