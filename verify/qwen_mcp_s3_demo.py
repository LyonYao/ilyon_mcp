import requests
import os

# 配置千问大模型API
QWEN_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
QWEN_API_KEY = os.environ.get("QWEN_API_KEY")  # 从环境变量读取API Key

# 配置MCP服务API
MCP_API_URL = "http://localhost:8000/mcp"  # 假设MCP服务已本地启动

def ask_qwen_for_mcp_params(user_input, mcp_missing=None):
    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }
    if mcp_missing:
        prompt = f"你是MCP协议助手。用户想要：{user_input}。MCP服务反馈缺少参数：{mcp_missing}。请根据上下文和常识补全所有参数，返回JSON格式（包含intent和parameters）。如果无法补全，parameters中缺失项请留空。"
    else:
        prompt = f"你是MCP协议助手。请根据用户的意图，提取出MCP协议调用AWS S3 bucket所需的参数（如bucket_name、region等），并以JSON格式返回。用户输入：{user_input}"
    payload = {
        "model": "qwen-turbo",
        "input": prompt
    }
    response = requests.post(QWEN_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result.get('output', '')
    else:
        print(f"千问API请求失败: {response.status_code}")
        print(response.text)
        return None

def call_mcp_api(mcp_input, context, parameters):
    payload = {
        "input": mcp_input,
        "context": context,
        "parameters": parameters
    }
    response = requests.post(MCP_API_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"MCP请求失败: {response.status_code}")
        print(response.text)
        return None

def main():
    import json
    user_input = input("请输入操作描述（如：创建名为test-bucket的S3存储桶，或删除test-bucket）：\n")
    retry = 0
    mcp_missing = None
    while retry < 2:
        qwen_result = ask_qwen_for_mcp_params(user_input, mcp_missing)
        if not qwen_result:
            print("未能从大模型获取参数。")
            return
        try:
            mcp_info = json.loads(qwen_result)
            mcp_input = mcp_info.get('intent', user_input)
            parameters = mcp_info.get('parameters', {})
            context = {"cloud": "aws"}
            mcp_resp = call_mcp_api(mcp_input, context, parameters)
            if mcp_resp and mcp_resp.get("status") == "error" and "缺少" in str(mcp_resp.get("error")):
                mcp_missing = mcp_resp.get("error")
                print(f"MCP提示缺少参数，尝试让大模型补全: {mcp_missing}")
                retry += 1
                continue
            print("MCP服务返回：")
            print(mcp_resp)
            return
        except Exception as e:
            print(f"解析大模型返回时出错: {e}")
            print("原始返回：", qwen_result)
            return
    print("参数仍不完整，请补充输入：")
    print(mcp_missing)

if __name__ == "__main__":
    main()
