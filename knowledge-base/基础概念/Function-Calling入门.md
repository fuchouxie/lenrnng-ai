# Function Calling 入门

## 是什么

让 AI **不只说话，还能调用你定义的函数**。这是 Agent 的基础。

```
普通对话：用户说 → AI 答 → 结束
Function Calling：用户说 → AI 判断需要调工具 → 返回调用意图 → 你执行 → 结果塞回去 → AI 基于结果回答
```

类比：AI 是一个没有手的大脑，Function Calling 就是你给它接上的**机械臂**——它决定用哪只手、怎么用，但真正干活的是你的代码。

---

## 三步走

### 1. 定义工具（tools 参数）

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time.",  # 描述决定 AI 会不会调用
            "parameters": {
                "type": "object",
                "properties": {},       # 无参数 → 空字典
                "required": [],         # 无必填参数 → 空列表
            },
        },
    },
]
```

**工具的 `description` 极其重要**——AI 靠读描述来决定调不调用。描述模糊 → AI 不调或乱调。

### 2. 接收 tool_calls

非流式时，`response.choices[0].message.tool_calls` 是一个**完整的列表**，不需要拼接：

```python
msg = response.choices[0].message

if msg.tool_calls:
    # AI 想调工具
    for tc in msg.tool_calls:
        print(tc.function.name)       # → "get_current_time"
        print(tc.function.arguments)  # → '{}'（JSON 字符串）
else:
    # AI 直接文字回复
    print(msg.content)
```

### 3. 执行 + 回传结果

```python
# 用字典映射函数名，替代 if/elif 链
available_functions = {
    "get_current_time": get_current_time,
    "get_current_weather": get_current_weather,
}

# 解析参数 + 执行
args = json.loads(tool_call.function.arguments)  # JSON 字符串 → Python 字典
result = available_functions[func_name](**args)    # **args 展开参数字典

# 关键：先存 assistant tool_calls 消息，再存 tool 结果
messages.append(msg.model_dump(exclude_none=True))     # 完整消息（含 tool_calls）
messages.append({                                       # 工具执行结果
    "role": "tool",
    "tool_call_id": tool_call.id,
    "content": result,
})

# 再调一次 API，AI 拿到结果后给出最终回复
response = send_messages(messages)
```

---

## 核心认知

### 消息链必须完整

API 要求 `tool` 消息前面**必须有**一条含 `tool_calls` 的 `assistant` 消息：

```
✅ 正常：
  user: "几点了？"
  assistant: { tool_calls: [{id: "call_xxx", name: "get_current_time"}] }
  tool: { tool_call_id: "call_xxx", content: "2026年..." }
  assistant: "现在是 2026年..."

❌ 报错（缺少 assistant tool_calls 消息）：
  user: "几点了？"
  tool: { tool_call_id: "call_xxx", content: "2026年..." }  → 400 错误！
```

### 用 model_dump() 存消息

不要手动拼 `{role, content}`——当消息里有 tool_calls 时，手动拼会丢字段：

```python
# ❌ 丢失 tool_calls 字段
messages.append({"role": "assistant", "content": msg.content})

# ✅ 完整保存
messages.append(msg.model_dump(exclude_none=True))
```

### 流式 vs 非流式

初学 tool 建议用**非流式**。流式下 tool_calls 会被拆成多个 chunk，需要自己累积拼接，增加了不必要的复杂度。

---

## Agent Loop 就是 Function Calling 的循环

```
while AI 还想调工具:
    调 API → AI 返回 tool_call → 你执行 → 结果塞回 messages → 循环

AI 不再要工具了 → 输出最终答案
```

这就是 Agent 的核心循环：**观察 → 思考 → 行动 → 观察 → …… → 完成**

---

## 相关笔记

- [[LLM的对话原理]] — tools 也占 messages 的上下文窗口
- [[Token与计费]] — 工具定义和结果也消耗 Token
- [[2026-07-17-Function-Calling实战]] — 本次实操记录
- [[2026-07-15-环境搭建与API初体验]] — 开发环境配置
