# AI 应用工程师 — 实战学习路线（超详细版）

> 特点：每一步都有具体的资料链接、代码片段和验收标准。
> 面向：有编程基础，想转 AI 应用开发的程序员。
> 每天投入：1-3 小时即可推进。

---

## 在你开始之前

### 两件事，今天花 30 分钟做完

**任务 0.1：注册 API 账号（15 分钟）**

```
1. 打开 https://console.anthropic.com/
2. 注册 Anthropic 账号（用 Google 登录最快）
3. 进入 API Keys 页面，点 "Create Key"
4. 给 Key 取个名字（比如 "learning"），复制保存
5. 充值 $10（最少金额，够你学完整个路线图）

备用方案（如果 Anthropic 注册有问题）：
  → https://platform.openai.com/ 注册 OpenAI
  → API Keys → Create → 复制保存 → 充值 $10
```

**任务 0.2：配好环境变量（15 分钟）**

```bash
# 在你的工作目录下创建 .env 文件
# 内容只有一行（选你注册的那个）：

ANTHROPIC_API_KEY=sk-ant-xxxxx
# 或者
OPENAI_API_KEY=sk-xxxxx
```

---

## 阶段一：第一次"对话"（Week 1）

### 任务 1.1 — 阅读资料（1 小时）

**只看这两个页面，不要看别的：**

| 读什么 | 链接 | 重点读什么 | 时间 |
|--------|------|-----------|------|
| Anthropic Messages API 概览 | https://docs.anthropic.com/en/api/messages | 只看"Create a Message"这一节，搞清楚 `model`、`messages`、`max_tokens`、`system` 四个参数的格式 | 30 分钟 |
| 或者 OpenAI Chat API 概览 | https://platform.openai.com/docs/api-reference/chat/create | 同上，搞清楚 `model`、`messages`、`stream` 三个参数 | 30 分钟 |

**不要看**：不要看 Embedding、不要看 Fine-tuning、不要看 Batch API、不要看 Assistants API。只看 Chat/Messages。

**检验标准**：你能用一张纸画出来 `messages` 数组的结构（role + content 交替），就够了。

---

### 任务 1.2 — 第一行代码（30 分钟）

**选择你的语言，复制下面的代码，把 `YOUR_KEY` 替换掉，跑起来。**

<details>
<summary>如果你用 TypeScript/Node.js：点我展开</summary>

```bash
mkdir ai-playground && cd ai-playground && npm init -y
npm install @anthropic-ai/sdk
```

```typescript
// file: 01-first-chat.ts
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! });

const response = await client.messages.create({
  model: 'claude-haiku-4-5-20251001',  // 最便宜的模型，够用了
  max_tokens: 500,
  system: '你是一个友好、简洁的助手。',  // 这个就是 System Prompt
  messages: [
    { role: 'user', content: '你好！用一句话介绍一下自己。' }
  ],
});

console.log(response.content[0].text);
```
</details>

<details>
<summary>如果你用 Python：点我展开</summary>

```bash
mkdir ai-playground && cd ai-playground
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install anthropic
```

```python
# file: 01_first_chat.py
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=500,
    system="你是一个友好、简洁的助手。",
    messages=[
        {"role": "user", "content": "你好！用一句话介绍一下自己。"}
    ],
)

print(response.content[0].text)
```
</details>

**跑起来了吗？**
- ✅ 成功 → 你已经完成了最难的一步：第一次 API 调用。继续。
- ❌ 报错 → 检查：Key 有没有写对？`ANTHROPIC_API_KEY` 环境变量设了吗？网络能不能访问 `api.anthropic.com`？

---

### 任务 1.3 — 加个死循环，变成对话程序（30 分钟）

把你刚才的代码改成这样：

```
程序行为：
  1. 打印 "你："
  2. 用户输入一句话
  3. 调 API，AI 回复
  4. 打印 "AI：回复内容"
  5. 回到第 1 步（除非用户输入 "exit"）
```

**关键改动**：你需要维护一个 `messages` 数组，每次把用户的新消息 append 进去，同时把 AI 的回复也 append 进去。下次调用时把整个数组发回去。

**验收标准**：
```
你：我叫小明
AI：你好小明！有什么我可以帮你的？

你：我叫什么名字？
AI：你叫小明。  ← 能记住！说明 messages 数组起作用了
```

> **到这里，你暂停 10 分钟，想想**：messages 数组就是"记忆"。你发给 AI 的每一次都是一整段对话历史，不是一句话。这就是为什么多轮对话会越来越贵——因为每次都要把整段历史发过去。

---

### 任务 1.4 — 让回复"流"出来（45 分钟）

**为什么需要流式？** 你现在的代码是等 AI 全部写完了才打印。流式让你看到一个一个字往外蹦——用户体验天差地别。

**阅读**：API 文档里搜 `stream`，看 streaming 部分的代码示例。只改一行参数：`stream: true`，然后处理返回的流。

<details>
<summary>流式处理的思路（先自己想，再看）：</summary>

```
非流式：request → 等 3 秒 → 拿到完整 response → 打印
流  式：request → 收到第一个字 → 打印 → 收到第二个字 → 打印 → …… → 结束
```

代码改动：
```
// 之前
const response = await client.messages.create({ ... });
console.log(response.content[0].text);

// 之后
const stream = client.messages.stream({ ...stream: true 后 });
for await (const event of stream) {
  // event 的类型不同，你需要判断
  // 如果是文字块，就 process.stdout.write(文字)
  // 查文档的 streaming 示例代码
}
```
</details>

**验收标准**：AI 回复逐字出现，打字机效果。

---

### 任务 1.5 — 给 AI 一只手（2 小时）

要让 AI 调用你的函数，你需要理解三个东西：

```
1. Tool 定义 — 你告诉 AI "我有一个函数，叫 get_weather，参数是 city"
2. Tool Call — AI 回复 "我要调用 get_weather，city=北京"
3. Tool Result — 你执行完，把结果塞回 messages
```

**阅读**：API 文档里的 Tool Use / Function Calling 部分。只看一个完整的示例代码。

**动手**：实现一个工具 `get_current_time()`，让 AI 能回答"现在几点"。

<details>
<summary>技术要点（卡住了再看）：</summary>

```
步骤 1：定义工具
告诉 AI："我有个叫 get_current_time 的函数，不需要参数，返回当前日期时间"

步骤 2：AI 回复时判断
if (response.stop_reason === 'tool_use') {
  // AI 想调工具了，不是普通回复
  // 从 response.content 里找到 tool_use 类型的 block
  // 提取出函数名和参数
}

步骤 3：执行函数
const result = get_current_time();

步骤 4：把结果塞回去
把 tool_use 和 tool_result 都 push 到 messages 里
再调一次 API
这次 AI 就能拿到时间，然后回复用户
```
</details>

**验收标准**：
```
你：现在几点？
AI：[调用了 get_current_time] → 回复：现在是 2026 年 7 月 15 日 下午 3:42

你：今天星期几？
AI：今天是星期三。 ← 能基于工具结果继续回答
```

> **到这里，阶段一结束。** 你已经走通了 LLM → 流式 → 多轮 → 工具调用的全链路。休息一下再继续。

---

## 阶段二：搭一个有 UI 的应用（Week 2-3）

### 选一条路

| 你的情况 | 选这个 | 原因 |
|----------|--------|------|
| 会 React / Next.js | **Next.js + Vercel AI SDK** | 最成熟的 AI 前端方案 |
| 会 Vue | **Nuxt + 自行处理** | 社区方案少，但能搞定 |
| 只会 Python | **Gradio** | 5 行代码出界面，专注后端的首选 |
| 想做 Obsidian 插件 | **Obsidian Plugin 模板** | 你学了 Claudian，可以直接上手 |

下面的任务以 **Next.js + Vercel AI SDK** 为例（当前最主流）。如果你选了其他路线，核心逻辑一样，界面框架不同。

---

### 任务 2.1 — 搭脚手架（1 小时）

```bash
npx create-next-app@latest ai-chat --typescript --tailwind --app
cd ai-chat
npm install ai @ai-sdk/anthropic
```

**资料**：打开 https://sdk.vercel.ai/docs/introduction ，花 15 分钟扫一眼 Getting Started。

---

### 任务 2.2 — 实现第一个 AI 对话页面（2 小时）

**目标**：一个输入框 + 一段 AI 回复。不要会话管理，不要样式，能跑就行。

<details>
<summary>核心代码骨架（自己写了再对照）：</summary>

```typescript
// app/api/chat/route.ts
import { anthropic } from '@ai-sdk/anthropic';
import { streamText } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: anthropic('claude-haiku-4-5-20251001'),
    system: '你是一个友好的助手。',
    messages,
  });

  return result.toDataStreamResponse();
}
```

```typescript
// app/page.tsx
'use client';
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();

  return (
    <div className="max-w-2xl mx-auto p-4">
      {messages.map((m) => (
        <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
          <div className={`inline-block p-2 rounded ${m.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-100'}`}>
            {m.content}
          </div>
        </div>
      ))}
      <form onSubmit={handleSubmit} className="mt-4">
        <input value={input} onChange={handleInputChange} placeholder="输入消息..." />
      </form>
    </div>
  );
}
```
</details>

**验收标准**：浏览器里打开 `localhost:3000`，输入消息，AI 逐字回复。

---

### 任务 2.3 — 加上会话管理（3 小时）

**目标**：侧边栏有对话列表。能新建、切换、删除对话。

这是一个纯前端工程任务，和 AI 无关。如果你是后端程序员，这可能是整个路线图里最"磨人"的一步——**耐心扛过去**。

**数据模型**（最简单的设计）：

```typescript
type Conversation = {
  id: string;
  title: string;         // "新对话" → AI 帮你自动生成标题
  messages: Message[];   // 就是之前那个 messages 数组
  createdAt: number;
  updatedAt: number;
};
```

**存储**：先用 `localStorage` 就行。后面再换数据库。

**拆分小任务**：
```
□ 左侧加一个对话列表 sidebar
□ "新建对话" 按钮 → 清空当前 messages
□ 点击列表中的对话 → 切换到该对话
□ 右键 / 长按 → 删除对话
□ 第一条消息发送后，自动生成标题

每完成一个 □，就提交一次 git
```

---

### 任务 2.4 — 打磨体验（2 小时）

```
□ AI 回复时，显示闪烁光标（表示"还在想"）
□ 加一个"停止生成"按钮（streaming 时出现，完成后消失）
□ 加一个"重新生成"按钮（放在 AI 最后一条回复下面）
□ Markdown 渲染：把 **粗体** - 列表 ```代码块``` 正确渲染
  → 推荐 react-markdown + remark-gfm
□ API 错误时显示提示而不是白屏（try-catch + toast）
```

---

### 阶段二产出物

```
一个 http://localhost:3000 上的 AI 聊天应用：
  ✅ 流式对话
  ✅ 多会话（新建/切换/删除）
  ✅ Markdown 渲染
  ✅ 停止生成 / 重新生成
  ✅ 基本的错误提示
```

---

## 阶段三：让 AI 动手（Week 4-6）

### 核心原理：理解 Agent Loop

Agent 和普通聊天的核心区别：

```
普通聊天：  用户说 → AI 答 → 结束
Agent：    用户说 → AI 想 → AI 调工具 → 拿到结果 → AI 想 → AI 调工具 → …… → AI 答 → 结束
```

你要实现的循环就是这样：

```typescript
while (true) {
  const response = await api.messages.create({ messages, tools });

  const toolUses = response.content.filter(c => c.type === 'tool_use');

  if (toolUses.length === 0) {
    // AI 不再需要工具了，输出最终答案
    print(response.text);
    break;
  }

  // AI 想调工具，挨个执行
  for (const toolCall of toolUses) {
    const result = executeTool(toolCall.name, toolCall.input);
    messages.push({ role: 'user', content: [{ type: 'tool_result', tool_use_id: toolCall.id, content: result }] });
  }
}
```

---

### 任务 3.1 — 给阶段一的项目加 3 个文件工具（1.5 小时）

先把阶段一的命令行程序打开，加这三个工具：

```
Tool 1: read_file(path: string)
  → 返回文件内容（只读项目目录内的）

Tool 2: write_file(path: string, content: string)
  → 写文件（加上：文件已存在要确认）

Tool 3: list_files(directory: string)
  → 返回目录下的文件列表
```

**关键学习点**：工具描述怎么写？

```typescript
// 差的描述 ❌
{ name: 'read_file', description: 'Read a file' }

// 好的描述 ✅
{
  name: 'read_file',
  description: '读取项目目录中的文件内容。用这个工具来查看代码、配置、或文档。' +
               '注意：只能读取本项目目录内的文件，不能读取系统文件。',
  input_schema: {
    type: 'object',
    properties: {
      path: { type: 'string', description: '文件路径，相对于项目根目录，例如 "src/main.ts"' }
    },
    required: ['path']
  }
}
```

**为什么工具描述这么重要？** AI 是靠读你的描述来决定调用哪个工具的。描述模糊 → 该调的时候不调。描述太宽 → 不该调的时候瞎调。

---

### 任务 3.2 — 实现 Agent Loop（2 小时）

把你阶段一的对话程序改成 Agent：

```
改造前（普通对话）：
  messages 发过去 → 拿 reply → 打印 → 结束

改造后（Agent）：
  messages 发过去 → 拿 reply → reply 里有 tool_use？
    ├── 没有 → 打印回复 → 结束
    └── 有 → 执行工具 → 把结果 push 进 messages → 回到开头再发
```

**调试技巧**：每一步都 `console.log` 出来。

```
console.log('→ 发送 messages，共', messages.length, '条');
console.log('← AI 回复，stop_reason =', response.stop_reason);
if (tool_use) {
  console.log('🔧 调用工具:', tool_use.name, tool_use.input);
  console.log('🔧 工具返回:', result);
}
```

---

### 任务 3.3 — 加上安全确认（1 小时）

```
风险分级：

🟢 低风险（直接执行）：
  - read_file
  - list_files

🟡 中风险（首次确认）：
  - write_file（文件不存在时）
  - search_files

🔴 高风险（每次都确认）：
  - write_file（覆盖已有文件）
  - execute_command
  - delete_file
```

实现：工具执行前，判断风险等级 → `🔴` 的弹窗让用户确认（本阶段用终端输入 `y/n` 就行）。

---

### 任务 3.4 — 做一个"真有用"的项目（2 天）

到了这里，你有能力做一个真正有用的小工具了。选一个方向：

**方向 A：代码助手**
```
"帮我在 src/ 下找到所有没有 try-catch 的 async 函数，列出来"
"帮我把这个文件里的 console.log 全部删掉"
"给我写一个接收 email 参数、返回 boolean 的校验函数"
```

**方向 B：文档助手**
```
"帮我把 README.md 里的英文部分翻译成中文"
"帮我生成一个 CHANGELOG.md，总结最近的 git commit"
"帮我看一下这 3 个 markdown 文件，找出互相矛盾的地方"
```

**方向 C：自动化脚本**
```
"帮我在这个项目里跑 npm install 然后 npm test，如果测试失败帮我分析原因"
"帮我把这个 CSV 文件转成 JSON，并去重"
```

**验收标准**：你完成其中一个方向的完整项目。代码推上 GitHub，README 写清楚怎么用。

---

## 阶段四：RAG — 让 AI 读你的文档（Week 7-8）

### 先理解概念（30 分钟读完这篇）

**读这篇文章**：https://docs.anthropic.com/en/docs/build-with-claude/embeddings

只看这一篇就够了。理解三个概念：
1. Embedding = 把一段文字变成一个数字数组（向量）
2. 语义相近的文字，向量也很接近
3. 向量搜索 = 找"意思最接近"的内容，而不是找"关键词匹配"

---

### 任务 4.1 — 感受 Embedding（45 分钟）

```typescript
// 安装：npm install @anthropic-ai/sdk
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic();

// 把一段文字变成向量
const result = await client.embeddings.create({
  model: 'claude-3-haiku-20240307-embedding',  // 这个是最便宜的
  input: '今天天气真不错，适合出去玩。',
  encoding_format: 'float',
});

console.log(result.embeddings[0].embedding);
// → [0.023, -0.451, 0.891, ...]   // 一个 1024 维的数组
```

**动手实验**：

```typescript
// 准备 10 句话
const sentences = [
  '如何煮米饭',
  '烹饪教程：白米饭的做法',
  'Python 编程入门',
  '学习 Python 的第一课',
  '今天的天气怎么样',
  // ... 加 5 句你自己想的
];

// 1. 给每句话算一个 Embedding
// 2. 用户输入："怎么做饭"
// 3. 把用户输入的 Embedding 和 10 句话的 Embedding 做比较
// 4. 找出最相似的 3 句

// 余弦相似度：
function cosineSimilarity(a: number[], b: number[]): number {
  const dot = a.reduce((sum, val, i) => sum + val * b[i], 0);
  const magA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
  const magB = Math.sqrt(b.reduce((sum, val) => sum + val * b[i], 0));
  return dot / (magA * magB);
}
```

**验收标准**：输入"怎么做饭"，最相似的前两句是"如何煮米饭"和"烹饪教程"，而不是"Python 编程"。

---

### 任务 4.2 — 做一个最小 RAG（3 小时）

**步骤拆解**：

```
步骤 1：准备文档（30 分钟）
  → 把你项目里的 README.md 切成一段一段
  → 最简单的切法：每 5-10 行切一段

步骤 2：建索引（1 小时）
  → 每段都算 Embedding → 存到一个 JSON 文件里
  → 格式：{ chunks: [{ text: "...", embedding: [...] }] }

步骤 3：检索（30 分钟）
  → 用户提问 → 算 Embedding → 找到最相似的 3 段

步骤 4：生成回答（1 小时）
  → 把 3 段原文 + 用户问题拼成 Prompt：
    "请基于以下资料回答问题。如果资料中没有相关信息，请诚实说明。
     资料 1：{chunk1}
     资料 2：{chunk2}
     资料 3：{chunk3}
     问题：{question}"
  → 发给 AI → 得到回答
```

**验收标准**：
```
文档内容包含：项目的安装方法、使用方法、配置说明

你：怎么安装？
AI：运行 npm install，然后 npm run build。需要 Node.js >= 24。
   （这些信息来自 README.md 里的安装部分）

你：作者是谁？
AI：文档中没有提到作者信息。  ← 诚实说不知道
```

---

### 任务 4.3 — 优化分块策略（1 小时）

试试不同的切法，比较效果：

```
方式 A：按固定行数切（5 行一段）
方式 B：按段落切（两个空行之间为一段）
方式 C：按固定 Token 数切（每段 500 Token）

每种切法都试一遍，看看哪个检索效果最好。
没有标准答案——不同的文档类型适合不同的切法。
```

---

## 阶段五：从现在开始，持续做的事

以下不再有"任务编号"。这些都是你可以随时开始的习惯。

### 每天 10 分钟：读一个好 Prompt

| 看什么 | 链接 |
|--------|------|
| Claude Code 的 System Prompt | 在 Claudian 源码 `src/providers/claude/prompt/mainAgent.ts` 里 |
| Anthropic 官方 Prompt 指南 | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts |
| Cursor 的 Prompt（社区分析版） | Google 搜 "Cursor system prompt analysis" |

每次看的时候想：**这个 Prompt 在约束什么行为？为什么这样写？如果去掉某一段会怎样？**

### 每周 2 小时：解剖一个开源项目

| 项目 | 学什么 | 怎么看 |
|------|--------|--------|
| **Claudian** | 多 Provider 架构、Agent 循环 | 从 `src/main.ts` 入口，跟一次完整请求 |
| **Continue.dev** | IDE 中集成 AI 的交互模式 | 看 `core/llm/` 目录，看他们怎么抽象不同 LLM |
| **Aider** | Agent 的地图编辑模式（只改变化的部分） | 看 `codelsp/` 目录的地图格式 |

**怎么看开源项目**（关键方法）：
```
1. 先读 README 和架构文档
2. 找到入口文件
3. 找一个你感兴趣的功能（比如"Inline Edit"）
4. 用 grep 搜关键字，定位到具体代码
5. 顺着函数调用链往下读 3-5 层
6. 画个流程图
7. 试着改一行代码，看效果
```

### 每两周 1 次：做一个小练习

| 练习 | 难度 | 预计时间 |
|------|:----:|:--------:|
| 给聊天应用加上"对话导出为 Markdown" | ★☆☆☆☆ | 2h |
| 实现 Prompt 模板功能（`/` 命令展开为预设 Prompt） | ★★☆☆☆ | 3h |
| 加入 Token 计数显示（每次回复用了多少 Token） | ★★☆☆☆ | 2h |
| 支持图片输入（多模态：上传图片 + 提问） | ★★★☆☆ | 4h |
| 实现对话分支（Fork：从某轮开始分叉出新的对话） | ★★★★☆ | 6h |
| 接入 MCP 协议（让应用通过 MCP 连接外部工具） | ★★★★★ | 8h |

---

## 加速器：困惑时怎么自救

### 优先级顺序

```
1. 看官方文档最准（不要先搜 CSDN / 知乎）
2. GitHub 搜一个最简示例（搜 "anthropic tool use example"）
3. 把你的代码和报错贴在 Claude / ChatGPT 里问它
4. 在代码里加 console.log，看每一步的实际输出
5. 睡一觉 → 第二天早上再想
```

### 最省时间的"不问问题"策略

当你卡在某个 bug 上超过 30 分钟：

1. 把你的代码**精简到最小**（删掉所有和 bug 无关的）
2. 把你的报错信息**完整复制**
3. 把这两样贴在 AI 对话里，说"这段代码报这个错，帮我看看"
4. **不要**只描述症状，**一定要贴代码和报错**

---

## 整条路线的时间预算

```
                   最少      宽裕
阶段一（API 基础）   1 周    2 周
阶段二（聊天应用）   2 周    3 周
阶段三（Agent）      2 周    4 周
阶段四（RAG）        1 周    2 周
阶段五（持续学习）   一直     一直
────────────────────────────────
           总计：   6 周    11 周
```

---

## 四个"立刻开始"清单

打印出来贴在显示器旁边：

```
□ 今天：注册 Anthropic / OpenAI API 账号，充 $10
□ 明天：跑通第一行 API 调用代码，看到 AI 回复
□ 本周：做好一个命令行对话程序（流式 + 多轮 + 一个工具）
□ 本月：部署一个带 UI 的聊天应用到网上，把链接发给朋友
```

---

*遇到困难是正常的。AI 输出的不确定性和传统编程完全不同——*
*你需要的不是天赋，是耐心调试 + 看官方文档的习惯。*
