#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成专利伪装文档 → 思源 createDocWithMd + setBlockAttrs"""
import json, time, urllib.request, re, random
from datetime import datetime, timedelta

API = "http://127.0.0.1:6806"
NOTEBOOK = "20260808225839-mm6cxzc"

def api(endpoint, payload):
    req = urllib.request.Request(f"{API}{endpoint}",
        data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())

def create_doc(path, title, markdown, slug_ts):
    r = api("/api/filetree/createDocWithMd", {"notebook": NOTEBOOK, "path": path, "markdown": markdown})
    doc_id = r.get("data")
    print(f"创建 {title}: {r.get('code')} id={doc_id}")
    if doc_id:
        api("/api/attr/setBlockAttrs", {"id": doc_id, "attrs": {
            "title": title, "hpath": title, "slug": slug_ts, "updated": slug_ts[:14]}})
        print(f"  设置 slug={slug_ts}")
    return doc_id

# slug 时间戳基准：从 2026-08-09 21:30 开始往后排（比现有测试帖新，排最前）
base = datetime(2026, 8, 9, 21, 30, 0)

docs = [
    # (path, 标题, slug 后缀, markdown)
    ("patent-1", "一种基于边缘计算的分布式缓存数据同步方法",
     "20260809213000-edge-cache-sync",
     """# 一种基于边缘计算的分布式缓存数据同步方法

## 技术领域

本发明涉及[边缘计算](https://example.com/edge)与分布式存储技术领域，具体涉及一种基于边缘计算的分布式缓存数据同步方法及系统。

## 背景技术

随着物联网设备的爆发式增长，边缘节点承载的数据量呈指数级上升。传统集中式缓存架构存在以下问题：

1. 中心节点带宽瓶颈，边缘设备访问延迟高
2. 数据一致性难以保证，弱网环境下同步失败率高
3. 缓存失效策略单一，热点数据无法动态迁移

> 现有技术如 US10,123,456 B2 采用全量同步策略，在边缘节点数量超过 100 时同步耗时呈线性增长，无法满足实时性要求。

## 发明内容

### 技术问题

本发明的目的在于提供一种基于边缘计算的分布式缓存数据同步方法，以解决现有技术中同步效率低、一致性差的技术问题。

### 技术方案

一种基于边缘计算的分布式缓存数据同步方法，包括以下步骤：

- 步骤 S1：边缘节点周期性采集本地缓存命中率与网络延迟指标
- 步骤 S2：根据所述指标构建**同步优先级队列**，按需调度同步任务
- 步骤 S3：采用增量哈希对比算法，仅同步变更数据块
- 步骤 S4：通过一致性仲裁协议确认同步结果

其中，所述同步优先级队列的构建公式为：

```
priority = w1 * (1 - hit_rate) + w2 * (latency / max_latency)
```

### 有益效果

| 对比项 | 现有技术 | 本发明 |
|--------|---------|--------|
| 同步耗时 | O(n) 全量 | O(Δ) 增量 |
| 带宽占用 | 100% | ≤30% |
| 一致性保证 | 最终一致 | 强一致(仲裁) |
| 边缘节点扩展 | ≤100 | ≥1000 |

## 具体实施方式

### 实施例 1

如图 1 所示，本实施例提供一种边缘缓存同步系统，包括：

```python
class EdgeCacheSync:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.priority_queue = PriorityQueue()

    def sync_cycle(self):
        metrics = self.collect_metrics()
        for peer in self.peers:
            priority = self.compute_priority(metrics, peer)
            self.priority_queue.push(peer, priority)
        self.process_queue()

    def compute_priority(self, metrics, peer):
        w1, w2 = 0.6, 0.4
        return w1 * (1 - metrics.hit_rate) + w2 * (metrics.latency / 100.0)
```

### 实施例 2

在另一实施例中，所述增量哈希对比算法采用 **Merkle 树** 结构：

```go
func BuildMerkle(blocks [][]byte) []byte {
    if len(blocks) == 1 {
        return sha256.Sum256(blocks[0])
    }
    mid := len(blocks) / 2
    left := BuildMerkle(blocks[:mid])
    right := BuildMerkle(blocks[mid:])
    return sha256.Sum256(append(left, right...))
}
```

## 权利要求

1. 一种基于边缘计算的分布式缓存数据同步方法，其特征在于，包括：
   - 边缘节点周期性采集本地缓存命中率与网络延迟指标；
   - 根据所述指标构建同步优先级队列，按需调度同步任务；
   - 采用增量哈希对比算法，仅同步变更数据块。
2. 根据权利要求 1 所述的方法，其特征在于，所述增量哈希对比算法采用 Merkle 树结构。
3. 一种基于边缘计算的分布式缓存数据同步系统，其特征在于，包括采集模块、调度模块与同步模块。

## 附图说明

图 1 为本发明实施例提供的系统架构示意图；
图 2 为本发明实施例提供的同步流程图。
"""),
    ("patent-2", "一种基于大语言模型的会议纪要自动生成方法",
     "20260809220000-llm-meeting-notes",
     """# 一种基于大语言模型的会议纪要自动生成方法

## 技术领域

本发明涉及自然语言处理技术领域，具体涉及一种基于大语言模型的会议纪要自动生成方法、装置及存储介质。

## 背景技术

企业会议场景中，会议纪要的整理通常依赖人工记录，存在以下痛点：

- 记录不及时，关键决策项遗漏率高
- 多说话人场景下发言归属混乱
- 纪要格式不统一，复盘检索困难

> 现有语音转写方案（如 US11,222,333 B2）仅完成语音到文本的转换，无法自动提炼**行动项**与**决策结论**。

## 发明内容

### 技术方案

一种基于大语言模型的会议纪要自动生成方法，包括：

1. 获取会议音频流，通过语音识别模型生成带时间戳的转写文本
2. 对所述转写文本进行**说话人分离**，标记每个分段的发言者身份
3. 将分段文本输入大语言模型，采用结构化提示词模板进行信息抽取
4. 聚合抽取结果，生成包含决策项、行动项、风险项的会议纪要

所述结构化提示词模板如下：

```text
你是专业的会议纪要助手。请从以下会议记录中提取：
1. 决策结论（Decision）
2. 行动项（Action Item，含负责人与截止时间）
3. 风险与阻塞（Risk）
输出 JSON 格式。
会议记录：{{transcript}}
```

### 有益效果

| 指标 | 人工纪要 | 本方法 |
|------|---------|--------|
| 平均耗时 | 45 分钟 | 3 分钟 |
| 行动项覆盖率 | 72% | 96% |
| 格式一致性 | 不统一 | 标准化 |

## 具体实施方式

### 实施例

```python
import json
from typing import List, Dict

def generate_minutes(segments: List[Dict]) -> Dict:
    prompt = TEMPLATE.format(transcript=json.dumps(segments, ensure_ascii=False))
    result = llm_complete(prompt, temperature=0.2)
    return json.loads(result)

def main():
    segments = diarize(audio_file)          # 说话人分离
    minutes = generate_minutes(segments)    # 纪要生成
    save_markdown(minutes, "minutes.md")    # 导出
```

## 权利要求

1. 一种基于大语言模型的会议纪要自动生成方法，其特征在于，包括：
   获取会议音频流并进行语音识别，得到带时间戳的转写文本；对所述转写文本进行说话人分离；将分段文本输入大语言模型进行结构化抽取；聚合生成会议纪要。
2. 根据权利要求 1 所述的方法，其特征在于，所述结构化抽取采用 JSON 格式的提示词模板。
3. 一种计算机可读存储介质，其上存储有计算机程序，所述程序被处理器执行时实现权利要求 1-2 任一项所述的方法。
"""),
    ("patent-3", "一种基于区块链的电子证据存证与验证系统",
     "20260809223000-blockchain-evidence",
     """# 一种基于区块链的电子证据存证与验证系统

## 技术领域

本发明涉及区块链技术与电子数据存证领域，具体涉及一种基于区块链的电子证据存证与验证系统、方法及装置。

## 背景技术

电子证据在司法实践中面临易篡改、难验证的困境。传统存证方式依赖**第三方公证机构**，成本高、周期长，且存在单点故障风险。

| 传统存证 | 区块链存证 |
|---------|-----------|
| 中心化存储 | 分布式账本 |
| 公证费用高 | 链上哈希锚定 |
| 验证需人工 | 秒级自动核验 |

## 发明内容

### 技术方案

本系统采用**双链架构**：

- **证据链**：存证原始数据的哈希摘要，区块头包含时间戳与前一区块哈希
- **索引链**：记录证据元数据（来源、持有人、验证公钥），支持高效检索

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceRegistry {
    mapping(bytes32 => Evidence) private evidences;

    struct Evidence {
        address owner;
        uint256 timestamp;
        string hashAlgo;
    }

    function register(bytes32 evidenceHash, string calldata algo) external {
        require(evidences[evidenceHash].owner == address(0), "duplicated");
        evidences[evidenceHash] = Evidence(msg.sender, block.timestamp, algo);
    }

    function verify(bytes32 evidenceHash) external view returns (bool, uint256) {
        Evidence memory ev = evidences[evidenceHash];
        return (ev.owner != address(0), ev.timestamp);
    }
}
```

### 有益效果

1. 证据不可篡改：哈希上链后任何修改均可被发现
2. 验证零成本：任何节点可独立核验
3. 司法采信度高：符合《电子签名法》相关规定

## 权利要求

1. 一种基于区块链的电子证据存证方法，其特征在于：计算电子数据的哈希摘要；将所述摘要与元数据写入区块链；生成存证凭证并返回验证接口。
2. 根据权利要求 1 所述的方法，其特征在于，所述区块链为联盟链，共识机制为 PBFT。
3. 一种基于区块链的电子证据验证系统，其特征在于，包括存证模块、查询模块与验真模块。
"""),
    ("patent-4", "一种基于图神经网络的网络流量异常检测方法",
     "20260809230000-gnn-traffic-detection",
     """# 一种基于图神经网络的网络流量异常检测方法

## 技术领域

本发明涉及网络安全与人工智能技术领域，具体涉及一种基于图神经网络的网络流量异常检测方法、装置及存储介质。

## 背景技术

网络入侵检测（IDS）是网络安全的第一道防线。传统基于规则的检测方式存在**误报率高、未知攻击漏检**的问题。近年来基于机器学习的方案虽然提升了检测率，但忽略了流量之间的**拓扑关联性**。

## 发明内容

### 技术方案

本方法将网络流量建模为动态图结构：

- 节点：主机、服务、会话
- 边：通信关系，边权重为流量特征向量
- 时序：引入时间窗口滑动机制，捕捉行为演变

采用 **GraphSAGE + LSTM** 混合架构：

```python
import torch
import torch.nn as nn

class TrafficGNN(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.sage = SAGEConv(in_dim, hidden_dim)
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, batch_first=True)
        self.classifier = nn.Linear(hidden_dim, out_dim)

    def forward(self, graph, features, seq):
        h = torch.relu(self.sage(graph, features))
        h_seq, _ = self.lstm(seq)
        return self.classifier(h_seq[:, -1, :])
```

### 训练流程

1. 采集正常流量构建基线图
2. 以自监督方式预训练图嵌入
3. 标注少量异常样本进行微调
4. 在线推理时计算**异常分数**并与阈值比较

## 实验效果

| 检测方法 | 准确率 | 误报率 | 未知攻击检出 |
|---------|--------|--------|-------------|
| 规则引擎 | 78.2% | 9.5% | 12% |
| 传统 ML | 86.4% | 4.8% | 45% |
| **本方法** | **94.1%** | **1.7%** | **83%** |

## 权利要求

1. 一种基于图神经网络的网络流量异常检测方法，其特征在于，包括：将网络流量建模为动态图结构；通过图神经网络提取拓扑特征；结合时序模型捕获行为演变；基于异常分数判定攻击行为。
2. 根据权利要求 1 所述的方法，其特征在于，所述图神经网络为 GraphSAGE。
3. 一种网络流量异常检测装置，其特征在于，包括建模模块、特征提取模块与判定模块。
"""),
    ("patent-5", "一种低功耗物联网设备的固件增量升级方法",
     "20260809233000-iot-firmware-upgrade",
     """# 一种低功耗物联网设备的固件增量升级方法

## 技术领域

本发明涉及物联网（IoT）技术领域，具体涉及一种低功耗物联网设备的固件增量升级方法、系统及计算机可读存储介质。

## 背景技术

物联网设备数量庞大、分布广泛，固件升级一直是运维痛点：

1. 全量升级包体积大（数百 KB 至数 MB），窄带网络下传输耗时长
2. 设备电池容量有限，长时传输导致电量耗尽
3. 升级中断恢复机制缺失，设备可能变砖

## 发明内容

### 技术方案

本方法采用 **bsdiff 差分算法 + 断点续传 + 分片校验** 三重机制：

- 服务器端：对比新旧固件生成差分补丁，补丁体积约为全量的 5%~15%
- 传输层：补丁分片传输，每片携带 CRC32 校验码，失败自动重传
- 设备端：接收完成后先写入**暂存分区**，校验通过再原子切换启动分区

```
┌─────────┐   差分补丁    ┌──────────────┐
│  云平台  │ ────────────▶ │  边缘网关     │
└─────────┘               └──────────────┘
                                │ 分片下发
                                ▼
                         ┌──────────────┐
                         │  IoT 设备     │
                         │  暂存分区→主分区│
                         └──────────────┘
```

### 升级流程伪代码

```c
int upgrade_firmware(const uint8_t *patch, size_t patch_len) {
    if (!verify_crc(patch, patch_len)) return -1;
    write_to_staging(patch, patch_len);       // 写入暂存分区
    if (!verify_signature(patch)) return -2;  // 验签
    atomic_switch_partition();                // 原子切换
    return 0;
}
```

### 有益效果

| 指标 | 全量升级 | 本发明 |
|------|---------|--------|
| 传输数据量 | 512 KB | 48 KB |
| 升级耗时(2G) | 68 s | 9 s |
| 电池损耗 | 高 | 降低 85% |
| 断点恢复 | 不支持 | 支持 |

## 权利要求

1. 一种低功耗物联网设备的固件增量升级方法，其特征在于：服务器端基于新旧固件生成差分补丁；补丁分片传输并携带校验码；设备端写入暂存分区，校验通过后原子切换。
2. 根据权利要求 1 所述的方法，其特征在于，所述差分补丁采用 bsdiff 算法生成。
3. 一种低功耗物联网设备的固件升级系统，其特征在于，包括云平台、边缘网关与物联网设备。
"""),
    ("patent-6", "一种容器集群的弹性伸缩策略优化方法",
     "20260810000000-k8s-autoscaling",
     """# 一种容器集群的弹性伸缩策略优化方法

## 技术领域

本发明涉及云计算与容器编排技术领域，具体涉及一种容器集群的弹性伸缩策略优化方法、装置及存储介质。

## 背景技术

Kubernetes 的 HPA（Horizontal Pod Autoscaler）基于 CPU/内存利用率进行伸缩，存在**反应滞后**与**抖动**问题：

- 流量突增时扩容需要 3~5 分钟，期间请求超时
- 指标波动导致频繁扩缩容，资源浪费
- 无法感知业务级指标（如队列积压、请求延迟）

## 发明内容

### 技术方案

本方法提出**预测式伸缩**策略：

1. 采集历史负载时序数据，使用 ARIMA 模型预测未来 15 分钟负载
2. 结合业务队列深度、P99 延迟等自定义指标
3. 采用**双阈值滞回**机制防止抖动

```python
def compute_replicas(predicted_load, current_replicas):
    target = ceil(predicted_load / per_pod_capacity)
    # 滞回: 扩容阈值 70%, 缩容阈值 30%
    if target > current_replicas and predicted_load > 0.7:
        return min(target, current_replicas * 2)  # 平滑扩容
    if target < current_replicas and predicted_load < 0.3:
        return max(target, current_replicas // 2)  # 平滑缩容
    return current_replicas
```

### 有益效果

| 场景 | 原生 HPA | 本方法 |
|------|---------|--------|
| 扩容响应时间 | 3-5 min | <1 min |
| 扩缩容次数/天 | 42 | 11 |
| CPU 利用率 | 61% | 78% |
| 请求超时率 | 2.3% | 0.4% |

## 权利要求

1. 一种容器集群的弹性伸缩策略优化方法，其特征在于：采集历史负载时序数据并进行预测；结合业务级自定义指标；基于双阈值滞回机制确定目标副本数。
2. 根据权利要求 1 所述的方法，其特征在于，所述预测模型为 ARIMA。
3. 一种容器集群的弹性伸缩装置，其特征在于，包括数据采集模块、预测模块与伸缩决策模块。
"""),
    ("patent-7", "一种多模态数据的统一检索与排序方法",
     "20260810003000-multimodal-retrieval",
     """# 一种多模态数据的统一检索与排序方法

## 技术领域

本发明涉及信息检索技术领域，具体涉及一种多模态数据的统一检索与排序方法、装置及存储介质。

## 背景技术

企业知识库中同时存在文本、图片、音视频等多模态数据，传统检索系统存在以下问题：

> 各模态数据独立建库、独立检索，跨模态查询需人工切换，无法统一排序。

## 发明内容

### 技术方案

本方法构建**统一向量空间**，将多模态数据映射到同一嵌入空间：

- 文本：BERT 编码器 → 768 维向量
- 图像：ViT 编码器 → 768 维向量  
- 音频：CLAP 编码器 → 768 维向量

检索时计算查询向量与各模态向量的**余弦相似度**，并引入重排序模型：

```python
def unified_search(query, corpora, k=10):
    q_vec = encode_text(query)
    scores = []
    for item in corpora:
        sim = cosine_similarity(q_vec, item.vector)
        scores.append((item, sim))
    scores.sort(key=lambda x: -x[1])
    return rerank(scores[:k * 5])[:k]  # 粗排后精排
```

### 跨模态对齐训练

```python
# 对比学习损失: 拉近匹配对, 推远不匹配对
loss = -log(exp(sim(pos)/tau) / sum(exp(sim(neg)/tau) for neg in negatives))
```

### 实验效果

| 模态组合 | Recall@10 | MRR |
|---------|-----------|-----|
| 文本-文本 | 0.912 | 0.884 |
| 文本-图像 | 0.867 | 0.823 |
| 文本-音频 | 0.795 | 0.761 |
| 三模态混合 | 0.843 | 0.809 |

## 权利要求

1. 一种多模态数据的统一检索与排序方法，其特征在于：将多模态数据映射到统一向量空间；计算查询与候选的相似度；基于重排序模型输出最终结果。
2. 根据权利要求 1 所述的方法，其特征在于，所述统一向量空间的维度为 768。
3. 一种多模态数据的统一检索装置，其特征在于，包括编码模块、相似度计算模块与重排序模块。
"""),
    ("patent-8", "一种基于知识图谱的专利技术功效矩阵构建方法",
     "20260810010000-patent-matrix",
     """# 一种基于知识图谱的专利技术功效矩阵构建方法

## 技术领域

本发明涉及专利情报分析与知识图谱技术领域，具体涉及一种基于知识图谱的专利技术功效矩阵构建方法、装置及存储介质。

## 背景技术

专利技术功效矩阵是专利布局分析的核心工具，通过「技术手段 × 实现功效」二维结构呈现竞争格局。传统构建方式依赖**人工阅读**，存在效率低、主观性强、更新滞后的问题。

## 发明内容

### 技术方案

本方法自动构建技术功效矩阵，包括：

1. **专利文本解析**：抽取独立权利要求中的技术特征与功效描述
2. **实体识别**：基于领域词典与 NER 模型识别技术手段实体
3. **关系抽取**：识别技术特征与功效之间的因果关系
4. **矩阵生成**：按聚类结果填充二维矩阵

```
技术手段 \\ 功效 | 提高效率 | 降低成本 | 增强安全
----------------|---------|---------|---------
边缘计算       |   ●●    |   ●     |   ●
知识图谱       |   ●     |   ●●    |   ●
区块链         |   ●     |   ●     |   ●●
```

### 实体关系抽取示例

```python
from spacy.matcher import Matcher

def extract_tech_effect(doc):
    matcher = Matcher(nlp.vocab)
    # 模式: [技术名词] 使得/用于 [功效描述]
    matcher.add("TECH_EFFECT", [
        [{"POS": "NOUN"}, {"LEMMA": {"IN": ["使", "用于", "实现"]}}, {"POS": "VERB"}]
    ])
    return [(m[0], doc[m[1]:m[2]].text) for m in matcher(doc)]
```

### 有益效果

1. 构建效率：从人工数天缩短至分钟级
2. 覆盖全面：自动识别隐含功效描述
3. 动态更新：新专利入库自动增量更新矩阵

## 权利要求

1. 一种基于知识图谱的专利技术功效矩阵构建方法，其特征在于：解析专利文本并抽取技术特征与功效描述；通过实体识别与关系抽取建立知识图谱；基于聚类生成技术功效矩阵。
2. 根据权利要求 1 所述的方法，其特征在于，所述实体识别采用 NER 模型与领域词典结合的方式。
3. 一种基于知识图谱的专利技术功效矩阵构建装置，其特征在于，包括解析模块、图谱构建模块与矩阵生成模块。
"""),
]

for i, (path, title, slug, md) in enumerate(docs):
    # slug 时间戳: 21:30 起每篇 +30min, 用 timedelta 保证时间合法
    ts = (base + timedelta(minutes=30 * i)).strftime("%Y%m%d%H%M%S")
    slug_ts = f"{ts}-{slug.split('-', 2)[-1]}"
    create_doc(f"/{path}", title, md, slug_ts)
    time.sleep(1)
print("完成")
