from elasticsearch import Elasticsearch, helpers
import hashlib
import re
import traceback
import json

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", "8d_g_J6=fBhej3LVFFlE"),
    verify_certs=False,
    request_timeout=60,      # ★タイムアウトを延長(デフォルトは短め)
    max_retries=3,           # ★一時的な通信エラーはリトライ
    retry_on_timeout=True,
)

INDEX_NAME = "onions-2026-07"


def preprocess(text):
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


def calculate_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def flush(actions, failed_log):
    if not actions:
        return
    success, errors = helpers.bulk(
        es, actions, stats_only=False, raise_on_error=False
    )
    if errors:
        for err in errors:
            failed_log.append(err)
            print("更新失敗:", err)


def update_documents():
    actions = []
    count = 0
    failed_log = []

    documents = helpers.scan(
        client=es,
        index=INDEX_NAME,
        query={"query": {"match_all": {}}},
        scroll="30m",          # ★スクロールタイムアウトを延長
        raise_on_error=True,   # scanのエラーは検知したいのでTrueのまま
    )

    try:
        for doc in documents:
            doc_id = doc["_id"]
            source = doc["_source"]
            content = source.get("content", "")

            if not content:
                continue

            try:
                clean_content = preprocess(content)
                content_hash = calculate_hash(clean_content)
            except Exception as e:
                print(f"前処理失敗: {doc_id} - {e}")
                failed_log.append({"id": doc_id, "stage": "preprocess", "error": str(e)})
                continue

            actions.append({
                "_op_type": "update",
                "_index": INDEX_NAME,
                "_id": doc_id,
                "doc": {
                    "clean_content": clean_content,
                    "content_hash": content_hash,
                },
            })
            count += 1

            if len(actions) >= 100:
                flush(actions, failed_log)
                print(f"{count}件処理済み")
                actions = []

    except Exception as e:
        # ★ここが今回一番重要: クラッシュの詳細を必ず記録する
        print("スクリプトが途中で停止しました。原因:")
        traceback.print_exc()
        with open("crash_log.txt", "w") as f:
            f.write(f"停止時点の処理件数: {count}\n")
            f.write(traceback.format_exc())

    finally:
        # ★クラッシュしても、溜まっていた分は必ずflushする
        flush(actions, failed_log)

        print(f"完了(または中断): {count}件処理を試行しました")
        print(f"失敗件数: {len(failed_log)}")

        with open("failed_log.json", "w") as f:
            json.dump(failed_log, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    update_documents()