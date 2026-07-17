import os
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime
from pprint import pprint
import json

def send_messages(messages):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response

def get_current_time():
      """返回当前日期和时间"""
      now = datetime.now()
      return now.strftime("%Y年%m月%d日 %H:%M:%S")

def get_current_weather(city: str) -> str:
      """返回指定城市的模拟天气信息"""
      # 模拟数据，不用真实 API
      weather_data = {
          "北京": "晴，25°C，湿度 40%",
          "上海": "多云，28°C，湿度 65%",
          "深圳": "阵雨，30°C，湿度 80%",
          "杭州": "阴，22°C，湿度 55%",
      }
      return weather_data.get(city, f"{city}：晴转多云，20°C，湿度 50%")

load_dotenv()

client = OpenAI(
      api_key=os.environ["DEEPSEEK_API_KEY"],
      base_url="https://api.deepseek.com",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a given city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The name of the city."
                    }
                },
                "required": ["city"],
            },
        }
    }
]

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

    response = send_messages(messages)
    # pprint(response.choices[0].model_dump(), indent=2, width=120)
    msg = response.choices[0].message
    # 有工具的情况
    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        messages.append(msg.model_dump(exclude_none=True))
        if tool_call :
            if tool_call.function.name == "get_current_time":
                current_time = get_current_time()
                # print(f"工具调用结果：当前时间是 {current_time}") 
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": current_time})
                response = send_messages(messages)   
            if  tool_call.function.name == "get_current_weather":
                args = json.loads(tool_call.function.arguments)
                city = args.get("city")
                weather_info = get_current_weather(city)
                # print(f"工具调用结果：{weather_info}") 
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": weather_info})
                response = send_messages(messages) 
            msg = response.choices[0].message   
    messages.append(msg.model_dump(exclude_none=True))
    print(f"AI：{msg.content}")
    print()
    print(messages)
    
    

