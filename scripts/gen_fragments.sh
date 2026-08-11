#!/bin/bash
# 构建后生成 fragment 清单 (pagefind 索引生成后调用)
# 用法: gen_fragments.sh <public目录>
set -e
PUB="${1:-public}"
LIST="$PUB/pagefind/fragments.json"
if [ -d "$PUB/pagefind/fragment" ]; then
  # 列出所有 fragment 文件名 (相对路径)
  (cd "$PUB/pagefind" && ls fragment/ | sed 's/^/fragment\//') | python3 -c "import sys,json; print(json.dumps([l.strip() for l in sys.stdin if l.strip()]))" > "$LIST"
  echo "fragments.json: $(cat "$LIST" | python3 -c 'import sys,json; print(len(json.load(sys.stdin)))') 条"
else
  echo "[]" > "$LIST"
  echo "无 fragment 目录"
fi
