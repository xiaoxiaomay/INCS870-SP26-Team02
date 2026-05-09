# SentinelFlow V2.0 — 工作方案

## 项目背景
SentinelFlow 是一个金融 RAG 管道的内联 AI 安全网关（INCS 870 毕业论文项目）。
V1 已完成 6 大贡献（C1-C6），系统运行在 Python 3.10+，
使用 PostgreSQL+pgvector（AWS）+ FAISS + OpenAI gpt-4o-mini + Streamlit。
代码库约 30+ Python 文件，7500+ 行。

## V2.0 工作目标
在不破坏任何现有 V1 功能和测试结果的前提下，完成以下升级。
所有新功能必须有独立的测试脚本，可单独运行。

---

## 模块一：真实世界评估数据集（最高优先级）

### 1A. 爬取真实良性财经查询
目标：获取 300-500 条真实分析师风格的金融问题，
用于替代/补充现有 100 条合成 normal prompts。

数据来源（按优先级）：
1. SEC EDGAR Full-Text Search API（完全合法，无需鉴权）
   - 端点：https://efts.sec.gov/LATEST/search-index
   - 抓取 8-K/10-Q 的 Q&A 部分，提取真实分析师问题
2. Yahoo Finance RSS Feed（公开）
   - https://feeds.finance.yahoo.com/rss/2.0/headline
   - 提取标题作为良性查询样本
3. Reddit r/investing / r/SecurityAnalysis（公开 API）
   - 使用 PRAW 或直接 requests，提取高质量问题帖

输出格式（与现有 normal_prompts.json 兼容）：
```json
{
  "id": "real_001",
  "query": "...",
  "source": "SEC_EDGAR | YAHOO_RSS | REDDIT",
  "expected_action": "allow",
  "sensitivity_level": "L0",
  "is_synthetic": false
}
```

保存路径：data/eval/real_world_normal_prompts.json

### 1B. 集成 garak 金融攻击向量
目标：从 garak 开源框架提取/改写金融相关攻击，
补充现有 70 条合成攻击，增加 20-30 条外部验证攻击。

步骤：
1. pip install garak
2. 运行：python -m garak --list_probes | grep -i finance
3. 重点关注以下 probe 类别：
   - garak.probes.leakreplay（训练数据泄漏）
   - garak.probes.knowledgegrounding
   - garak.probes.promptinject
4. 将 garak 生成的攻击改写为金融场景版本

同时从 HarmBench 提取（GitHub: centerforaisafety/HarmBench）：
- 克隆仓库，查找 data/behavior_datasets/ 下金融相关条目
- 关键词过滤：finance, investment, trading, strategy, portfolio

输出格式（与现有 attack_prompts.json 兼容）：
```json
{
  "id": "ext_001",
  "prompt": "...",
  "category": "garak_leakreplay | harmbench_financial",
  "target_secret_id": "S001",
  "expected_action": "block",
  "difficulty": "hard",
  "source": "external",
  "is_synthetic": false
}
```

保存路径：data/eval/external_attack_prompts.json

---

## 模块二：Gate 0c — 共现检测（Co-occurrence Detection）

### 目标
填补 V1 已知 gap：单个 token 无害，但特定组合出现 = 机密策略信号。

### 实现位置
在 Gate 0b（hard-block）之后、Gate 1（embedding precheck）之前插入。
修改文件：scripts/run_rag_with_audit.py

### 核心逻辑
```python
def cooccurrence_check(query: str, config: dict) -> dict:
    """
    检测查询中是否同时出现多个机密信号词。
    返回：{"action": "allow|warn|block", "matched_pattern": str, "match_count": int}
    """
    query_lower = query.lower()
    patterns = config["policy"]["cooccurrence_patterns"]
    
    for pattern in patterns:
        terms = pattern["terms"]
        min_count = pattern["min_count"]
        action = pattern["action"]
        
        matched = [t for t in terms if t.lower() in query_lower]
        if len(matched) >= min_count:
            return {
                "action": action,
                "matched_pattern": pattern["name"],
                "matched_terms": matched,
                "match_count": len(matched)
            }
    
    return {"action": "allow", "matched_pattern": None, "match_count": 0}
```

### config.yaml 新增配置
在 policy 下新增：
```yaml
cooccurrence_patterns:
  - name: "rsi_strategy_combo"
    terms: ["RSI", "VWAP", "Universe", "NAV", "position size"]
    min_count: 3
    action: "block"
  - name: "threshold_extraction_combo"
    terms: ["threshold", "basis points", "drawdown", "limit", "cap"]
    min_count: 3
    action: "warn"
  - name: "alpha_signal_combo"
    terms: ["alpha", "signal", "entry", "exit", "condition", "trigger"]
    min_count: 3
    action: "block"
  - name: "risk_param_combo"
    terms: ["VaR", "beta", "hedge ratio", "sector cap", "single-name"]
    min_count: 2
    action: "warn"
```

### 审计日志集成
gate_0c 的决定必须记录到 audit chain，
格式与现有 gate_0a/gate_0b 日志一致。

### 测试脚本
创建：scripts/test_gate0c.py
- 测试 20 个共现命中案例（应 warn/block）
- 测试 20 个非共现案例（应 allow，验证零误报）

---

## 模块三：端到端延迟测量

### 目标
测量并报告系统在不同路径下的延迟分布，
这是现实部署可行性的关键指标。

### 测量路径
- Path A：Gate 0a 拦截（最快路径）
- Path B：Gate 0b 拦截
- Path C：Gate 0c 拦截（新）
- Path D：Gate 1 拦截
- Path E：完整通过（最慢路径：所有 gate + RAG + LLM + leakage scan）

### 实现
创建新文件：scripts/latency_benchmark.py
```python
import time, statistics, json

def measure_latency(query, pipeline_fn, n_runs=50):
    times = []
    for _ in range(n_runs):
        start = time.perf_counter()
        result = pipeline_fn(query)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # 转换为 ms
    
    return {
        "p50": statistics.median(times),
        "p95": statistics.quantiles(times, n=20)[18],
        "p99": statistics.quantiles(times, n=100)[98],
        "mean": statistics.mean(times),
        "min": min(times),
        "max": max(times)
    }
```

### 输出
保存：data/eval/latency_benchmark.json
格式：
```json
{
  "path_a_gate0a_block": {"p50": X, "p95": X, "p99": X, "mean": X},
  "path_b_gate0b_block": {"p50": X, "p95": X, "p99": X, "mean": X},
  "path_c_gate0c_block": {"p50": X, "p95": X, "p99": X, "mean": X},
  "path_d_gate1_block":  {"p50": X, "p95": X, "p99": X, "mean": X},
  "path_e_full_pass":    {"p50": X, "p95": X, "p99": X, "mean": X}
}
```

---

## 模块四：V2 综合评估跑批

### 目标
用新数据集重跑完整评估，产出可直接引用进论文的结果。

### 评估脚本更新
修改：scripts/eval_finance_attacks.py
新增评估模式：--mode real_world

新增评估维度：
1. 外部攻击集（external_attack_prompts.json）的 ASR
2. 真实良性查询（real_world_normal_prompts.json）的 FPR
3. Gate 0c 的单独贡献（ablation：关闭 Gate 0c 后的 ASR 变化）

### 输出报告
保存：data/eval/v2_evaluation_report.json
必须包含：
- synthetic_results（V1 原始结果，不变）
- real_world_results（新增）
- gate0c_ablation（新增）
- latency_summary（新增）

---

## 约束与要求

1. 不得修改或破坏任何 V1 现有测试的通过状态
2. 所有新功能默认关闭（通过 config.yaml 开启），
   确保 V1 的 31/31 demo cases 仍然全部通过
3. 每个模块完成后运行：
   python scripts/run_demo_cases.py 验证无回归
4. 爬虫需要有 rate limiting 和 retry 逻辑，
   不要对目标服务器发出过于密集的请求
5. 所有外部数据需要记录来源 URL 和抓取时间戳
```
