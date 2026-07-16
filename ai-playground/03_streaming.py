import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
      api_key=os.environ["DEEPSEEK_API_KEY"],
      base_url="https://api.deepseek.com",
)

# messages 就是"记忆"——对话历史全存在这个列表里
messages = [
    {"role": "system", "content": "你是一个友好、简洁的助手。用中文回答。"},
]

print("开始对话（输入 exit 退出）")
print("-" * 40)

while True:
    user_input = input("你：")
    if user_input.lower() == "exit":
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,  # 开启流式输出
    )
    print("AI：", end="", flush=True)
    full_reply = ""

    for chunk in response:
        text = chunk.choices[0].delta.content
        if text:
            print(text, end="", flush=True)
            full_reply += text

    print()
    messages.append({"role": "assistant", "content": full_reply})
    print()