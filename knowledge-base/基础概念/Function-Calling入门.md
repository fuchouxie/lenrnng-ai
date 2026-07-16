# Function Calling 入门

## 什么是 Function Calling

让 AI **不只说话，还能调用你定义的函数**。这是 Agent 的基础。

```
普通对话：用户说 → AI 答 → 结束
Function Calling：用户说 → AI 判断需要调工具 → 返回调用意图 → 你执行 → 结果塞回去 → AI 基于结果回答
```

---

## 三个步骤

### 1. 定义工具

告诉 AI "我有什么工具、干什么用的"：

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前日期和时间。用户问时间时调用。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
```

**工具的 description 非常重要**——AI 靠读描述来决定要不要调用。

### 2. 判断 AI 是否想调工具

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,       # ← 把工具传进去
)

msg = response.choices[0].message

if msg.tool_calls:
    # AI 想调工具
    tool_name = msg.tool_calls[0].function.name
    arguments = msg.tool_calls[0].function.arguments
else:
    # AI 直接文字回复
    print(msg.content)
```

### 3. 执行工具，结果塞回去

```python
result = execute_tool(tool_name, arguments)

# 关键步骤：把工具调用和结果都 push 进 messages
messages.append({"role": "assistant", "tool_calls": [tool_call]})
messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

# 再调一次 API，让 AI 基于工具结果生成回答
response2 = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
)
```

---

## Agent Loop 就是 Function Calling 的循环

```
while AI还想调工具:
    调 API → AI 返回 tool_call → 你执行 → 结果塞回 messages → 循环

AI 不再要工具了 → 输出最终答案给用户
```

这就是 Agent 的核心循环：**观察 → 思考 → 行动 → 观察 → …… → 完成**

---

## 注意事项

| 问题 | 说明 |
|------|------|
| DeepSeek FC 偶有偏差 | 该调不调，或参数格式偏差——学习够用，生产注意 |
| 工具描述决定一切 | 描述模糊 → AI 乱调，描述太窄 → AI 不调 |
| 工具越多越慢 | 每个工具定义也占 Token |
| 安全性 | 执行前判断：这个操作需要用户确认吗？ |

---

## 相关笔记

- [[LLM的对话原理]] — tools 也占 messages 的上下文窗口
- [[Token与计费]] — 工具定义和结果也消耗 Token
- [[2026-07-15-环境搭建与API初体验]] — 对应代码 `04_tool_use.py`
