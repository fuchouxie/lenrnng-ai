# Function Calling 实战

> 日期：2026-07-17
> 阶段：阶段一（API 基础）— 任务 1.5

---

## 产出

`ai-playground/04_function_calling.py` — 能使用两个工具的 AI 对话程序

| 工具 | 功能 | 参数 |
|------|------|------|
| `get_current_time` | 返回当前日期时间 | 无 |
| `get_current_weather` | 返回城市模拟天气 | `city: str` |

---

## 踩坑记录

### 坑 1：流式下 tool_calls 被拆成碎片

每个 chunk 只包含 tool_call 的部分字段（第一个 chunk 带 `name`，第二个带 `arguments`），需要累积拼接。初学阶段用非流式更好——`stream=False` 直接拿到完整 `tool_calls`。

### 坑 2：忘记再调一次 API

执行完工具、结果存入 messages 后，必须**再调用一次 API**，AI 才能基于结果生成回复。漏掉这一步会拿到 tool_calls 消息里的引导词（"好的，让我查一下..."）而非实际答案。

### 坑 3：消息链完整性 400 错误

```
Error: Messages with role 'tool' must be a response to a preceding message with 'tool_calls'
```

**原因**：存入 tool 结果前，忘了先存 assistant 的 tool_calls 消息。消息链必须：
```
user → assistant(tool_calls) → tool(result)
```
缺少中间那条 `assistant(tool_calls)` 就会报错。

### 坑 4：存消息时丢字段

手动 `{"role": "assistant", "content": msg.content}` 会丢失 `tool_calls` 字段。用 `msg.model_dump(exclude_none=True)` 统一存完整消息。

---

## 代码要点

```python
# 用字典映射函数名 → 函数对象，替代 if/elif 链
available_functions = {
    "get_current_time": get_current_time,
    "get_current_weather": get_current_weather,
}

# 解析 arguments JSON 字符串
args = json.loads(tool_call.function.arguments)

# **args 自动展开参数字典
result = available_functions[func_name](**args)

# 主循环简化版
msg = response.choices[0].message

if msg.tool_calls:
    messages.append(msg.model_dump(exclude_none=True))  # 存 tool_calls 消息
    # 执行工具...
    messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    response = send_messages(messages)  # 再调
    msg = response.choices[0].message   # 拿最终文本消息

messages.append(msg.model_dump(exclude_none=True))  # 只存一次
print(f"AI：{msg.content}")
```

---

## 学员提问记录

| 问题 | 答案要点 |
|------|---------|
| 为什么需要用列表记录 tool_calls？ | 流式下 tool_call 跨多个 chunk，需累积拼接 |
| 初学 tool 用非流式是不是更好？ | 是，去掉碎片拼接的噪音，专注核心流程 |
| 是不是每次直接把完整消息存进去就行？ | 是，`model_dump()` 一视同仁，不用分情况 |
| 为什么 tool 消息会报 400？ | assistant(tool_calls) 必须出现在 tool(result) 前面 |
| Python 中怎么查函数用法？ | `help(__import__('datetime').datetime.strftime)` |
| 怎么解析 city 参数？ | `json.loads(arguments)["city"]` |
| 获取 tool_calls 后需要自己调函数吗？ | 是，AI 只管决策，执行是你的事 |

---

## 进度

阶段一全部完成 ✅，下次进入阶段二（聊天应用）。

## 相关笔记

- [[Function-Calling入门]] — Function Calling 概念详解
- [[2026-07-15-环境搭建与API初体验]] — 之前的 API 基础实战
