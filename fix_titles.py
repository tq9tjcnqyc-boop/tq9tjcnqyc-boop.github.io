#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复标题重复: 思源 setBlockAttrs 更新 title, 去掉多余的「结构」"""
import json, urllib.request, glob, re, os

API = "http://127.0.0.1:6806"
NOTEBOOK = "20260808225839-mm6cxzc"

def api(endpoint, payload):
    req = urllib.request.Request(f"{API}{endpoint}",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

# 找所有有「结构结构」的 md, 提取 title + 对应思源文档ID
# md 文件名 = slug, 但思源文档 ID 是随机 ID... 需要从 slug 找到文档
# 先列笔记本文档, 匹配 slug 属性
r = api("/api/filetree/listDocsByPath", {"notebook": NOTEBOOK, "path": "/"})
files = r.get("data", {}).get("files", [])
print(f"笔记本文档数: {len(files)}")

# 对每个有问题的 md, 找到对应文档(通过 .sy 里的 slug)
fixed = 0
for md_path in glob.glob("/Users/ageha/site/content/posts/*.md"):
    content = open(md_path, encoding="utf-8").read()
    m = re.search(r'^title = "(.*?)"', content, re.M)
    if not m:
        continue
    title = m.group(1)
    if "结构结构" not in title:
        continue
    new_title = title.replace("结构结构", "结构")
    # 找 slug
    slug_m = re.search(r'^slug = "(.*?)"', content, re.M)
    slug = slug_m.group(1) if slug_m else os.path.basename(md_path).replace(".md", "")
    # 在思源文档里找匹配 slug 的
    doc_id = None
    for f in files:
        # 检查 .sy 内容里的 slug
        sy_path = f"/Users/ageha/Documents/文字/data/{NOTEBOOK}/{f['id']}.sy"
        try:
            sy = open(sy_path, encoding="utf-8").read()
            if f'"{slug}"' in sy:
                doc_id = f["id"]
                break
        except Exception:
            continue
    if doc_id:
        api("/api/attr/setBlockAttrs", {"id": doc_id, "attrs": {"title": new_title}})
        print(f"修复: {title} -> {new_title}")
        fixed += 1
    else:
        print(f"未找到文档: {title}")

print(f"\n修复 {fixed} 篇")
