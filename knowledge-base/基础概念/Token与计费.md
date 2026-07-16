# Token 与计费

## Token 是什么

**Token 是 AI 的"最小阅读单位"。** AI 不认字，只认数字。发过去的字符串会先被切分成 Token。

```
你输入：  "你好，我叫小乐"
             ↓ 分词
Token：   ["你好", "，", "我叫", "小", "乐"]
             ↓ 每个 Token 对应一个数字 ID
数字：    [12345, 678, 90123, 456, 789]
             ↓
模型处理这些数字 → 生成新数字 → 转回文字给你
```

---

## 中英文 Token 差异

| 内容类型 | 多少字 ≈ 1 Token |
|----------|:--------------:|
| 英文单词 | ~0.75 个单词 |
| 中文汉字 | ~1.5-2 个汉字 |
| 代码 | ~3-4 个字符 |
| 标点/空格 | 通常单独 1 Token |

**同一句话，中英文 Token 数可能不同：**

```
英文："Hello, my name is Bob"  → 6 Token
中文："你好，我叫鲍勃"          → 5 Token
```

---

## 和计费的关系

**API 按 Token 数收费。** 每个模型有不一样的单价：

| 模型 | 输入价格（百万 Token） | 输出价格（百万 Token） |
|------|:------------------:|:------------------:|
| DeepSeek V3 | ~¥1 | ~¥3 |
| Claude Haiku | ~$1 | ~$5 |
| GPT-4o | ~$2.5 | ~$10 |

**输入 Token** = 你发给 AI 的所有东西（system prompt + 对话历史 + 工具定义）
**输出 Token** = AI 生成的内容

输入比输出便宜——因为输入可以缓存，输出必须逐个生成。

---

## 上下文窗口

**上下文窗口 = 一次请求里所有东西的总 Token 上限。**

| 模型 | 窗口 | 相当于 |
|------|:----:|--------|
| DeepSeek V3 | 64K | 一本中篇小说 |
| Claude 4 | 200K | 《三体》第一部 |
| GPT-4o | 128K | 两本中篇小说 |

超出窗口 → API 报错 → 需要 Compaction（[[LLM的对话原理#Compaction]]）

---

## 在代码里看 Token 用量

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
)

# usage 对象包含本次消耗
print(response.usage.total_tokens)       # 总共
print(response.usage.prompt_tokens)      # 输入（你的 messages）
print(response.usage.completion_tokens)  # 输出（AI 生成的）
```

---

## 相关笔记

- [[LLM的对话原理]] — messages 数组和上下文窗口的关系
- [[2026-07-15-环境搭建与API初体验]] — 动手练习
