import os
import json
from dashscope import Generation  # 千问官方SDK

MCP_BASE_URL = "http://localhost:8000"
MCP_API_URL = f"{MCP_BASE_URL}/mcp"
MCP_CAP_URL = f"{MCP_BASE_URL}/capabilities"

import requests

def discover_mcp_capabilities():
    print("[LOG] 正在发现MCP服务能力...")
    resp = requests.get(MCP_CAP_URL)
    if resp.status_code == 200:
        print("[LOG] MCP功能列表:")
        print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        return resp.json()
    else:
        print(f"[ERROR] 获取MCP功能列表失败: {resp.status_code}")
        print(resp.text)
        return None

def ask_qwen_for_mcp_params(user_input, mcp_capabilities, mcp_missing=None):
    if mcp_missing:
        prompt = f"你是MCP协议助手。MCP服务能力如下：{mcp_capabilities}。用户想要：{user_input}。MCP服务反馈缺少参数：{mcp_missing}。请根据能力和上下文补全所有参数，返回JSON格式（包含intent和parameters）。如果无法补全，parameters中缺失项请留空。"
    else:
        prompt = f"你是MCP协议助手。MCP服务能力如下：{mcp_capabilities}。请根据用户的意图，提取出MCP协议调用所需的intent和parameters，返回JSON格式。用户输入：{user_input}"
    print(f"[LOG] 向千问AI提问: {prompt}")
    api_key = os.environ.get("QWEN_API_KEY")
    response = Generation.call(
        model="qwen-turbo",
        prompt=prompt,
        api_key=api_key
    )
    # 修正：提取text字段并去除markdown包裹
    ai_text = None
    if response and hasattr(response, 'output'):
        print("[LOG] 千问AI返回:")
        print(response)
        ai_text = response.output["text"] if isinstance(response.output, dict) and "text" in response.output else response.output
    elif isinstance(response, dict) and 'output' in response:
        print("[LOG] 千问AI返回:")
        print(response)
        ai_text = response['output']
        if isinstance(ai_text, dict) and "text" in ai_text:
            ai_text = ai_text["text"]
    if isinstance(ai_text, str) and ai_text.strip().startswith("```json"):
        ai_text = ai_text.strip().lstrip("```json").rstrip("``` ").strip()
    if ai_text:
        return ai_text
    print("[ERROR] 千问API请求失败:")
    print(response)
    return None

def call_mcp_api(mcp_input, context, parameters):
    # 强制将 input 转为字符串，避免422错误
    if not isinstance(mcp_input, str):
        mcp_input = json.dumps(mcp_input, ensure_ascii=False)
    payload = {
        "input": mcp_input,
        "context": context,
        "parameters": parameters
    }
    print(f"[LOG] 调用MCP: {payload}")
    resp = requests.post(MCP_API_URL, json=payload)
    if resp.status_code == 200:
        print("[LOG] MCP服务返回:")
        print(resp.json())
        return resp.json()
    else:
        print(f"[ERROR] MCP请求失败: {resp.status_code}")
        print(resp.text)
        return None

def main():
    mcp_capabilities = discover_mcp_capabilities()
    if not mcp_capabilities:
        print("无法获取MCP能力，退出。")
        return
    while True:
        user_input = input("请输入操作描述（如：创建名为test-bucket的S3存储桶，或删除test-bucket，输入exit退出）：\n")
        if user_input.strip().lower() == "exit":
            print("退出。"); break
        retry = 0
        mcp_missing = None
        while retry < 2:
            qwen_result = ask_qwen_for_mcp_params(user_input, mcp_capabilities, mcp_missing)
            if not qwen_result:
                print("未能从大模型获取参数。")
                break
            try:
                mcp_info = json.loads(qwen_result)
                mcp_input = mcp_info.get('intent', user_input)
                # 修正：确保mcp_input为字符串类型
                if not isinstance(mcp_input, str):
                    mcp_input = json.dumps(mcp_input, ensure_ascii=False)
                parameters = mcp_info.get('parameters', {})
                context = {"cloud": "aws"}
                mcp_resp = call_mcp_api(mcp_input, context, parameters)
                if mcp_resp and mcp_resp.get("status") == "error" and "缺少" in str(mcp_resp.get("error")):
                    mcp_missing = mcp_resp.get("error")
                    print(f"[LOG] MCP提示缺少参数，尝试让大模型补全: {mcp_missing}")
                    retry += 1
                    continue
                break
            except Exception as e:
                print(f"[ERROR] 解析大模型返回时出错: {e}")
                print("原始返回：", qwen_result)
                break
        else:
            print("参数仍不完整，请补充输入：")
            print(mcp_missing)

if __name__ == "__main__":
    main()
