import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def calculator(a,b):
    return a*b

def add(a,b):
    return a+b

def get_current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def read_file(file_path):
    with open(file_path,"r",encoding="utf-8") as file:
        content = file.read()

    return content


tool_functions = {
    "calculator":calculator,
    "add":add,
    "get_current_time":get_current_time,
    "read_file":read_file
}

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
    },

    {
        "type":"function",
        "function":{
            "name":"add",
            "description":"计算两个数字的和",
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
    },

    {
        "type":"function",
        "function":{
            "name":"get_current_time",
            "description":"获取当前本地日期和时间",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    },

    {
        "type":"function",
        "function":{
            "name":"read_file",
            "description":"读取指定路径的文本文件内容",
            "parameters":{
                "type":"object",
                "properties":{
                    "file_path":{
                        "type":"string",
                        "description":"要读取的文件路径"
                    }
                },
                "required":["file_path"]
            }
        }
    }
]

messages = []

max_steps = 5

while True:
    user_input=input("你：")

    if user_input == "退出":
        print("AI:再见！")
        break

    messages.append({
        "role":"user",
        "content":user_input
    })

    for step in range(max_steps):
        response = client.chat.completions.create(
                model="deepseek-flash",
                messages=messages,
                tools=tools
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print("AI:",message.content)
            break

        messages.append(message)

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name

            try:
                arguments = json.loads(tool_call.function.arguments)

                if function_name not in tool_functions:
                    raise ValueError(f"不存在这个工具:{function_name}")
                
                function = tool_functions[function_name]

                result = function(**arguments)

                print(
                    f"调用工具:{function_name},"
                    f"参数:{arguments},"
                    f"结果:{result}"
                )

            except Exception as e:
                result = f"工具执行失败:{str(e)}"

                print(result)
            
            messages.append({
                "role":"tool",
                "tool_call_id":tool_call.id,
                "content":str(result)
            })

    else:
        print("Agent 达到最大执行步数,已停止")

    '''
    tool_call = message.tool_calls[0]

    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    print("模型想调用的函数：", function_name)
    print("模型给出的参数:", arguments)

    """
    if function_name == "calculator":
        result = calculator(
            arguments["a"],
            arguments["b"]
        )
    """
    function = tool_functions[function_name]

    result = function(**arguments)

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
    '''

    # print ("工具执行结果:", result)

    # answer = response.choices[0].message.content

    # print("AI:" + answer)

    # messages.append({
    #     "role":"assistant",
    #     "content":answer
    # })