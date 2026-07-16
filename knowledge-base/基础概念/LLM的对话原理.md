# LLM 的对话原理

## 核心认知：大模型是"无状态"的

大模型本身**不会记住**上一轮聊了什么。每次 API 调用都是独立的一次请求。

"记忆"是开发者用 **messages 数组** 手动维护出来的。

---

## messages 数组：AI 的"记忆"

```python
messages = [
    {"role": "system", "content": "你是一个友好的助手。"},
    {"role": "user", "content": "我叫小明"},
    {"role": "assistant", "content": "你好小明！"},
    {"role": "user", "content": "我叫什么名字？"},
]
# → 发给 AI，AI 会回答"你叫小明"
```

### 三种 role

| role | 谁说的 | 作用 |
|------|--------|------|
| `system` | 开发者 | 设定 AI 的人设、行为规则、输出格式 |
| `user` | 用户 | 用户输入的内容 |
| `assistant` | AI | AI 之前的回复 |

### 为什么每次发整个数组？

因为模型没有状态。你必须把完整对话历史发回去，模型才知道刚才聊了什么。

### 这样做的代价

对话越长 → messages 越长 → Token 消耗越大 → 费用越高 → 响应越慢

---

## 上下文窗口

**上下文窗口 = messages 数组 + 工具定义 + AI 输出 的总 Token 数上限**

| 模型 | 窗口大小 |
|------|:------:|
| DeepSeek V3 | 64K Token |
| Claude 4 | 200K Token |
| GPT-4o | 128K Token |

超出窗口 → API 直接报错。

---

## Compaction（压缩）：解决窗口不够用

生产系统（Claude Code、Codex 等）不会无限制地保留历史。当接近窗口上限时：

```
压缩前（15000 Token，40 轮对话）：
  用户：帮我写登录功能
  AI：好的，这是代码……
  用户：改按钮颜色
  AI：好的……
  ……（省略 36 轮）

压缩后（约 500 Token）：
  <对话摘要>
  - 用户要求写登录功能，使用 React + JWT
  - 请求将登录按钮颜色改为蓝色
  - 新增注册功能需求
  - 当前正在修改 signup.ts
```

实现方式：让 AI 把历史对话总结成一段摘要，用摘要替换原始消息。

---

## 完整链路

```
用户输入
    │
    ▼
检查 messages 总 Token 数
    │
    ├── 未超窗口 → 直接发 messages
    │
    └── 快超了 → 先 compact（压缩历史）
                    ↓
                 发压缩后的 messages
                    │
                    ▼
               AI 回复
                    │
                    ▼
          append 进 messages
                    │
                    ▼
                  循环
```

---

## 相关笔记

- [[Token与计费]] — Token 是什么、中英文差异
- [[Function-Calling入门]] — 工具调用在 messages 里的角色
- [[2026-07-15-环境搭建与API初体验]] — 对应代码 `02_multi_turn.py`
