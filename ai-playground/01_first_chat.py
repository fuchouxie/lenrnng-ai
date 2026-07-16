import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个友好、简洁的助手。"},
        {"role": "user", "content": "你好！用一句话介绍一下自己。"},
    ],
    stream=False,
)

print(response.choices[0].message.content)