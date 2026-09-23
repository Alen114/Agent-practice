import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def calculator(a,b):
    return a*b

tools = [
    {
        "type":"function",
        "function":{
            "name":"calculator",
            "description":"计算两个数字的乘积",
            "parameters":{
                "type":"object",
                "properties":{
                    "a":{
                        "type":"number",
                        "description":"第一个数字"
                    },
                    "b":{
                        "type":"number",
                        "description":"第二个数字"
                    }
                },
                "required":["a","b"]
            }
        }
    }
]

messages = []

while True:
    user_input=input("你：")

    if user_input == "退出":
        print("AI:再见！")
        break

    messages.append({
        "role":"user",
        "content":user_input
    })

    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message

    tool_call = message.tool_calls[0]

    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print("模型想调用的函数：", function_name)
    print("模型给出的参数:", arguments)

    if function_name == "calculator":
        result = calculator(
            arguments["a"],
            arguments["b"]
        )

        messages.append(message)

        messages.append({
            "role":"tool",
            "tool_call_id":tool_call.id,
            "content":str(result)
        })

        final_response = client.chat.completions.create(
            model="deepseek-flash",
            messages=messages
        )

        final_answer = final_response.choices[0].message.content

        print("AI:",final_answer)

    # print ("工具执行结果:", result)

    # answer = response.choices[0].message.content

    # print("AI:" + answer)

    # messages.append({
    #     "role":"assistant",
    #     "content":answer
    # })