from openai import OpenAI
from dotenv import dotenv_values
import json

key_value = dotenv_values(".env")

client = OpenAI(
    base_url="https://api.deepseek.com",
    api_key=key_value["API_KEY"],
)

tools = [{
    "type":"function",
    "function": {
        "name": "get_current_weather",
        "description": "获取当前城市的天气情况",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city to get the weather for"},
                "country": {"type": "string", "description": "The country to get the weather for"}
            },
            "required": ["city", "country"]
        }
    }
},
]

messages = [
    {"role": "user", "content": "北京现在的天气如何？"}
]

# 这一步是调用模型，并返回工具调用信息
# response是模型针对messages的回复，其中包含了工具调用信息
# 后续将这个回复加入到新的messages中，并再次调用模型，直到模型不再返回工具调用信息
# 此时，模型返回的content就是最终的回答
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

# 打印内容：工具调用信息
# 这里的tool_calls是一个列表，列表中每个元素是一个字典，字典中包含工具名称和工具参数
# 例如：
# [{'name': 'get_current_weather', 'arguments': '{"city": "北京", "country": "中国"}'}]
print(response.choices[0].message.tool_calls)

def get_current_weather(city: str, country: str):
    return f"The weather in {city}, {country} is sunny."

tool_call = response.choices[0].message.tool_calls[0]
tool_name = tool_call.function.name
tool_args = json.loads(tool_call.function.arguments)

print(tool_name, )
print(tool_args)

print(tool_call.id)

function_call_result=get_current_weather(tool_args["location"], tool_args["country"])
print(function_call_result)

mesages = messages.append(response.choices[0].message)

messages.append({
    "role": "tool",
    "content": function_call_result,
    "tool_call_id": tool_call.id
})

res = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages,
)

print(res)
print(res.choices[0].message.content)


