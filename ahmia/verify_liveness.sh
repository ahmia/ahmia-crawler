#!/bin/bash
# 使い方: bash verify_liveness.sh sample_is_alive_false.json
# 1URLにつき3回試行し、1回でも成功すればALIVEと判定する
# （死活判定システム側の「3回連続失敗」に対応する、緩やかな基準）

FILE=$1
PROXY="http://127.0.0.1:15000"
ATTEMPTS=3

python3 -c "
import json
with open('$FILE') as f:
    data = json.load(f)
urls = [hit['_source']['url'] for hit in data['hits']['hits']]
for u in urls:
    print(u)
" > _urls_tmp.txt

echo "ファイル: $FILE"
echo "URL,結果,成功回数/試行回数"

while read -r url; do
    success=0
    for i in $(seq 1 $ATTEMPTS); do
        code=$(curl -s -x "$PROXY" --max-time 30 -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        if echo "$code" | grep -qE "^[2-5]"; then
            success=$((success+1))
        fi
        sleep 1
    done
    if [ "$success" -ge 1 ]; then
        echo "$url,ALIVE,$success/$ATTEMPTS"
    else
        echo "$url,DEAD,$success/$ATTEMPTS"
    fi
done < _urls_tmp.txt

rm -f _urls_tmp.txt
