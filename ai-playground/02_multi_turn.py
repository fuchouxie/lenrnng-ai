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
    )

    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})

    print(f"AI：{reply}")
    print()